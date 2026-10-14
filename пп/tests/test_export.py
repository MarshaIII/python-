from database import Database
from data_export import export_orders, import_orders


def create_database_with_order(tmp_path):
    database = Database(tmp_path / "test_delivery.db")

    customer_id = database.add_customer("Иван")

    database.add_order(
        customer_id=customer_id,
        order_date="2025-04-20",
        status="новый",
        items=[
            {"product_name": "Пицца", "quantity": 2, "price": 750},
        ],
    )

    return database


def test_export_json(tmp_path):
    database = create_database_with_order(tmp_path)

    file_path = tmp_path / "orders.json"

    export_orders(database, file_path)

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8")


def test_export_xml(tmp_path):
    database = create_database_with_order(tmp_path)

    file_path = tmp_path / "orders.xml"

    export_orders(database, file_path)

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8")


def test_import_json(tmp_path):
    source_database = create_database_with_order(tmp_path)

    file_path = tmp_path / "orders.json"
    export_orders(source_database, file_path)

    target_database = Database(tmp_path / "target_delivery.db")
    target_database.add_customer("Иван")

    imported_count = import_orders(target_database, file_path)

    assert imported_count == 1
    assert len(target_database.get_orders()) == 1


def test_import_xml(tmp_path):
    source_database = create_database_with_order(tmp_path)

    file_path = tmp_path / "orders.xml"
    export_orders(source_database, file_path)

    target_database = Database(tmp_path / "target_delivery_xml.db")
    target_database.add_customer("Иван")

    imported_count = import_orders(target_database, file_path)

    assert imported_count == 1
    assert len(target_database.get_orders()) == 1