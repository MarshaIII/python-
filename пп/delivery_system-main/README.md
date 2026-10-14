# Delivery System

Внутреннее приложение для учёта заказов компании «Быстрая доставка».

## Описание проекта

Проект позволяет вести учёт клиентов и заказов службы доставки.

Реализованы:

- управление клиентами;
- управление заказами;
- хранение товаров внутри заказа;
- фильтрация заказов по статусу и дате;
- отчёты;
- экспорт заказов в JSON и XML;
- импорт заказов из JSON и XML;
- CLI-режим через argparse;
- GUI-режим через Tkinter;
- логирование;
- тесты pytest.

## Технологии

- Python 3.8+
- SQLite
- Tkinter
- argparse
- logging
- json
- xml.etree.ElementTree
- pytest

## Структура проекта

```text
delivery_system/
├── main_cli.py
├── main_gui.py
├── database.py
├── models.py
├── data_export.py
├── logger_config.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
├── logs/
└── tests/
    ├── test_database.py
    ├── test_models.py
    └── test_export.py
```

## Установка

Склонировать репозиторий:

```bash
git clone https://github.com/LACKYON/delivery_system.git
cd delivery_system
```

Создать виртуальное окружение:

```bash
python -m venv venv
```

Активировать виртуальное окружение на Windows:

```bash
venv\Scripts\activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Запуск CLI

Добавить тестовые данные:

```bash
python main_cli.py seed
```

Показать отчёт за месяц:

```bash
python main_cli.py report --period month
```

Показать отчёт за неделю:

```bash
python main_cli.py report --period week
```

Показать отчёт за день:

```bash
python main_cli.py report --period day
```

Показать список заказов:

```bash
python main_cli.py list-orders
```

Показать заказы только со статусом "новый":

```bash
python main_cli.py list-orders --status "новый"
```

Экспортировать заказы в JSON:

```bash
python main_cli.py export --file orders_backup.json
```

Экспортировать заказы в XML:

```bash
python main_cli.py export --file orders_backup.xml
```

Импортировать заказы из JSON:

```bash
python main_cli.py import --file orders_backup.json
```

Импортировать заказы из XML:

```bash
python main_cli.py import --file orders_backup.xml
```

## Запуск GUI

```bash
python main_gui.py
```

В GUI можно:

- добавить клиента;
- добавить заказ;
- редактировать заказ;
- удалить заказ;
- фильтровать заказы по статусу;
- смотреть отчёт.

## Запуск тестов

```bash
pytest
```

## База данных

Используется SQLite.

База создаётся автоматически в папке:

```text
data/delivery.db
```

## Логирование

Логи сохраняются в файл:

```text
logs/app.log
```

## Автор
Марилов Ярослав
Учебный проект по Python.