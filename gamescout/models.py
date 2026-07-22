from datetime import datetime
from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


class ProductType(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, min_length=1)

    products: List["Product"] = Relationship(back_populates="type")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("El nombre del tipo no puede estar vacio.")
        return clean_value


class Product(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(ge=1)
    title: str = Field(min_length=1)
    price_eur: float = Field(ge=0.0)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    type_id: int = Field(foreign_key="producttype.id")

    type: Optional[ProductType] = Relationship(back_populates="products")

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("El titulo del producto no puede estar vacio.")
        return clean_value

    @field_validator("price_eur")
    @classmethod
    def validate_price(cls, value: float) -> float:
        if value < 0:
            raise ValueError("El precio no puede ser negativo.")
        return value
