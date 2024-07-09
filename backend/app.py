from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from auth.auth_routes import auth_blueprint
from routes import init_routes
from flask_cors import CORS

from config import Config
from database import db
from tree.personal_tree import personal_tree


def create_app():
    from LLM.llm_routes import llm_blueprint

    current_app = Flask(__name__)
    current_app.config.from_object(Config)

    CORS(current_app, supports_credentials=True)

    JWTManager(current_app)

    db.init_app(current_app)

    migrate = Migrate(current_app, db)
    migrate.init_app(current_app, db)

    init_routes(current_app)
    current_app.register_blueprint(auth_blueprint)
    current_app.register_blueprint(llm_blueprint, url_prefix='/llm')
    current_app.register_blueprint(personal_tree, url_prefix='/api/personal')

    return current_app


app = create_app()


if __name__ == '__main__':
    app.run()
