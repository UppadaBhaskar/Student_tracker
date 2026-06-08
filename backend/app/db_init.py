"""Ensure SQLite/Postgres schema exists before serving requests."""

import os

from sqlalchemy import inspect, text

from app.extensions import db


def ensure_database(app) -> None:
    """Run migrations when the schema is missing or only partially applied."""
    with app.app_context():
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())

        if "users" in tables:
            return

        from flask_migrate import upgrade

        # Alembic stamped but migration never ran (only alembic_version row/table).
        if tables <= {"alembic_version"}:
            if "alembic_version" in tables:
                db.session.execute(text("DELETE FROM alembic_version"))
                db.session.commit()
            upgrade()
            return

        url = db.engine.url
        if url.get_backend_name() == "sqlite" and url.database not in (None, ":memory:"):
            db.session.remove()
            db.engine.dispose()
            if os.path.exists(url.database):
                os.remove(url.database)
            upgrade()
            return

        raise RuntimeError(
            "Database schema is incomplete (missing users table). Run: flask db upgrade"
        )
