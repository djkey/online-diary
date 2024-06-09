from flask import Flask
import pymysql
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Подключение к базе данных
    connection = pymysql.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'],
        cursorclass=pymysql.cursors.DictCursor
    )

    app.connection = connection

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
