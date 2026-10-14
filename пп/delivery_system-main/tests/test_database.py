import pytest

from database import Database


def create_test_database(tmp_path):
    return Database(tmp_path / "test_delivery.db")


def test_add_customer(tmp_path):
    database = create_test_database(tmp_path)

    customer_id = database.add_customer(
        name="Иван",
        phone="+79990000000",
        address="Москва",
    )

    customer = database.get_customer(customer_id)

    assert customer is not None
    assert customer["name"] == "Иван"


def test_delete_customer_without_orders(tmp_path):
    database = create_test_database(tmp_path)

    customer_id = database.add_customer("Иван")

    database.delete_customer(customer_id)

    assert database.get_customer(customer_id) is None


def test_cannot_delete_customer_with_orders(tmp_path):
    database = create_test_database(tmp_path)

    customer_id = database.add_customer("Иван")

    database.add_order(
        customer_id=customer_id,
        order_date="2025-04-20",
        status="новый",
        items=[
            {"product_name": "Пицца", "quantity": 2, "price": 750},
        ],
    )

    with pytest.raises(ValueError):
        database.delete_customer(customer_id)


def test_add_order(tmp_path):
    database = create_test_database(tmp_path)

    customer_id = database.add_customer("Иван")

    order_id = database.add_order(
        customer_id=customer_id,
        order_date="2025-04-20",
        status="новый",
        items=[
            {"product_name": "Пицца", "quantity": 2, "price": 750},
            {"product_name": "Сок", "quantity": 1, "price": 200},
        ],
    )

    order = database.get_order(order_id)

    assert order is not None
    assert order["total"] == 1700
    assert len(order["items"]) == 2


def test_report_orders_by_status(tmp_path):
    database = create_test_database(tmp_path)

    customer_id = database.add_customer("Иван")

    database.add_order(
        customer_id=customer_id,
        order_date="2025-04-20",
        status="новый",
        items=[
            {"product_name": "Пицца", "quantity": 1, "price": 750},
        ],
    )

    report = database.orders_count_by_status()

    assert report["новый"] == 1