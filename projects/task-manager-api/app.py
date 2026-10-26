import os

from flask import Flask
from flask_cors import CORS

from database import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///tasks.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SECRET_KEY') or os.urandom(32),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    CORS(app, origins=os.environ.get('CORS_ORIGINS', '').split(',') or [])

    from models import Category, Task, User
    from routes.report_routes import report_bp
    from routes.task_routes import task_bp
    from routes.user_routes import user_bp

    with app.app_context():
        db.create_all()

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    return app


if __name__ == '__main__':
    create_app().run(debug=False, host='127.0.0.1', port=int(os.environ.get('PORT', '5000')))
