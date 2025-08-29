#### Описание
Приложение для парсинга сайта https://www.flip.kz.
Можно парсить целый каталог, либо отдельный продукт.

Парсинг каталога предназначен только для https://www.flip.kz/catalog?subsection=2649, возможно еще и спарсить и другие каталоги, если они схожи по структуре документа.

#### Установка и запуск
Требование:
- Docker

Порты:
- FastAPI App - 8000,
- VNC Server - 5900.

Копировать содержимое `.env.example` в файл `.env`, оно должно быть в корне проекта, если надо можно изменить.

Сборка проекта:
```bash
docker compose up --build --detach
```

И затем надо применить миграций:
```bash
docker exec -it flip-catalog-parser-app python -m alembic upgrade head
```

Тест:
```bash
docker exec -it flip-catalog-parser-app python -m pytest -v -s
```
