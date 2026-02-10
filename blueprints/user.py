from flask import Blueprint, render_template, redirect, session, flash
from datetime import datetime, timedelta
from extensions import db
from models import Book, BorrowHistory
from config import Config

user_bp = Blueprint("user", __name__, url_prefix="/user")


def user_required():
    return session.get("role") == "user"


@user_bp.route("/")
def dashboard():
    if not user_required():
        flash("Please log in with a user account to continue.", "warning")
        return redirect("/login")
    return render_template("user.html", books=Book.query.all())


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
    db.session.add(BorrowHistory(
        user_id=session["user_id"],
        book_id=id,
        due_date=datetime.utcnow() + timedelta(days=7)
    ))
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
        return_date=None
    ).first()

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
            "warning"
        )
    else:
        flash(f"'{book.title}' was returned successfully. Thank you!", "success")

    return redirect("/user")
