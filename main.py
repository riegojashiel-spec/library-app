import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "jasmine")

# ==============================
# DATABASE CONFIG (Fixed & Optimized)
# ==============================
# 1. Look for Railway's DATABASE_URL
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # 2. Fix the 'postgres://' vs 'postgresql://' issue for SQLAlchemy 1.4+
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # 3. Fallback to local SQLite if no environment variable is found
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

@app.route('/')
def home():
    return render_template('register_book.html')

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

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/books')
def view_books():
    all_books = Book.query.order_by(Book.id.desc()).all()
    return render_template('book.html', books=all_books)

# ==============================
# RUN APP (Optimized for Cloud)
# ==============================
if __name__ == "__main__":
    # Railway provides a PORT variable; locally it defaults to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
