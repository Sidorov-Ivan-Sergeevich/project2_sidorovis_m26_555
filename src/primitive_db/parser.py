import ast
import re

from primitive_db.constants import VALID_TYPES


def split_csv(text):
    """Split comma-separated values preserving quoted strings."""
    values = []
    current = []
    in_quotes = False
    quote_char = ""
    for char in text:
        if char in {'"', "'"}:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif quote_char == char:
                in_quotes = False
        if char == "," and not in_quotes:
            values.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        values.append("".join(current).strip())
    return values


def parse_literal(raw_value):
    """Parse string value to Python literal."""
    value = raw_value.strip()
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return ast.literal_eval(value)
    return value


def parse_columns(column_tokens):
    """Parse columns like name:str age:int."""
    columns = []
    for token in column_tokens:
        if ":" not in token:
            raise ValueError(token)
        name, column_type = token.split(":", 1)
        if not name or column_type not in VALID_TYPES:
            raise ValueError(token)
        columns.append((name, column_type))
    return columns


def parse_values(command):
    """Parse values from values (...)."""
    match = re.search(r"values\s*\((.*)\)\s*$", command, re.IGNORECASE)
    if not match:
        raise ValueError(command)
    return [parse_literal(item) for item in split_csv(match.group(1))]


def parse_condition(condition_text):
    """Parse where clause column = value."""
    if "=" not in condition_text:
        raise ValueError(condition_text)
    column, raw_value = condition_text.split("=", 1)
    column = column.strip()
    if not column:
        raise ValueError(condition_text)
    return {column: parse_literal(raw_value)}


def parse_set_clause(set_text):
    """Parse set clause column = value, column = value."""
    result = {}
    for item in split_csv(set_text):
        result.update(parse_condition(item))
    return result