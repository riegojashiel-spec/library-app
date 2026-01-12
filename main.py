import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'jasmine'

# ==============================
# DATABASE CONFIG
# SQLite (LOCAL) + PostgreSQL (RAILWAY)
# ==============================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Fix for Railway postgres URL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Local SQLite fallback
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "books.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==============================
# BOOK MODEL
# ==============================
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    bn_id = db.Column(db.String(50), unique=True, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Book {self.title}>'

# ==============================
# CREATE TABLES
# ==============================
with app.app_context():
    db.create_all()

# ==============================
# ROUTES
# ==============================

# Home Page
@app.route('/')
def home():
    return render_template('register_book.html')

# Register Book
@app.route('/register_book', methods=['POST'])
def register_book():
    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    bn_id = request.form.get('bn_id')
    genre = request.form.get('genre')
    language = request.form.get('language')

    # Check duplicate BN ID
    existing_book = Book.query.filter_by(bn_id=bn_id).first()
    if existing_book:
        flash('BN ID number already exists!', 'error')
        return redirect(url_for('home'))

    new_book = Book(
        title=title,
        author=author,
        publisher=publisher,
        bn_id=bn_id,
        genre=genre,
        language=language
    )

    try:
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('success'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))

# Success Page
@app.route('/success')
def success():
    return render_template('success.html')

# View All Books
@app.route('/books')
def view_books():
    all_books = Book.query.order_by(Book.id.desc()).all()
    return render_template('book.html', books=all_books)

# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)