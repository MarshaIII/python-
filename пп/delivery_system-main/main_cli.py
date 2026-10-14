import argparse

from database import Database
from data_export import export_orders, import_orders


def print_report(report):
    print()
    print("ОТЧЁТ")
    print("=" * 40)

    print(f"Период: {report['period']}")
    print()

    print("Количество заказов по статусам:")
    for status, count in report["orders_by_status"].items():
        print(f"- {status}: {count}")

    print()
    print("Топ-3 клиента по сумме заказов:")

    if not report["top_clients"]:
        print("Нет данных")
    else:
        for index, client in enumerate(report["top_clients"], start=1):
            print(f"{index}. {client['name']} — {client['total_sum']}")

    print()
    print(f"Выручка за период: {report['revenue']}")
    print("=" * 40)
    print()


def print_orders(orders):
    if not orders:
        print("Заказы не найдены")
        return

    for order in orders:
        print("-" * 40)
        print(f"ID: {order['id']}")
        print(f"Дата: {order['order_date']}")
        print(f"Клиент: {order['customer_name']}")
        print(f"Статус: {order['status']}")
        print(f"Сумма: {order['total']}")
        print("Товары:")

        for item in order["items"]:
            print(
                f"  - {item['product_name']}: "
                f"{item['quantity']} × {item['price']} = {item['subtotal']}"
            )

    print("-" * 40)


def main():
    database = Database()

    parser = argparse.ArgumentParser(
        description="Внутреннее приложение для учёта заказов компании «Быстрая доставка»"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="Показать отчёт")
    report_parser.add_argument(
        "--period",
        choices=["day", "week", "month"],
        default="month",
        help="Период отчёта: day, week или month",
    )

    export_parser = subparsers.add_parser("export", help="Экспортировать заказы")
    export_parser.add_argument(
        "--file",
        required=True,
        help="Имя файла для экспорта, например orders.json или orders.xml",
    )

    import_parser = subparsers.add_parser("import", help="Импортировать заказы")
    import_parser.add_argument(
        "--file",
        required=True,
        help="Имя файла для импорта, например orders.json или orders.xml",
    )

    list_orders_parser = subparsers.add_parser("list-orders", help="Показать список заказов")
    list_orders_parser.add_argument(
        "--status",
        choices=["новый", "в доставке", "выполнен", "отменён"],
        required=False,
        help="Фильтр по статусу",
    )
    list_orders_parser.add_argument(
        "--date-from",
        required=False,
        help="Дата начала периода в формате YYYY-MM-DD",
    )
    list_orders_parser.add_argument(
        "--date-to",
        required=False,
        help="Дата конца периода в формате YYYY-MM-DD",
    )

    subparsers.add_parser("seed", help="Добавить тестовые данные")

    args = parser.parse_args()

    try:
        if args.command == "report":
            report = database.get_full_report(args.period)
            print_report(report)

        elif args.command == "export":
            path = export_orders(database, args.file)
            print(f"Экспорт выполнен: {path}")

        elif args.command == "import":
            count = import_orders(database, args.file)
            print(f"Импорт выполнен. Импортировано заказов: {count}")

        elif args.command == "list-orders":
            orders = database.get_orders(
                status=args.status,
                date_from=args.date_from,
                date_to=args.date_to,
            )
            print_orders(orders)

        elif args.command == "seed":
            database.seed_sample_data()
            print("Тестовые данные добавлены")

    except Exception as error:
        print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()