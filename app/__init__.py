from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app import models  # noqa: F401

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app