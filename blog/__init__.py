import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flaskext.markdown import Markdown
from flask_mail import Mail
from blog.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    markdown = Markdown(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # registering blueprints
    from blog.auth.routes import auth
    from blog.posts.routes import posts
    from blog.main.routes import main


    app.register_blueprint(auth)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app