import tkinter as tk
from datetime import date, datetime
from tkinter import ttk, messagebox

from database import Database
from models import VALID_STATUSES


class DeliveryApp:
    def __init__(self):
        self.database = Database()

        self.root = tk.Tk()
        self.root.title("Быстрая доставка")
        self.root.geometry("900x500")

        self.status_filter = tk.StringVar(value="все")

        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(top_frame, text="Фильтр по статусу:").pack(side="left")

        status_combo = ttk.Combobox(
            top_frame,
            textvariable=self.status_filter,
            values=["все"] + list(VALID_STATUSES),
            state="readonly",
            width=20,
        )
        status_combo.pack(side="left", padx=5)

        ttk.Button(top_frame, text="Применить фильтр", command=self.load_orders).pack(
            side="left", padx=5
        )

        ttk.Button(top_frame, text="Сбросить", command=self.reset_filter).pack(
            side="left", padx=5
        )

        columns = ("id", "date", "customer", "status", "total")

        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=15,
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("customer", text="Клиент")
        self.tree.heading("status", text="Статус")
        self.tree.heading("total", text="Сумма")

        self.tree.column("id", width=50)
        self.tree.column("date", width=120)
        self.tree.column("customer", width=250)
        self.tree.column("status", width=150)
        self.tree.column("total", width=100)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Добавить клиента", command=self.open_customer_form).pack(
            side="left", padx=5
        )

        ttk.Button(button_frame, text="Добавить заказ", command=self.open_add_order_form).pack(
            side="left", padx=5
        )

        ttk.Button(button_frame, text="Редактировать заказ", command=self.open_edit_order_form).pack(
            side="left", padx=5
        )

        ttk.Button(button_frame, text="Удалить заказ", command=self.delete_selected_order).pack(
            side="left", padx=5
        )

        ttk.Button(button_frame, text="Показать отчёт", command=self.show_report).pack(
            side="left", padx=5
        )

        ttk.Button(button_frame, text="Обновить", command=self.load_orders).pack(
            side="left", padx=5
        )

    def reset_filter(self):
        self.status_filter.set("все")
        self.load_orders()

    def load_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        status = self.status_filter.get()

        if status == "все":
            status = None

        orders = self.database.get_orders(status=status)

        for order in orders:
            self.tree.insert(
                "",
                "end",
                iid=str(order["id"]),
                values=(
                    order["id"],
                    order["order_date"],
                    order["customer_name"],
                    order["status"],
                    order["total"],
                ),
            )

    def get_selected_order_id(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите заказ")
            return None

        return int(selected[0])

    def open_customer_form(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить клиента")
        window.geometry("350x220")

        ttk.Label(window, text="Имя:").pack(pady=5)
        name_entry = ttk.Entry(window, width=40)
        name_entry.pack()

        ttk.Label(window, text="Телефон:").pack(pady=5)
        phone_entry = ttk.Entry(window, width=40)
        phone_entry.pack()

        ttk.Label(window, text="Адрес:").pack(pady=5)
        address_entry = ttk.Entry(window, width=40)
        address_entry.pack()

        def save_customer():
            try:
                self.database.add_customer(
                    name=name_entry.get(),
                    phone=phone_entry.get(),
                    address=address_entry.get(),
                )

                messagebox.showinfo("Готово", "Клиент добавлен")
                window.destroy()

            except Exception as error:
                messagebox.showerror("Ошибка", str(error))

        ttk.Button(window, text="Сохранить", command=save_customer).pack(pady=15)

    def open_add_order_form(self):
        self.open_order_form()

    def open_edit_order_form(self):
        order_id = self.get_selected_order_id()

        if order_id is None:
            return

        self.open_order_form(order_id=order_id)

    def open_order_form(self, order_id=None):
        customers = self.database.get_customers()

        if not customers:
            messagebox.showwarning(
                "Нет клиентов",
                "Сначала добавьте хотя бы одного клиента",
            )
            return

        order = None

        if order_id is not None:
            order = self.database.get_order(order_id)

            if not order:
                messagebox.showerror("Ошибка", "Заказ не найден")
                return

        window = tk.Toplevel(self.root)
        window.title("Заказ")
        window.geometry("450x420")

        customer_values = [f"{customer['id']} - {customer['name']}" for customer in customers]

        ttk.Label(window, text="Клиент:").pack(pady=5)

        customer_combo = ttk.Combobox(
            window,
            values=customer_values,
            state="readonly",
            width=45,
        )
        customer_combo.pack()

        if order:
            for value in customer_values:
                if value.startswith(f"{order['customer_id']} - "):
                    customer_combo.set(value)
                    break
        else:
            customer_combo.current(0)

        ttk.Label(window, text="Дата заказа YYYY-MM-DD:").pack(pady=5)

        date_entry = ttk.Entry(window, width=45)
        date_entry.pack()

        if order:
            date_entry.insert(0, order["order_date"])
        else:
            date_entry.insert(0, date.today().isoformat())

        ttk.Label(window, text="Статус:").pack(pady=5)

        status_combo = ttk.Combobox(
            window,
            values=list(VALID_STATUSES),
            state="readonly",
            width=45,
        )
        status_combo.pack()

        if order:
            status_combo.set(order["status"])
        else:
            status_combo.set("новый")

        first_item = None

        if order and order["items"]:
            first_item = order["items"][0]

        ttk.Label(window, text="Название товара:").pack(pady=5)

        product_entry = ttk.Entry(window, width=45)
        product_entry.pack()

        if first_item:
            product_entry.insert(0, first_item["product_name"])

        ttk.Label(window, text="Количество:").pack(pady=5)

        quantity_entry = ttk.Entry(window, width=45)
        quantity_entry.pack()

        if first_item:
            quantity_entry.insert(0, str(first_item["quantity"]))
        else:
            quantity_entry.insert(0, "1")

        ttk.Label(window, text="Цена:").pack(pady=5)

        price_entry = ttk.Entry(window, width=45)
        price_entry.pack()

        if first_item:
            price_entry.insert(0, str(first_item["price"]))
        else:
            price_entry.insert(0, "0")

        def save_order():
            try:
                customer_text = customer_combo.get()

                if not customer_text:
                    raise ValueError("Выберите клиента")

                customer_id = int(customer_text.split(" - ")[0])

                order_date = date_entry.get().strip()
                datetime.strptime(order_date, "%Y-%m-%d")

                status = status_combo.get()

                item = {
                    "product_name": product_entry.get(),
                    "quantity": int(quantity_entry.get()),
                    "price": float(price_entry.get()),
                }

                if order_id is None:
                    self.database.add_order(
                        customer_id=customer_id,
                        order_date=order_date,
                        status=status,
                        items=[item],
                    )
                    messagebox.showinfo("Готово", "Заказ добавлен")

                else:
                    self.database.update_order(
                        order_id=order_id,
                        customer_id=customer_id,
                        order_date=order_date,
                        status=status,
                        items=[item],
                    )
                    messagebox.showinfo("Готово", "Заказ обновлён")

                window.destroy()
                self.load_orders()

            except Exception as error:
                messagebox.showerror("Ошибка", str(error))

        ttk.Button(window, text="Сохранить", command=save_order).pack(pady=15)

    def delete_selected_order(self):
        order_id = self.get_selected_order_id()

        if order_id is None:
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить заказ id={order_id}?",
        )

        if not confirm:
            return

        try:
            self.database.delete_order(order_id)
            messagebox.showinfo("Готово", "Заказ удалён")
            self.load_orders()

        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def show_report(self):
        report = self.database.get_full_report("month")

        window = tk.Toplevel(self.root)
        window.title("Отчёт")
        window.geometry("500x400")

        text = tk.Text(window, wrap="word")
        text.pack(fill="both", expand=True, padx=10, pady=10)

        text.insert("end", "ОТЧЁТ ЗА МЕСЯЦ\n")
        text.insert("end", "=" * 40 + "\n\n")

        text.insert("end", "Количество заказов по статусам:\n")

        for status, count in report["orders_by_status"].items():
            text.insert("end", f"{status}: {count}\n")

        text.insert("end", "\nТоп-3 клиента:\n")

        if report["top_clients"]:
            for index, client in enumerate(report["top_clients"], start=1):
                text.insert("end", f"{index}. {client['name']} — {client['total_sum']}\n")
        else:
            text.insert("end", "Нет данных\n")

        text.insert("end", f"\nВыручка за месяц: {report['revenue']}\n")

        text.config(state="disabled")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DeliveryApp()
    app.run()