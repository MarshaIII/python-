import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from logger_config import logger
from models import OrderItem, VALID_STATUSES


class Database:
    """
    Класс для работы с SQLite-базой данных.
    """

    def __init__(self, db_path="data/delivery.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.create_tables()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self):
        """
        Создаёт таблицы customers, orders и order_items, если их ещё нет.
        """

        with closing(self._connect()) as connection:
            with connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        address TEXT
                    );

                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER NOT NULL,
                        order_date TEXT NOT NULL,
                        status TEXT NOT NULL CHECK(status IN ('новый', 'в доставке', 'выполнен', 'отменён')),
                        total REAL NOT NULL,
                        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE RESTRICT
                    );

                    CREATE TABLE IF NOT EXISTS order_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER NOT NULL,
                        product_name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
                    );
                    """
                )

        logger.info("Таблицы базы данных проверены/созданы")

    # ---------- Клиенты ----------

    def add_customer(self, name: str, phone: str = "", address: str = "") -> int:
        if not name or not name.strip():
            raise ValueError("Имя клиента не может быть пустым")

        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO customers (name, phone, address)
                    VALUES (?, ?, ?)
                    """,
                    (name.strip(), phone.strip(), address.strip()),
                )

                customer_id = cursor.lastrowid

        logger.info(f"Создан клиент: id={customer_id}, name={name}")
        return customer_id

    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT id, name, phone, address
                FROM customers
                WHERE id = ?
                """,
                (customer_id,),
            ).fetchone()

        return dict(row) if row else None

    def get_customers(self) -> List[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, name, phone, address
                FROM customers
                ORDER BY id
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def update_customer(self, customer_id: int, name: str, phone: str = "", address: str = ""):
        if not self.get_customer(customer_id):
            raise ValueError("Клиент не найден")

        if not name or not name.strip():
            raise ValueError("Имя клиента не может быть пустым")

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE customers
                    SET name = ?, phone = ?, address = ?
                    WHERE id = ?
                    """,
                    (name.strip(), phone.strip(), address.strip(), customer_id),
                )

        logger.info(f"Обновлён клиент: id={customer_id}")

    def delete_customer(self, customer_id: int):
        """
        Удаляет клиента только если у него нет заказов.
        """

        if not self.get_customer(customer_id):
            raise ValueError("Клиент не найден")

        with closing(self._connect()) as connection:
            count = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM orders
                WHERE customer_id = ?
                """,
                (customer_id,),
            ).fetchone()["count"]

            if count > 0:
                raise ValueError("Нельзя удалить клиента, у него есть заказы")

            with connection:
                connection.execute(
                    """
                    DELETE FROM customers
                    WHERE id = ?
                    """,
                    (customer_id,),
                )

        logger.info(f"Удалён клиент: id={customer_id}")

    # ---------- Заказы ----------

    def _normalize_items(self, items) -> List[OrderItem]:
        normalized_items = []

        for item in items:
            if isinstance(item, OrderItem):
                normalized_items.append(item)
            elif isinstance(item, dict):
                normalized_items.append(
                    OrderItem(
                        product_name=item["product_name"],
                        quantity=item["quantity"],
                        price=item["price"],
                    )
                )
            else:
                raise ValueError("Некорректный формат товара")

        if not normalized_items:
            raise ValueError("В заказе должен быть хотя бы один товар")

        return normalized_items

    def _calculate_total(self, items: List[OrderItem]) -> float:
        return sum(item.subtotal for item in items)

    def add_order(self, customer_id: int, order_date: str, status: str, items) -> int:
        if status not in VALID_STATUSES:
            raise ValueError("Некорректный статус заказа")

        if not self.get_customer(customer_id):
            raise ValueError("Клиент не найден")

        normalized_items = self._normalize_items(items)
        total = self._calculate_total(normalized_items)

        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO orders (customer_id, order_date, status, total)
                    VALUES (?, ?, ?, ?)
                    """,
                    (customer_id, order_date, status, total),
                )

                order_id = cursor.lastrowid

                for item in normalized_items:
                    connection.execute(
                        """
                        INSERT INTO order_items (order_id, product_name, quantity, price)
                        VALUES (?, ?, ?, ?)
                        """,
                        (order_id, item.product_name, item.quantity, item.price),
                    )

        logger.info(f"Создан заказ: id={order_id}, total={total}")
        return order_id

    def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, order_id, product_name, quantity, price
                FROM order_items
                WHERE order_id = ?
                ORDER BY id
                """,
                (order_id,),
            ).fetchall()

        result = []

        for row in rows:
            item = dict(row)
            item["subtotal"] = item["quantity"] * item["price"]
            result.append(item)

        return result

    def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT 
                    orders.id,
                    orders.customer_id,
                    customers.name AS customer_name,
                    orders.order_date,
                    orders.status,
                    orders.total
                FROM orders
                JOIN customers ON orders.customer_id = customers.id
                WHERE orders.id = ?
                """,
                (order_id,),
            ).fetchone()

        if not row:
            return None

        order = dict(row)
        order["items"] = self.get_order_items(order_id)
        return order

    def get_orders(
        self,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                orders.id,
                orders.customer_id,
                customers.name AS customer_name,
                orders.order_date,
                orders.status,
                orders.total
            FROM orders
            JOIN customers ON orders.customer_id = customers.id
        """

        conditions = []
        params = []

        if status:
            if status not in VALID_STATUSES:
                raise ValueError("Некорректный статус заказа")
            conditions.append("orders.status = ?")
            params.append(status)

        if date_from:
            conditions.append("orders.order_date >= ?")
            params.append(date_from)

        if date_to:
            conditions.append("orders.order_date <= ?")
            params.append(date_to)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY orders.order_date DESC, orders.id DESC"

        with closing(self._connect()) as connection:
            rows = connection.execute(query, params).fetchall()

        orders = []

        for row in rows:
            order = dict(row)
            order["items"] = self.get_order_items(order["id"])
            orders.append(order)

        return orders

    def update_order(
        self,
        order_id: int,
        customer_id: Optional[int] = None,
        order_date: Optional[str] = None,
        status: Optional[str] = None,
        items=None,
    ):
        old_order = self.get_order(order_id)

        if not old_order:
            raise ValueError("Заказ не найден")

        customer_id = customer_id if customer_id is not None else old_order["customer_id"]
        order_date = order_date if order_date is not None else old_order["order_date"]
        status = status if status is not None else old_order["status"]

        if status not in VALID_STATUSES:
            raise ValueError("Некорректный статус заказа")

        if not self.get_customer(customer_id):
            raise ValueError("Клиент не найден")

        if items is None:
            normalized_items = self._normalize_items(old_order["items"])
        else:
            normalized_items = self._normalize_items(items)

        total = self._calculate_total(normalized_items)

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE orders
                    SET customer_id = ?, order_date = ?, status = ?, total = ?
                    WHERE id = ?
                    """,
                    (customer_id, order_date, status, total, order_id),
                )

                connection.execute(
                    """
                    DELETE FROM order_items
                    WHERE order_id = ?
                    """,
                    (order_id,),
                )

                for item in normalized_items:
                    connection.execute(
                        """
                        INSERT INTO order_items (order_id, product_name, quantity, price)
                        VALUES (?, ?, ?, ?)
                        """,
                        (order_id, item.product_name, item.quantity, item.price),
                    )

        logger.info(f"Обновлён заказ: id={order_id}")

    def delete_order(self, order_id: int):
        if not self.get_order(order_id):
            raise ValueError("Заказ не найден")

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    DELETE FROM order_items
                    WHERE order_id = ?
                    """,
                    (order_id,),
                )

                connection.execute(
                    """
                    DELETE FROM orders
                    WHERE id = ?
                    """,
                    (order_id,),
                )

        logger.info(f"Удалён заказ: id={order_id}")

    # ---------- Отчёты ----------

    def orders_count_by_status(self) -> Dict[str, int]:
        result = {status: 0 for status in VALID_STATUSES}

        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM orders
                GROUP BY status
                """
            ).fetchall()

        for row in rows:
            result[row["status"]] = row["count"]

        return result

    def top_clients_by_sum(self, limit: int = 3) -> List[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT 
                    customers.id,
                    customers.name,
                    SUM(orders.total) AS total_sum
                FROM orders
                JOIN customers ON orders.customer_id = customers.id
                WHERE orders.status != 'отменён'
                GROUP BY customers.id, customers.name
                ORDER BY total_sum DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def _period_bounds(self, period: str):
        today = date.today()

        if period == "day":
            start = today
            end = today

        elif period == "week":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)

        elif period == "month":
            start = today.replace(day=1)

            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)

            end = next_month - timedelta(days=1)

        else:
            raise ValueError("Период должен быть day, week или month")

        return start.isoformat(), end.isoformat()

    def revenue_for_period(self, period: str) -> float:
        date_from, date_to = self._period_bounds(period)

        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT SUM(total) AS revenue
                FROM orders
                WHERE order_date >= ?
                  AND order_date <= ?
                  AND status != 'отменён'
                """,
                (date_from, date_to),
            ).fetchone()

        return float(row["revenue"] or 0)

    def get_full_report(self, period: str = "month") -> Dict[str, Any]:
        return {
            "period": period,
            "orders_by_status": self.orders_count_by_status(),
            "top_clients": self.top_clients_by_sum(),
            "revenue": self.revenue_for_period(period),
        }

    # ---------- Тестовые данные ----------

    def seed_sample_data(self):
        """
        Добавляет тестовых клиентов и заказы.
        Удобно для первой проверки проекта.
        """

        if self.get_customers():
            return

        ivan_id = self.add_customer("Иван", "+79990000001", "Москва")
        anna_id = self.add_customer("Анна", "+79990000002", "Санкт-Петербург")
        oleg_id = self.add_customer("Олег", "+79990000003", "Казань")

        today = date.today().isoformat()

        self.add_order(
            ivan_id,
            today,
            "новый",
            [
                {"product_name": "Пицца", "quantity": 2, "price": 750},
                {"product_name": "Сок", "quantity": 1, "price": 200},
            ],
        )

        self.add_order(
            anna_id,
            today,
            "в доставке",
            [
                {"product_name": "Суши", "quantity": 3, "price": 500},
            ],
        )

        self.add_order(
            oleg_id,
            today,
            "выполнен",
            [
                {"product_name": "Бургер", "quantity": 4, "price": 350},
            ],
        )

        logger.info("Добавлены тестовые данные")