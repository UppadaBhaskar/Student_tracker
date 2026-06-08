"""Wait until PostgreSQL is reachable (Docker startup)."""
import os
import sys
import time

from sqlalchemy import create_engine, text


def main(max_attempts: int = 60, delay: float = 2.0) -> None:
    url = os.environ.get("DATABASE_URL")
    if not url or url.startswith("sqlite"):
        return

    for attempt in range(1, max_attempts + 1):
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready.")
            return
        except Exception as exc:
            print(f"Waiting for database ({attempt}/{max_attempts}): {exc}")
            time.sleep(delay)

    print("Database did not become ready in time.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
