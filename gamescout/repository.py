from typing import Any, Dict, List, Optional, cast
from sqlalchemy.engine import Engine
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, select
from gamescout.database import get_engine
from gamescout.models import Product, ProductType


class ProductRepository:

    def __init__(self) -> None:
        self.engine: Engine = get_engine()

    def get_or_create_type(
        self, name: str, session: Optional[Session] = None
    ) -> ProductType:
        clean_name: str = name.split("\n")[0].strip()

        if session is not None:
            return self._get_or_create_type_with_session(clean_name, session)

        with Session(self.engine) as new_session:
            product_type = self._get_or_create_type_with_session(clean_name, new_session)
            new_session.commit()
            new_session.refresh(product_type)
            return product_type

    def _get_or_create_type_with_session(
        self, name: str, session: Session
    ) -> ProductType:
        statement = select(ProductType).where(ProductType.name == name)
        product_type: Optional[ProductType] = session.exec(statement).first()

        if not product_type:
            product_type = ProductType(name=name)
            session.add(product_type)
            session.flush()

        return product_type

    def upsert_products(self, products_data: List[Dict[str, Any]]) -> None:
        with Session(self.engine) as session:
            for item in products_data:
                p_type: ProductType = self.get_or_create_type(
                    item["type_name"], session=session
                )

                assert p_type.id is not None

                statement = select(Product).where(
                    Product.product_id == item["product_id"]
                )
                existing_product: Optional[Product] = session.exec(statement).first()

                if existing_product:
                    existing_product.title = item["title"]
                    existing_product.price_eur = item["price_eur"]
                    existing_product.type_id = p_type.id
                    session.add(existing_product)
                else:
                    new_product = Product(
                        product_id=item["product_id"],
                        title=item["title"],
                        price_eur=item["price_eur"],
                        type_id=p_type.id,
                    )
                    session.add(new_product)

            session.commit()

    def get_top_n(self, n: int) -> List[Product]:
        with Session(self.engine) as session:
            statement = (
                select(Product)
                .options(joinedload(cast(Any, Product.type)))
                .order_by(col(Product.price_eur).desc())
                .limit(n)
            )
            results = session.exec(statement).all()
            return [product for product in results]

    def get_products_by_type(self, type_name: str) -> List[Product]:
        with Session(self.engine) as session:
            statement = (
                select(Product)
                .join(ProductType)
                .where(ProductType.name == type_name)
            )
            results = session.exec(statement).all()
            return [product for product in results]