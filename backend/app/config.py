import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def _default_sqlite_uri() -> str:
    """Use backend/instance/fabricator.db so run.py and flask db share one file."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    instance_dir = os.path.join(base, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, "fabricator.db")
    return "sqlite:///" + db_path.replace("\\", "/")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_EXPIRE_DAYS", "7")))

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or _default_sqlite_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    TRAINER_EMAIL = os.getenv("TRAINER_EMAIL", "trainer@workshop.local")
    TRAINER_PASSWORD = os.getenv("TRAINER_PASSWORD", "trainer123")
    SEED_DEMO_DATA = _env_bool("SEED_DEMO_DATA", False)

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

    @staticmethod
    def validate():
        weak = []
        if Config.SECRET_KEY in ("", "dev-secret-key", "change-me-in-production"):
            weak.append("SECRET_KEY")
        if Config.JWT_SECRET_KEY in ("", "dev-jwt-secret", "change-me-jwt-secret"):
            weak.append("JWT_SECRET_KEY")
        if Config.TRAINER_PASSWORD in ("", "trainer123"):
            weak.append("TRAINER_PASSWORD")
        if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
            weak.append("DATABASE_URL (use PostgreSQL in production)")
        if weak:
            raise RuntimeError(
                "Production misconfiguration — set strong values for: "
                + ", ".join(weak)
            )


def resolve_config_name(explicit: str | None = None) -> str:
    if explicit and explicit != "default":
        return explicit
    env = os.getenv("FLASK_ENV", "development").lower()
    return "production" if env == "production" else "development"


config_by_name = {
    "development": DevelopmentConfig,
    "default": DevelopmentConfig,
    "production": ProductionConfig,
}
