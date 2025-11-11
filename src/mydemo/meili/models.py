from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    categories: List[str]
    in_stock: bool

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        return cls(**data)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "categories": self.categories,
            "in_stock": self.in_stock,
        }