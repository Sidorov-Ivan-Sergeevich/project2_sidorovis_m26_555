from pathlib import Path
import json
from prettytable import PrettyTable


VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """Create a new table in metadata."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = [("ID", "int")]

    for column in columns:
        if ":" not in column:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        column_name, column_type = column.split(":", 1)

        if column_type not in VALID_TYPES:
            print(f"Некорректное значение: {column_type}. Попробуйте снова.")
            return metadata

        parsed_columns.append((column_name, column_type))

    metadata[table_name] = parsed_columns

    table_file = Path(f"{table_name}.json")
    with open(table_file, "w", encoding="utf-8") as file:
        json.dump([], file, ensure_ascii=False, indent=4)

    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{name}:{col_type}" for name, col_type in parsed_columns)
    )
    return metadata


def drop_table(metadata, table_name):
    """Drop table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    table_file = Path(f"{table_name}.json")
    if table_file.exists():
        table_file.unlink()

    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Print all tables."""
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


def convert_value(value, column_type):
    """Convert string value to column type."""
    if column_type == "int":
        return int(value)

    if column_type == "bool":
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        raise ValueError

    return value


def insert_row(metadata, table_name, values):
    """Insert one row into a table."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]
    row = {}

    for item in values:
        if "=" not in item:
            print(f"Некорректное значение: {item}. Попробуйте снова.")
            return

        column_name, value = item.split("=", 1)

        if column_name == "ID":
            print('Ошибка: Поле "ID" заполняется автоматически.')
            return

        column_type = None
        for name, data_type in columns:
            if name == column_name:
                column_type = data_type
                break

        if column_type is None:
            print(f'Ошибка: Столбца "{column_name}" нет в таблице.')
            return

        try:
            row[column_name] = convert_value(value, column_type)
        except ValueError:
            print(
                f'Ошибка: Значение "{value}" '
                f'не соответствует типу "{column_type}".'
            )
            return

    table_file = Path(f"{table_name}.json")

    with open(table_file, "r", encoding="utf-8") as file:
        rows = json.load(file)

    if rows:
        max_id = max(item.get("ID", 0) for item in rows)
    else:
        max_id = 0

    row["ID"] = max_id + 1
    rows.append(row)

    with open(table_file, "w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=4)

    print(f'Запись успешно добавлена в таблицу "{table_name}".')


def select_rows(metadata, table_name):
    """Print all rows from a table."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    table_file = Path(f"{table_name}.json")

    with open(table_file, "r", encoding="utf-8") as file:
        rows = json.load(file)

    if not rows:
        print(f'В таблице "{table_name}" пока нет записей.')
        return

    columns = [name for name, _ in metadata[table_name]]

    table = PrettyTable()
    table.field_names = columns

    for row in rows:
        table.add_row([row.get(column, "") for column in columns])

    print(table)


def delete_row(metadata, table_name, row_id):
    """Delete row from table by ID."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    table_file = Path(f"{table_name}.json")

    with open(table_file, "r", encoding="utf-8") as file:
        rows = json.load(file)

    new_rows = [row for row in rows if row.get("ID") != row_id]

    if len(new_rows) == len(rows):
        print(f'Ошибка: Запись с ID {row_id} не найдена.')
        return

    with open(table_file, "w", encoding="utf-8") as file:
        json.dump(new_rows, file, ensure_ascii=False, indent=4)

    print(f'Запись с ID {row_id} успешно удалена из таблицы "{table_name}".')

def update_row(metadata, table_name, row_id, values):
    """Update row fields by ID."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    table_file = Path(f"{table_name}.json")

    with open(table_file, "r", encoding="utf-8") as file:
        rows = json.load(file)

    row_to_update = None

    for row in rows:
        if row.get("ID") == row_id:
            row_to_update = row
            break

    if row_to_update is None:
        print(f'Ошибка: Запись с ID {row_id} не найдена.')
        return

    for item in values:
        if "=" not in item:
            print(f"Некорректное значение: {item}. Попробуйте снова.")
            return

        column_name, value = item.split("=", 1)

        if column_name == "ID":
            print('Ошибка: Поле "ID" изменять нельзя.')
            return

        column_type = None

        for name, data_type in metadata[table_name]:
            if name == column_name:
                column_type = data_type
                break

        if column_type is None:
            print(f'Ошибка: Столбца "{column_name}" нет в таблице.')
            return

        try:
            row_to_update[column_name] = convert_value(value, column_type)
        except ValueError:
            print(
                f'Ошибка: Значение "{value}" '
                f'не соответствует типу "{column_type}".'
            )
            return

    with open(table_file, "w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=4)

    print(f'Запись с ID {row_id} успешно обновлена.')
    
def find_rows(metadata, table_name, condition):
    """Find rows by one condition: column=value."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    if "=" not in condition:
        print("Некорректное условие. Используйте формат столбец=значение.")
        return

    column_name, value = condition.split("=", 1)

    if column_name == "ID":
        column_type = "int"
    else:
        column_type = None

        for name, data_type in metadata[table_name]:
            if name == column_name:
                column_type = data_type
                break

    if column_type is None:
        print(f'Ошибка: Столбца "{column_name}" нет в таблице.')
        return

    try:
        search_value = convert_value(value, column_type)
    except ValueError:
        print(
            f'Ошибка: Значение "{value}" '
            f'не соответствует типу "{column_type}".'
        )
        return

    table_file = Path(f"{table_name}.json")

    with open(table_file, "r", encoding="utf-8") as file:
        rows = json.load(file)

    found_rows = [
        row for row in rows
        if row.get(column_name) == search_value
    ]

    if not found_rows:
        print("Подходящие записи не найдены.")
        return

    columns = [name for name, _ in metadata[table_name]]

    table = PrettyTable()
    table.field_names = columns

    for row in found_rows:
        table.add_row([row.get(column, "") for column in columns])

    print(table)