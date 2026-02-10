from flask import Blueprint, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("We couldn't find that username. Please try again.", "danger")
        elif not check_password_hash(user.password_hash, password):
            flash("That password didn't match. Try again.", "danger")
        else:
            session["user_id"] = user.id
            session["role"] = user.role
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/admin" if user.role == "admin" else "/user")

        return render_template("login.html", remembered_username=username)

    return render_template("login.html", remembered_username="")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Please enter both a username and password.", "danger")
        elif len(password) < 6:
            flash("Use at least 6 characters for a stronger password.", "warning")
        elif password != confirm_password:
            flash("Your passwords didn't match. Please re-enter them.", "warning")
        elif User.query.filter_by(username=username).first():
            flash("That username is already taken. Please choose another one.", "warning")
        else:
            db.session.add(
                User(
                    username=username,
                    password_hash=generate_password_hash(password),
                    role="user",
                )
            )
            db.session.commit()
            flash("Your account has been created. You can log in now.", "success")
            return redirect("/login")

        return render_template("register.html", remembered_username=username)

    return render_template("register.html", remembered_username="")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/login")
