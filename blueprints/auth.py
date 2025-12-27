from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect("/admin" if user.role == "admin" else "/user")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not User.query.filter_by(username=request.form["username"]).first():
            db.session.add(User(
                username=request.form["username"],
                password_hash=generate_password_hash(request.form["password"]),
                role="user"
            ))
            db.session.commit()
            return redirect("/login")
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
