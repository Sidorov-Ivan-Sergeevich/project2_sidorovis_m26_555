from prettytable import PrettyTable

from primitive_db.constants import META_FILE, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data, save_metadata, save_table_data

select_cache = create_cacher()


def _normalize_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    raise ValueError(f"Некорректное значение bool: {value}")


def _validate_value(value, expected_type):
    if expected_type == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"Ожидался int, получено: {value}")
        return value
    if expected_type == "str":
        if not isinstance(value, str):
            raise ValueError(f"Ожидался str, получено: {value}")
        return value
    if expected_type == "bool":
        return _normalize_bool(value)
    raise ValueError(f"Неподдерживаемый тип: {expected_type}")


def _get_schema(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(table_name)
    return metadata[table_name]


def _match_where(row, where_clause):
    if where_clause is None:
        return True
    for key, value in where_clause.items():
        if key not in row:
            raise KeyError(key)
        if row[key] != value:
            return False
    return True


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Create a table in metadata."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    validated_columns = []
    for name, column_type in columns:
        if column_type not in VALID_TYPES:
            raise ValueError(
                f"Некорректное значение: {column_type}. Попробуйте снова."
            )
        validated_columns.append([name, column_type])
    metadata[table_name] = [["ID", "int"], *validated_columns]
    save_metadata(META_FILE, metadata)
    save_table_data(table_name, [])
    columns_text = ", ".join(
        f"{column_name}:{column_type}"
        for column_name, column_type in metadata[table_name]
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


@handle_db_errors
def list_tables(metadata):
    """Print all tables."""
    if not metadata:
        print("Таблиц пока нет.")
        return []
    for table_name in metadata:
        print(table_name)
    return list(metadata.keys())


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Drop table from metadata."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    del metadata[table_name]
    save_metadata(META_FILE, metadata)
    save_table_data(table_name, [])
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Insert row into table."""
    schema = _get_schema(metadata, table_name)
    if len(values) != len(schema) - 1:
        raise ValueError("Количество значений не соответствует количеству столбцов.")
    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1
    row = {"ID": new_id}
    for (column_name, column_type), value in zip(schema[1:], values, strict=False):
        row[column_name] = _validate_value(value, column_type)
    data.append(row)
    save_table_data(table_name, data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return data


@handle_db_errors
@log_time
def select(metadata, table_name, where_clause=None):
    """Select rows from table."""
    _get_schema(metadata, table_name)
    data = load_table_data(table_name)
    cache_key = (
        table_name,
        tuple(sorted(where_clause.items())) if where_clause else None,
        str(data),
    )

    def calculate_result():
        return [row for row in data if _match_where(row, where_clause)]

    rows = select_cache(cache_key, calculate_result)
    return rows


@handle_db_errors
def update(metadata, table_name, set_clause, where_clause):
    """Update rows in table."""
    schema = _get_schema(metadata, table_name)
    schema_map = {column_name: column_type for column_name, column_type in schema}
    data = load_table_data(table_name)
    updated_ids = []
    for row in data:
        if _match_where(row, where_clause):
            for column_name, value in set_clause.items():
                if column_name == "ID":
                    raise ValueError("Поле ID нельзя изменять.")
                if column_name not in schema_map:
                    raise KeyError(column_name)
                row[column_name] = _validate_value(value, schema_map[column_name])
            updated_ids.append(row["ID"])
    if not updated_ids:
        raise ValueError("Записи по условию не найдены.")
    save_table_data(table_name, data)
    for row_id in updated_ids:
        print(f'Запись с ID={row_id} в таблице "{table_name}" успешно обновлена.')
    return data


@handle_db_errors
@confirm_action("удаление записи")
def delete(metadata, table_name, where_clause):
    """Delete rows from table."""
    _get_schema(metadata, table_name)
    data = load_table_data(table_name)
    rows_to_delete = [row for row in data if _match_where(row, where_clause)]
    if not rows_to_delete:
        raise ValueError("Записи по условию не найдены.")
    remaining_rows = [row for row in data if not _match_where(row, where_clause)]
    save_table_data(table_name, remaining_rows)
    for row in rows_to_delete:
        print(
            f'Запись с ID={row["ID"]} успешно удалена из таблицы "{table_name}".'
        )
    return remaining_rows


@handle_db_errors
def info(metadata, table_name):
    """Print table info."""
    schema = _get_schema(metadata, table_name)
    data = load_table_data(table_name)
    columns_text = ", ".join(
        f"{name}:{column_type}" for name, column_type in schema
    )
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_text}")
    print(f"Количество записей: {len(data)}")
    return {"table": table_name, "columns": schema, "count": len(data)}


def print_rows(rows):
    """Print rows with PrettyTable."""
    if not rows:
        print("Нет данных.")
        return
    table = PrettyTable()
    table.field_names = list(rows[0].keys())
    for row in rows:
        table.add_row(list(row.values()))
    print(table)