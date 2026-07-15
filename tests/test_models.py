from sqlmodel import Session, SQLModel, create_engine
from gamescout.models import Product, ProductType

def test_product_and_type_relationship() -> None:
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        action_type = ProductType(name="Action")
        session.add(action_type)
        session.commit()
        session.refresh(action_type)

        product = Product(
            product_id=1,
            title="Zelda",
            price_eur=59.99,
            type_id=action_type.id,
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        assert product.type is not None
        assert product.type.name == "Action"
        assert len(action_type.products) == 1
        assert action_type.products[0].title == "Zelda"