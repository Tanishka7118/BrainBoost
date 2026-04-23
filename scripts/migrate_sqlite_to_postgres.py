import argparse
import json
from collections.abc import Iterable

from sqlalchemy import MetaData, create_engine, select, text

from app.db.database import Base


def _normalize_row(table_name: str, row: dict) -> dict:
    normalized = dict(row)
    if table_name == "generated_questions":
        raw_options = normalized.get("options_json")
        if isinstance(raw_options, str):
            try:
                normalized["options_json"] = json.loads(raw_options)
            except json.JSONDecodeError:
                normalized["options_json"] = [raw_options]
    return normalized


def _postgres_reset_sequences(connection, table_names: Iterable[str]) -> None:
    for table_name in table_names:
        table_identifier = f'"{table_name}"'
        connection.execute(
            text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_identifier}', 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                )
                FROM {table_identifier}
                """
            ),
        )


def migrate(sqlite_url: str, postgres_url: str) -> None:
    sqlite_engine = create_engine(sqlite_url)
    postgres_engine = create_engine(postgres_url)

    Base.metadata.create_all(bind=postgres_engine)

    source_metadata = MetaData()
    source_metadata.reflect(bind=sqlite_engine)

    with sqlite_engine.connect() as source_conn, postgres_engine.begin() as target_conn:
        for table in reversed(Base.metadata.sorted_tables):
            target_conn.execute(table.delete())

        for target_table in Base.metadata.sorted_tables:
            source_table = source_metadata.tables.get(target_table.name)
            if source_table is None:
                continue

            rows = source_conn.execute(select(source_table)).mappings().all()
            if not rows:
                continue

            payloads = []
            target_columns = set(target_table.columns.keys())
            for row in rows:
                normalized_row = _normalize_row(target_table.name, dict(row))
                payloads.append({k: normalized_row[k] for k in normalized_row if k in target_columns})

            target_conn.execute(target_table.insert(), payloads)

        _postgres_reset_sequences(target_conn, [table.name for table in Base.metadata.sorted_tables])

    print("Data migration completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate BrainBoost data from SQLite to PostgreSQL")
    parser.add_argument(
        "--sqlite-url",
        default="sqlite:///./brainboost.db",
        help="SQLite SQLAlchemy URL (default: sqlite:///./brainboost.db)",
    )
    parser.add_argument(
        "--postgres-url",
        default="postgresql+psycopg://postgres:qwerty@localhost:5432/brainboost",
        help="PostgreSQL SQLAlchemy URL",
    )
    args = parser.parse_args()

    migrate(sqlite_url=args.sqlite_url, postgres_url=args.postgres_url)


if __name__ == "__main__":
    main()
