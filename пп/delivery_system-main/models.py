from dataclasses import dataclass, field
from typing import List, Optional


VALID_STATUSES = ("новый", "в доставке", "выполнен", "отменён")


@dataclass
class Customer:
    """
    Модель клиента.
    """

    name: str
    phone: str = ""
    address: str = ""
    id: Optional[int] = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Имя клиента не может быть пустым")

        self.name = self.name.strip()
        self.phone = self.phone.strip()
        self.address = self.address.strip()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
        }


@dataclass
class OrderItem:
    """
    Модель товара внутри заказа.
    """

    product_name: str
    quantity: int
    price: float
    id: Optional[int] = None
    order_id: Optional[int] = None

    def __post_init__(self):
        if not self.product_name or not str(self.product_name).strip():
            raise ValueError("Название товара не может быть пустым")

        self.product_name = str(self.product_name).strip()
        self.quantity = int(self.quantity)
        self.price = float(self.price)

        if self.quantity <= 0:
            raise ValueError("Количество товара должно быть больше 0")

        if self.price < 0:
            raise ValueError("Цена товара не может быть отрицательной")

    @property
    def subtotal(self):
        return self.quantity * self.price

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": self.price,
            "subtotal": self.subtotal,
        }


@dataclass
class Order:
    """
    Модель заказа.
    """

    customer_id: int
    order_date: str
    status: str
    items: List[OrderItem] = field(default_factory=list)
    id: Optional[int] = None
    total: Optional[float] = None

    def __post_init__(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Некорректный статус заказа. Допустимые статусы: {', '.join(VALID_STATUSES)}"
            )

        if not self.order_date or not self.order_date.strip():
            raise ValueError("Дата заказа не может быть пустой")

        if not self.items:
            raise ValueError("В заказе должен быть хотя бы один товар")

        if self.total is None:
            self.total = self.calculate_total()

    def calculate_total(self):
        return sum(item.subtotal for item in self.items)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "order_date": self.order_date,
            "status": self.status,
            "total": self.total,
            "items": [item.to_dict() for item in self.items],
        }