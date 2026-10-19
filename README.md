# Primitive DB

Консольное приложение на Python для работы с простой JSON-базой данных.

## Установка

```bash
uv sync
```

## Запуск

```bash
uv run database
```

## Команды

- `create_table users name:str age:int is_active:bool`
- `list_tables`
- `drop_table users`
- `insert into users values ("Sergei", 28, true)`
- `select from users`
- `select from users where age = 28`
- `update users set age = 29 where name = "Sergei"`
- `delete from users where ID = 1`
- `info users`
- `help`
- `exit`