from flask import Flask
from config import Config
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.user import user_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(role="admin").first():
            db.session.add(User(
                username="admin",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            ))
            db.session.commit()

    app.run()
