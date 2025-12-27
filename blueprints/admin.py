from flask import Blueprint, render_template, redirect, request, session
from extensions import db
from models import Book, BorrowHistory

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required():
    return session.get("role") == "admin"


@admin_bp.route("/")
def dashboard():
    if not admin_required():
        return redirect("/login")
    return render_template(
        "admin.html",
        books=Book.query.all(),
        history=BorrowHistory.query.order_by(BorrowHistory.borrow_date.desc()).all()
    )


@admin_bp.route("/add", methods=["POST"])
def add_book():
    if admin_required():
        db.session.add(Book(
            title=request.form["title"],
            author=request.form["author"]
        ))
        db.session.commit()
    return redirect("/admin")


@admin_bp.route("/delete/<int:id>")
def delete_book(id):
    if admin_required():
        db.session.delete(Book.query.get_or_404(id))
        db.session.commit()
    return redirect("/admin")
