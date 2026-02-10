from flask import Blueprint, render_template, redirect, request, session, flash
from extensions import db
from models import Book, BorrowHistory

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required():
    return session.get("role") == "admin"


@admin_bp.route("/")
def dashboard():
    if not admin_required():
        flash("Please log in with an admin account to view that page.", "warning")
        return redirect("/login")
    return render_template(
        "admin.html",
        books=Book.query.all(),
        history=BorrowHistory.query.order_by(BorrowHistory.borrow_date.desc()).all()
    )


@admin_bp.route("/add", methods=["POST"])
def add_book():
    if not admin_required():
        flash("Only admins can add books.", "danger")
        return redirect("/login")

    title = request.form["title"].strip()
    author = request.form["author"].strip()
    if not title or not author:
        flash("Please enter both a title and author.", "warning")
        return redirect("/admin")

    db.session.add(Book(
        title=title,
        author=author
    ))
    db.session.commit()
    flash(f"'{title}' by {author} was added to the library.", "success")
    return redirect("/admin")


@admin_bp.route("/delete/<int:id>")
def delete_book(id):
    if not admin_required():
        flash("Only admins can delete books.", "danger")
        return redirect("/login")

    book = Book.query.get_or_404(id)
    if book.status == "Borrowed":
        flash(f"'{book.title}' is currently borrowed and can't be deleted yet.", "warning")
        return redirect("/admin")

    db.session.delete(book)
    db.session.commit()
    flash(f"'{book.title}' was removed from the library.", "info")
    return redirect("/admin")
