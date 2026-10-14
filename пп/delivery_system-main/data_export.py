import json
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

from logger_config import logger
from models import VALID_STATUSES


class ImportValidationError(ValueError):
    """
    Ошибка проверки данных при импорте.
    """


def export_orders(database, file_path):
    """
    Экспортирует все заказы в JSON или XML.
    Формат определяется по расширению файла.
    """

    path = Path(file_path)
    orders = database.get_orders()

    if path.suffix.lower() == ".json":
        _export_json(orders, path)

    elif path.suffix.lower() == ".xml":
        _export_xml(orders, path)

    else:
        raise ValueError("Поддерживаются только файлы .json и .xml")

    logger.info(f"Экспорт выполнен: {path}")
    return path


def _export_json(orders, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(orders, file, ensure_ascii=False, indent=2)


def _export_xml(orders, path):
    root = ET.Element("orders")

    for order in orders:
        order_element = ET.SubElement(root, "order")

        for key in ["id", "customer_id", "customer_name", "order_date", "status", "total"]:
            child = ET.SubElement(order_element, key)
            child.text = str(order.get(key, ""))

        items_element = ET.SubElement(order_element, "items")

        for item in order.get("items", []):
            item_element = ET.SubElement(items_element, "item")

            for key in ["product_name", "quantity", "price"]:
                child = ET.SubElement(item_element, key)
                child.text = str(item.get(key, ""))

    rough_xml = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(rough_xml).toprettyxml(indent="  ", encoding="utf-8")

    with open(path, "wb") as file:
        file.write(pretty_xml)


def import_orders(database, file_path):
    """
    Импортирует заказы из JSON или XML.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    if path.suffix.lower() == ".json":
        orders = _read_json(path)

    elif path.suffix.lower() == ".xml":
        orders = _read_xml(path)

    else:
        raise ValueError("Поддерживаются только файлы .json и .xml")

    imported_count = 0

    for order_data in orders:
        cleaned_order = _validate_order_data(database, order_data)

        database.add_order(
            customer_id=cleaned_order["customer_id"],
            order_date=cleaned_order["order_date"],
            status=cleaned_order["status"],
            items=cleaned_order["items"],
        )

        imported_count += 1

    logger.info(f"Импорт выполнен: {path}, импортировано заказов: {imported_count}")
    return imported_count


def _read_json(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ImportValidationError("JSON-файл должен содержать список заказов")

    return data


def _read_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    if root.tag != "orders":
        raise ImportValidationError("Корневой элемент XML должен называться orders")

    orders = []

    for order_element in root.findall("order"):
        order = {
            "customer_id": _get_text(order_element, "customer_id"),
            "order_date": _get_text(order_element, "order_date"),
            "status": _get_text(order_element, "status"),
            "items": [],
        }

        items_element = order_element.find("items")

        if items_element is not None:
            for item_element in items_element.findall("item"):
                order["items"].append(
                    {
                        "product_name": _get_text(item_element, "product_name"),
                        "quantity": _get_text(item_element, "quantity"),
                        "price": _get_text(item_element, "price"),
                    }
                )

        orders.append(order)

    return orders


def _get_text(element, child_name):
    child = element.find(child_name)

    if child is None or child.text is None:
        return ""

    return child.text


def _validate_order_data(database, order_data):
    required_fields = ["customer_id", "order_date", "status", "items"]

    for field in required_fields:
        if field not in order_data:
            raise ImportValidationError(f"В заказе отсутствует поле: {field}")

    try:
        customer_id = int(order_data["customer_id"])
    except ValueError:
        raise ImportValidationError("customer_id должен быть числом")

    if not database.get_customer(customer_id):
        raise ImportValidationError(f"Клиент с id={customer_id} не найден")

    order_date = str(order_data["order_date"]).strip()

    if not order_date:
        raise ImportValidationError("Дата заказа не может быть пустой")

    status = str(order_data["status"]).strip()

    if status not in VALID_STATUSES:
        raise ImportValidationError(f"Некорректный статус заказа: {status}")

    items = order_data["items"]

    if not isinstance(items, list) or not items:
        raise ImportValidationError("В заказе должен быть список товаров")

    cleaned_items = []

    for item in items:
        if "product_name" not in item:
            raise ImportValidationError("У товара отсутствует product_name")

        if "quantity" not in item:
            raise ImportValidationError("У товара отсутствует quantity")

        if "price" not in item:
            raise ImportValidationError("У товара отсутствует price")

        product_name = str(item["product_name"]).strip()

        if not product_name:
            raise ImportValidationError("Название товара не может быть пустым")

        try:
            quantity = int(item["quantity"])
        except ValueError:
            raise ImportValidationError("quantity должен быть числом")

        try:
            price = float(item["price"])
        except ValueError:
            raise ImportValidationError("price должен быть числом")

        if quantity <= 0:
            raise ImportValidationError("quantity должен быть больше 0")

        if price < 0:
            raise ImportValidationError("price не может быть отрицательным")

        cleaned_items.append(
            {
                "product_name": product_name,
                "quantity": quantity,
                "price": price,
            }
        )

    return {
        "customer_id": customer_id,
        "order_date": order_date,
        "status": status,
        "items": cleaned_items,
    }