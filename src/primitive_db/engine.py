from pathlib import Path
import prompt
from primitive_db.core import create_table, delete_row, drop_table, insert_row, list_tables, select_rows
from primitive_db.utils import load_metadata, save_metadata
from primitive_db.core import create_table, delete_row, drop_table, insert_row, list_tables, select_rows, update_row
from primitive_db.core import create_table, delete_row, drop_table, find_rows, insert_row, list_tables, select_rows, update_row

METADATA_FILE = Path("db_meta.json")


def print_help():
    """Print help message."""
    print("\n***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    print("<command> create_table - создать таблицу")
    print("<command> list_tables - показать таблицы")
    print("<command> drop_table - удалить таблицу")
    print("<command> insert - добавить запись")
    print("<command> select - показать записи таблицы")
    print("<command> delete - удалить запись по ID")
    print("<command> update - изменить запись по ID")
    print("<command> find - найти записи по условию")

def welcome():
    """Print welcome message."""
    print("Первая попытка запустить проект!")


def run():
    """Run command loop."""
    welcome()

    while True:
        command = prompt.string("Введите команду: ")

        if command == "help":
            print_help()

        elif command == "create_table":
            metadata = load_metadata(METADATA_FILE)

            table_name = prompt.string("Введите имя таблицы: ")
            columns_text = prompt.string(
                "Введите столбцы через пробел в формате имя:тип: "
            )

            columns = columns_text.split()
            metadata = create_table(metadata, table_name, columns)
            save_metadata(METADATA_FILE, metadata)

        elif command == "list_tables":
            metadata = load_metadata(METADATA_FILE)
            list_tables(metadata)

        elif command == "drop_table":
            metadata = load_metadata(METADATA_FILE)

            table_name = prompt.string("Введите имя таблицы для удаления: ")
            metadata = drop_table(metadata, table_name)
            save_metadata(METADATA_FILE, metadata)

        elif command == "insert":
            metadata = load_metadata(METADATA_FILE)

            table_name = prompt.string("Введите имя таблицы: ")
            values_text = prompt.string(
                "Введите значения через пробел в формате столбец=значение: "
            )

            values = values_text.split()
            insert_row(metadata, table_name, values)

        elif command == "select":
            metadata = load_metadata(METADATA_FILE)

            table_name = prompt.string("Введите имя таблицы: ")
            select_rows(metadata, table_name)

        elif command == "delete":
            metadata = load_metadata(METADATA_FILE)

            table_name = prompt.string("Введите имя таблицы: ")
            row_id = int(prompt.string("Введите ID записи для удаления: "))

            delete_row(metadata, table_name, row_id)        

        elif command == "update":
            metadata = load_metadata(METADATA_FILE)

            table_name = prompt.string("Введите имя таблицы: ")
            row_id = int(prompt.string("Введите ID записи для изменения: "))
            values_text = prompt.string(
                "Введите новые значения через пробел в формате столбец=значение: "
            )

            values = values_text.split()
            update_row(metadata, table_name, row_id, values)

        elif command == "find":
            metadata = load_metadata(METADATA_FILE)

            table_name = prompt.string("Введите имя таблицы: ")
            condition = prompt.string(
                "Введите условие в формате столбец=значение: "
            )

            find_rows(metadata, table_name, condition)

        elif command == "exit":
            print("Выход из программы.")
            break

        else:
            print(f'Функции "{command}" нет. Попробуйте снова.')