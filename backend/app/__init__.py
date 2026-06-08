import os

from flask import Flask, jsonify
from flask_cors import CORS

from app.config import ProductionConfig, config_by_name, resolve_config_name
from app.exceptions import AppException
from app.extensions import db, jwt, migrate
from app.routes import analytics_bp, attempts_bp, auth_bp, entities_bp, questions_bp, students_bp


def _cors_origins():
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def create_app(config_name: str | None = None) -> Flask:
    resolved = resolve_config_name(config_name)
    app = Flask(__name__)
    app.config.from_object(config_by_name[resolved])

    if resolved == "production":
        ProductionConfig.validate()

    CORS(
        app,
        resources={r"/api/*": {"origins": _cors_origins()}},
        supports_credentials=True,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    api_prefix = "/api/v1"

    app.register_blueprint(auth_bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(entities_bp, url_prefix=f"{api_prefix}/entities")
    app.register_blueprint(students_bp, url_prefix=f"{api_prefix}/students")
    app.register_blueprint(questions_bp, url_prefix=f"{api_prefix}/questions")
    app.register_blueprint(attempts_bp, url_prefix=f"{api_prefix}/attempts")
    app.register_blueprint(analytics_bp, url_prefix=f"{api_prefix}")

    @app.errorhandler(AppException)
    def handle_app_exception(e: AppException):
        return jsonify({"success": False, "error": e.message}), e.status_code

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app
