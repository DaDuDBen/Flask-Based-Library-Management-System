from flask import Blueprint, flash, redirect, render_template, request, session

from extensions import db
from models import Book, BorrowHistory, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required():
    return session.get("role") == "admin"


@admin_bp.route("/")
def dashboard():
    if not admin_required():
        flash("Please log in with an admin account to view that page.", "warning")
        return redirect("/login")

    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all")

    books_query = Book.query
    if q:
        books_query = books_query.filter(
            (Book.title.ilike(f"%{q}%")) | (Book.author.ilike(f"%{q}%"))
        )
    if status_filter == "available":
        books_query = books_query.filter(Book.status == "Available")
    elif status_filter == "borrowed":
        books_query = books_query.filter(Book.status == "Borrowed")

    books = books_query.order_by(Book.title.asc()).all()

    users = {user.id: user.username for user in User.query.all()}
    history = BorrowHistory.query.order_by(BorrowHistory.borrow_date.desc()).all()
    book_lookup = {book.id: book.title for book in Book.query.all()}

    history_rows = []
    total_fines = 0
    for row in history:
        total_fines += row.fine_amount
        history_rows.append(
            {
                "entry": row,
                "username": users.get(row.user_id, f"User #{row.user_id}"),
                "book_title": book_lookup.get(row.book_id, f"Book #{row.book_id}"),
            }
        )

    all_books = Book.query.all()
    stats = {
        "total_books": len(all_books),
        "available_books": len([book for book in all_books if book.status == "Available"]),
        "borrowed_books": len([book for book in all_books if book.status == "Borrowed"]),
        "members": User.query.filter_by(role="user").count(),
        "total_fines": total_fines,
    }

    return render_template(
        "admin.html",
        books=books,
        history_rows=history_rows,
        stats=stats,
        user_lookup=users,
        q=q,
        status_filter=status_filter,
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

    db.session.add(Book(title=title, author=author))
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
