from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class ProductType(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, min_length=1)

    products: List["Product"] = Relationship(back_populates="type")


class Product(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(ge=1)
    title: str = Field(min_length=1)
    price_eur: float = Field(ge=0.0)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    type_id: int = Field(foreign_key="producttype.id")

    type: Optional[ProductType] = Relationship(back_populates="products")
