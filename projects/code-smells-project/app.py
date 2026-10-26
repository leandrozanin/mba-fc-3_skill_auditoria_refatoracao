from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database import close_db, init_db
from middlewares.error_handler import register_error_handlers
from views.routes import api


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Settings)
    if test_config:
        app.config.update(test_config)
    if app.config["CORS_ORIGINS"]:
        CORS(app, origins=app.config["CORS_ORIGINS"])
    app.register_blueprint(api)
    app.teardown_appcontext(close_db)
    register_error_handlers(app)
    with app.app_context():
        init_db()
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(
        host=application.config["HOST"],
        port=application.config["PORT"],
        debug=application.config["DEBUG"],
    )
