import pytest

from models import Customer, OrderItem, Order


def test_customer_creation():
    customer = Customer(name="Иван", phone="+79990000000", address="Москва")

    assert customer.name == "Иван"
    assert customer.phone == "+79990000000"
    assert customer.address == "Москва"


def test_empty_customer_name_error():
    with pytest.raises(ValueError):
        Customer(name="")


def test_order_item_subtotal():
    item = OrderItem(product_name="Пицца", quantity=2, price=750)

    assert item.subtotal == 1500


def test_order_total_calculation():
    items = [
        OrderItem(product_name="Пицца", quantity=2, price=750),
        OrderItem(product_name="Сок", quantity=1, price=200),
    ]

    order = Order(
        customer_id=1,
        order_date="2025-04-20",
        status="новый",
        items=items,
    )

    assert order.total == 1700


def test_invalid_order_status():
    items = [
        OrderItem(product_name="Пицца", quantity=1, price=750),
    ]

    with pytest.raises(ValueError):
        Order(
            customer_id=1,
            order_date="2025-04-20",
            status="непонятный статус",
            items=items,
        )