import json
from pathlib import Path

from primitive_db.constants import DATA_DIR, META_FILE


def load_metadata(filepath=META_FILE):
    """Load metadata from JSON file."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Save metadata to JSON file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def ensure_data_dir():
    """Create data directory if it does not exist."""
    Path(DATA_DIR).mkdir(exist_ok=True)


def get_table_path(table_name):
    """Return path to table data file."""
    ensure_data_dir()
    return Path(DATA_DIR) / f"{table_name}.json"


def load_table_data(table_name):
    """Load table data from JSON file."""
    table_path = get_table_path(table_name)
    try:
        with open(table_path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Save table data to JSON file."""
    table_path = get_table_path(table_name)
    with open(table_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)