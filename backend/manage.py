"""Flask-Migrate / Alembic entry point."""
from app import create_app
from app.extensions import db

app = create_app()

import app.models  # noqa: F401, E402
