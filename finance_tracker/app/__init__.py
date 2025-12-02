from flask import Flask,render_template,Blueprint
from config import Config
from app.extensions import db, login_manager
from app.models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # HOMEPAGE ROUTE
    @app.route("/")
    def home():
        return render_template("home.html")
    

    # Blueprints
    from app.auth import auth_bp
    from app.finance import finance_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(finance_bp, url_prefix="/finance")

    return app
