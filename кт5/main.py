import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime
import os

TASKS_FILE = "tasks.txt"

def days_word(n):
    if 11 <= n % 100 <= 14:
        return "дней"
    last = n % 10
    if last == 1:
        return "день"
    if 2 <= last <= 4:
        return "дня"
    return "дней"

def load_tasks():
    tasks = []
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|", 1)
                if len(parts) == 2:
                    date_str, task = parts
                    date_str = date_str.strip()
                    task = task.strip()
                    if date_str == "":
                        tasks.append({"date": None, "task": task})
                    else:
                        tasks.append({"date": date_str, "task": task})
                else:
                    tasks.append({"date": None, "task": line.strip()})
    return tasks

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        for t in tasks:
            date_part = t["date"] if t["date"] is not None else ""
            f.write(f"{date_part}|{t['task']}\n")

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Напоминалка ToDo")
        self.root.configure(bg="black")

        self.tasks = []
        self.selected_index = None

        frame_input = tk.Frame(root, bg="black")
        frame_input.pack(pady=5, padx=5, fill="x")

        tk.Label(frame_input, text="Задача:", fg="white", bg="black",
                 font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5)
        self.entry_task = tk.Entry(frame_input, width=30, font=("Arial", 10))
        self.entry_task.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="Дедлайн (ДД-ММ-ГГГГ):", fg="white", bg="black",
                 font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5)
        self.entry_date = tk.Entry(frame_input, width=30, font=("Arial", 10))
        self.entry_date.grid(row=1, column=1, padx=5)

        btn_frame = tk.Frame(root, bg="black")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Добавить задачу", command=self.add_task,
                  bg="#333", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить выбранную", command=self.delete_task,
                  bg="#333", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

        self.text = tk.Text(root, bg="black", fg="white", insertbackground="white",
                            font=("Arial", 11), wrap="word", state="disabled",
                            height=20, width=70)
        self.text.pack(pady=10, padx=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.text, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.text.tag_configure("overdue", foreground="red")
        self.text.tag_configure("today", foreground="orange")
        self.text.tag_configure("upcoming", foreground="white")
        self.text.tag_configure("current", foreground="yellow", underline=True,
                                font=("Arial", 11, "underline"))
        self.text.tag_configure("selected", background="gray30")

        self.text.bind("<Button-1>", self.on_click)

        self.tasks = load_tasks()
        self.display_tasks()

    def display_tasks(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)

        today = date.today()

        for i, task in enumerate(self.tasks):
            date_str = task["date"]
            task_text = task["task"]

            if date_str is None:
                line = f"• {task_text}\n"
                self.text.insert(tk.END, line, "current")
            else:
                try:
                    deadline = datetime.strptime(date_str, "%d-%m-%Y").date()
                    delta = (deadline - today).days
                except ValueError:
                    line = f"• {task_text} (неверная дата)\n"
                    self.text.insert(tk.END, line, "current")
                    continue

                if delta < 0:
                    days_ago = -delta
                    line = f"Прошло {days_ago} {days_word(days_ago)} от {task_text}\n"
                    self.text.insert(tk.END, line, "overdue")
                elif delta == 0:
                    line = f"Прямо сейчас происходит {task_text}\n"
                    self.text.insert(tk.END, line, "today")
                else:  # delta > 0
                    line = f"Осталось {delta} {days_word(delta)} до {task_text}\n"
                    self.text.insert(tk.END, line, "upcoming")

        self.text.configure(state="disabled")
        self.selected_index = None

    def add_task(self):
        task = self.entry_task.get().strip()
        date_str = self.entry_date.get().strip()

        if not task:
            messagebox.showwarning("Ошибка", "Введите название задачи.")
            return

        if date_str:
            try:
                datetime.strptime(date_str, "%d-%m-%Y")
            except ValueError:
                messagebox.showwarning("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
                return
            new_task = {"date": date_str, "task": task}
        else:
            new_task = {"date": None, "task": task}

        self.tasks.append(new_task)
        save_tasks(self.tasks)
        self.display_tasks()

        self.entry_task.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)

    def delete_task(self):
        if self.selected_index is None:
            messagebox.showinfo("Удаление", "Сначала кликните на задачу для выбора.")
            return

        confirm = messagebox.askyesno("Подтверждение", "Удалить выбранную задачу?")
        if confirm:
            del self.tasks[self.selected_index]
            save_tasks(self.tasks)
            self.display_tasks()

    def on_click(self, event):
        self.text.configure(state="normal")
        self.text.tag_remove("selected", "1.0", tk.END)

        index = self.text.index(f"@{event.x},{event.y}")
        line_start = self.text.index(f"{index} linestart")
        line_end = self.text.index(f"{index} lineend")

        self.text.tag_add("selected", line_start, line_end)
        self.text.configure(state="disabled")

        line_num = int(line_start.split(".")[0]) - 1
        if 0 <= line_num < len(self.tasks):
            self.selected_index = line_num
        else:
            self.selected_index = None

root = tk.Tk()
app = TodoApp(root)
root.geometry("400x600")
root.mainloop()