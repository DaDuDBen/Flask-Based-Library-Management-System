from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session

from config import Config
from extensions import db
from models import Book, BorrowHistory

user_bp = Blueprint("user", __name__, url_prefix="/user")


def user_required():
    return session.get("role") == "user"


@user_bp.route("/")
def dashboard():
    if not user_required():
        flash("Please log in with a user account to continue.", "warning")
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
    elif status_filter == "mine":
        books_query = books_query.filter(Book.borrowed_by == session["user_id"])

    books = books_query.order_by(Book.title.asc()).all()

    my_active_loans = (
        BorrowHistory.query.filter_by(user_id=session["user_id"], return_date=None)
        .order_by(BorrowHistory.due_date.asc())
        .all()
    )
    loan_book_ids = [loan.book_id for loan in my_active_loans]
    loan_books = {book.id: book for book in Book.query.filter(Book.id.in_(loan_book_ids)).all()} if loan_book_ids else {}

    now = datetime.utcnow()
    loans_with_meta = []
    for loan in my_active_loans:
        book = loan_books.get(loan.book_id)
        days_left = (loan.due_date - now).days
        loans_with_meta.append(
            {
                "history": loan,
                "book": book,
                "days_left": days_left,
                "is_due_soon": 0 <= days_left <= 2,
                "is_overdue": days_left < 0,
            }
        )

    all_books = Book.query.all()
    stats = {
        "total": len(all_books),
        "available": len([book for book in all_books if book.status == "Available"]),
        "borrowed": len([book for book in all_books if book.status == "Borrowed"]),
        "my_loans": len(my_active_loans),
    }

    return render_template(
        "user.html",
        books=books,
        loans_with_meta=loans_with_meta,
        stats=stats,
        q=q,
        status_filter=status_filter,
    )


@user_bp.route("/borrow/<int:id>")
def borrow(id):
    if not user_required():
        flash("Please log in with a user account to borrow books.", "warning")
        return redirect("/login")

    book = Book.query.get_or_404(id)
    if book.status != "Available":
        flash("That book is already borrowed right now.", "warning")
        return redirect("/user")

    book.status = "Borrowed"
    book.borrowed_by = session["user_id"]
    db.session.add(
        BorrowHistory(
            user_id=session["user_id"],
            book_id=id,
            due_date=datetime.utcnow() + timedelta(days=7),
        )
    )
    db.session.commit()
    flash(f"You borrowed '{book.title}'. It's due in 7 days.", "success")
    return redirect("/user")


@user_bp.route("/return/<int:id>")
def return_book(id):
    if not user_required():
        flash("Please log in with a user account to return books.", "warning")
        return redirect("/login")

    book = Book.query.get_or_404(id)
    if book.borrowed_by != session["user_id"]:
        flash("You can only return books that you borrowed.", "danger")
        return redirect("/user")

    history = BorrowHistory.query.filter_by(
        user_id=session["user_id"],
        book_id=id,
        return_date=None,
    ).first()

    late_days = 0
    if history:
        history.return_date = datetime.utcnow()
        late_days = (history.return_date - history.due_date).days
        if late_days > 0:
            history.is_late = True
            history.fine_amount = late_days * Config.FINE_PER_DAY

    book.status = "Available"
    book.borrowed_by = None
    db.session.commit()

    if history and history.is_late:
        flash(
            f"'{book.title}' was returned. It was {late_days} day(s) late, so a fine of ₹{history.fine_amount} was added.",
            "warning",
        )
    else:
        flash(f"'{book.title}' was returned successfully. Thank you!", "success")

    return redirect("/user")
