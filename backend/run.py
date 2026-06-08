from app import create_app
from app.db_init import ensure_database

app = create_app()
ensure_database(app)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
