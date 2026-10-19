#!/usr/bin/env python3
import shlex

import prompt

from primitive_db.constants import (
    HELP_TEXT,
    INVALID_COMMAND,
    INVALID_VALUE,
    META_FILE,
    RUN_MESSAGE,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    print_rows,
    select,
    update,
)
from primitive_db.parser import (
    parse_columns,
    parse_condition,
    parse_set_clause,
    parse_values,
)
from primitive_db.utils import load_metadata


def print_help():
    """Print help text."""
    print(HELP_TEXT)


def welcome():
    """Print welcome message."""
    print(RUN_MESSAGE)
    print_help()


def get_where_text(user_input):
    """Return original-case text after WHERE."""
    lower_input = user_input.lower()
    where_index = lower_input.index(" where ")
    return user_input[where_index + 7 :]


def run():
    """Run database command loop."""
    welcome()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string("Введите команду: ").strip()

        if not user_input:
            continue

        try:
            tokens = shlex.split(user_input)
        except ValueError:
            print(INVALID_VALUE.format(value=user_input))
            continue

        command = tokens[0].lower()

        if command == "exit":
            print("Выход из программы.")
            break

        if command == "help":
            print_help()
            continue

        if command == "list_tables":
            list_tables(metadata)
            continue

        if command == "create_table":
            if len(tokens) < 3:
                print(INVALID_VALUE.format(value=user_input))
                continue

            table_name = tokens[1]

            try:
                columns = parse_columns(tokens[2:])
            except ValueError as error:
                print(INVALID_VALUE.format(value=error))
                continue

            create_table(metadata, table_name, columns)
            continue

        if command == "drop_table":
            if len(tokens) != 2:
                print(INVALID_VALUE.format(value=user_input))
                continue

            drop_table(metadata, tokens[1])
            continue

        if command == "info":
            if len(tokens) != 2:
                print(INVALID_VALUE.format(value=user_input))
                continue

            info(metadata, tokens[1])
            continue

        is_insert_command = (
            command == "insert"
            and len(tokens) >= 4
            and tokens[1].lower() == "into"
        )

        if is_insert_command:
            table_name = tokens[2]

            try:
                values = parse_values(user_input)
            except ValueError as error:
                print(INVALID_VALUE.format(value=error))
                continue

            insert(metadata, table_name, values)
            continue

        is_select_command = (
            command == "select"
            and len(tokens) >= 3
            and tokens[1].lower() == "from"
        )

        if is_select_command:
            table_name = tokens[2]

            if len(tokens) == 3:
                rows = select(metadata, table_name)
                if rows is not None:
                    print_rows(rows)
                continue

            if len(tokens) >= 5 and tokens[3].lower() == "where":
                try:
                    where_clause = parse_condition(get_where_text(user_input))
                except ValueError as error:
                    print(INVALID_VALUE.format(value=error))
                    continue

                rows = select(metadata, table_name, where_clause)
                if rows is not None:
                    print_rows(rows)
                continue

        is_update_command = (
            command == "update"
            and " set " in user_input.lower()
            and " where " in user_input.lower()
        )

        if is_update_command:
            table_name = tokens[1]
            lower_input = user_input.lower()
            set_start = lower_input.index(" set ") + 5
            where_start = lower_input.index(" where ")

            set_text = user_input[set_start:where_start]
            where_text = user_input[where_start + 7 :]

            try:
                set_clause = parse_set_clause(set_text)
                where_clause = parse_condition(where_text)
            except ValueError as error:
                print(INVALID_VALUE.format(value=error))
                continue

            update(metadata, table_name, set_clause, where_clause)
            continue

        is_delete_command = (
            command == "delete"
            and len(tokens) >= 5
            and tokens[1].lower() == "from"
            and " where " in user_input.lower()
        )

        if is_delete_command:
            table_name = tokens[2]

            try:
                where_clause = parse_condition(get_where_text(user_input))
            except ValueError as error:
                print(INVALID_VALUE.format(value=error))
                continue

            delete(metadata, table_name, where_clause)
            continue

        print(INVALID_COMMAND.format(command=command))