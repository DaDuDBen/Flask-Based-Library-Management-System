# Flask Library Management System

A full-stack Library Management System built using **Flask**, **SQLAlchemy**, and **Bootstrap**, featuring role-based access, secure authentication, borrowing workflows, due dates, and fines.

This project demonstrates **backend system design**, **database modeling**, and **modular Flask architecture using Blueprints**.

---

## Features

### Authentication & Security

* User registration and login
* Password hashing using Werkzeug
* Session-based authentication
* Role-based access control (Admin / User)

### Admin Features

* Add and delete books
* View all books and their status
* View complete borrow history
* See late returns and calculated fines

### User Features

* Browse available books
* Borrow and return books
* Automatic due date assignment
* Late return fine calculation

### Borrow & Fine System

* Borrow history stored permanently
* Due date (default: 7 days)
* Late return detection
* Fine calculation (₹10 per late day)

### Architecture

* Flask Blueprints for modular design
* Separate concerns for auth, admin, and user
* SQLite database (easy to run locally)

---

## Project Structure

```
library-system/
├ app.py
├ config.py
├ extensions.py
├ models.py
├ blueprints/
│   ├ __init__.py
│   ├ auth.py
│   ├ admin.py
│   └ user.py
├ templates/
│   ├ login.html
│   ├ register.html
│   ├ admin.html
│   └ user.html
├ library.db
└ README.md
```

---

## Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite + SQLAlchemy ORM
* **Frontend:** HTML + Bootstrap 5
* **Security:** Werkzeug password hashing
* **Architecture:** Flask Blueprints

---

## Setup & Run Instructions

### Install dependencies

```bash
pip install flask flask-sqlalchemy
```

### Run the application

```bash
python app.py
```

### Open in browser

```
http://127.0.0.1:5000
```

---

## Default Admin Credentials

| Role  | Username | Password |
| ----- | -------- | -------- |
| Admin | admin    | admin123 |

(New users can register as normal users.)

---

## Demo Workflow

1. Login as **admin**
2. Add books
3. Register a new user
4. Login as user
5. Borrow a book
6. Return it late
7. View fine in admin dashboard

---

## Future Enhancements

* REST API for mobile/frontend apps
* Automated unit tests (pytest)
* Deployment on Render / Railway
* Docker support
* Email notifications

---

## License

This project is for educational purposes.
