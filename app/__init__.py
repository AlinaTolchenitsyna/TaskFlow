from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from config import Config
from flask import Flask, Blueprint



db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
migrate = Migrate()
csrf = CSRFProtect()

auth_bp = Blueprint(
    "auth", 
    __name__, 
    template_folder="templates"  # ищет внутри app/templates/
)

# from . import auth_routes  # сюда вынести функции view

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Регистрация блюпринтов
    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app