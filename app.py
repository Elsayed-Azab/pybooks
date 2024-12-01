from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from supabase import create_client
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = '82134fb0f92f2dcce833a2773124992b2f9dfa9353654f1d8d1a50fe351789d7'

SUPABASE_URL = "https://ddtizhmtdsmygzgigpfx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkdGl6aG10ZHNteWd6Z2lncGZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxOTc4NTUsImV4cCI6MjA0NTc3Mzg1NX0.Eot-5cF5p_QZCajJ-UG5uBtCliEwxu_q5voa7O0ryng"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

conn = psycopg2.connect(
    host="aws-0-eu-central-1.pooler.supabase.com",
    database="postgres",
    user="postgres.ddtizhmtdsmygzgigpfx",
    password="Azab2002Azab",
)

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    conn.rollback() 
    flash(f"An unexpected error occurred: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def home():
    books = []
    try:
        with conn.cursor() as cur:
            if request.method == 'POST':
                query = request.form['query']
                cur.execute(
                    """SELECT b.*, a.name FROM books b, author a WHERE b.author_id = a.author_id AND title ILIKE %s OR isbn ILIKE %s""",
                    (f"%{query}%", f"%{query}%")
                )
            else:
                cur.execute("SELECT b.*, a.name FROM books b, author a WHERE b.author_id = a.author_id")
            books = cur.fetchall()
    except Exception as e:
        conn.rollback()
        flash(f"Error fetching books: {e}")
    return render_template('home.html', books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            supabase_id = response.user.id
            
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM users WHERE supabase_id = %s", (supabase_id,))
                user = cur.fetchone()
                if user is None:
                    flash('User not found in local database.')
                    return redirect(url_for('signup'))
                session['user'] = user[0]
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Login failed. ' + str(e))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        hashed_password = generate_password_hash(password)

        response = supabase.auth.sign_up({"email": email, "password": password})
        try:
            supabase_id = response.user.id
            
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (supabase_id, email, name, password, address) VALUES (%s, %s, %s, %s, %s)",
                    (supabase_id, email, name, hashed_password, address)
                )
                conn.commit()
            
            flash('Account created successfully. Please confirm your email.')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Account creation failed. Try again. ' + str(e))
    return render_template('signup.html')

@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_details(book_id):
    is_borrower = False
    with conn.cursor() as cur:
        cur.execute("SELECT b.*, a.name FROM books b, author a WHERE b.author_id = a.author_id AND book_id = %s", (book_id,))
        book_data = cur.fetchone()
        
        if book_data:
            book = {
                "book_id": book_data[0],
                "title": book_data[1],
                "author": book_data[6],
                "ISBN": book_data[2],
                "publication_year": book_data[4],
                "availability_status": book_data[3],
            }
            if 'user' in session:
                cur.execute(
                    "SELECT COUNT(*) FROM borrows WHERE book_id = %s AND user_id = %s",
                    (book_id, session['user'])
                )
                is_borrower = cur.fetchone()[0] > 0
        else:
            flash('Book not found.')
            return redirect(url_for('home'))

    if request.method == 'POST':
        action = request.form.get('action')
        if 'user' in session:
            with conn.cursor() as cur:
                try:
                    if action == 'borrow':
                        cur.execute(
                            """INSERT INTO transaction (staff_id, borrower_id, book_id, trans_type, trans_status, trans_date) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)""",
                            (1, session['user'], book_id, 'Borrow', 'Completed')
                        )

                        cur.execute(
                            """INSERT INTO borrows (user_id, book_id, dt_borrow) VALUES (%s, %s, CURRENT_DATE)""",
                            (session['user'], book_id)
                        )

                        cur.execute(
                            """UPDATE books SET available = FALSE WHERE book_id = %s""",
                            (book_id,)
                        )
                        flash('Book borrowed successfully.')
                    elif action == 'return' and is_borrower:
                        cur.execute(
                            """INSERT INTO transaction (staff_id, borrower_id, book_id, trans_type, trans_status, trans_date) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)""",
                            (1, session['user'], book_id, 'Return', 'Completed')
                        )

                        cur.execute(
                            """DELETE FROM borrows WHERE user_id = %s AND book_id = %s""",
                            (session['user'], book_id)
                        )

                        cur.execute(
                            """UPDATE books SET available = TRUE WHERE book_id = %s""",
                            (book_id,)
                        )
                        flash('Book returned successfully.')
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    flash('An error occurred: ' + str(e))
            return redirect(url_for('book_details', book_id=book_id))
        else:
            flash('Please log in to perform this action.')

    return render_template('book_details.html', book=book, is_borrower=is_borrower)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']
    borrowed_books = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT book_id, dt_borrow FROM borrows WHERE user_id = %s", (user_id,))
            transactions = cur.fetchall()
            for transaction in transactions:
                book_id = transaction[0]
                cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
                book = cur.fetchone()
                if book:
                    book_data = {
                        "book_id": book[0],
                        "title": book[1],
                        "ISBN": book[2],
                        "availability_status": book[3],
                        "publication_year": book[4],
                        "author": book[5],
                        "borrow_date": transaction[1],
                    }
                    borrowed_books.append(book_data)
    except Exception as e:
        conn.rollback()
        flash('An error occurred while fetching borrowed books: ' + str(e))
        
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        if book_id:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """DELETE FROM borrows WHERE user_id = %s AND book_id = %s""",
                        (user_id, book_id)
                    )
                    cur.execute(
                        """UPDATE books SET available = TRUE WHERE book_id = %s""",
                        (book_id,)
                    )
                    cur.execute(
                        """INSERT INTO transaction (staff_id, borrower_id, book_id, trans_type, trans_status, trans_date)
                           VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)""",
                        (1, user_id, book_id, 'Return', 'Completed')
                    )
                    conn.commit()
                    flash('Book returned successfully.')
                    return redirect(url_for('dashboard'))
            except Exception as e:
                conn.rollback()
                flash('An error occurred while returning the book: ' + str(e))

    return render_template('dashboard.html', borrowed_books=borrowed_books)

@app.route('/admin/books', methods=['GET'])
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    books = []
    with conn.cursor() as cur:
        cur.execute("SELECT b.*, a.name FROM books b, author a WHERE b.author_id = a.author_id")
        books = cur.fetchall()
    return render_template('admin_dashboard.html', books=books)

@app.route('/admin/books/add', methods=['GET', 'POST'])
def add_book():
    if 'user' not in session:
        return redirect(url_for('login'))

    authors = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT author_id, name FROM author")
            authors = cur.fetchall()
    except Exception as e:
        conn.rollback()
        flash(f'Error fetching authors: {e}')

    if request.method == 'POST':
        title = request.form['title']
        author_id = request.form['author_id']
        isbn = request.form['isbn']
        publication_year = request.form['publication_year']

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO books (title, author_id, isbn, publish_year, available) VALUES (%s, %s, %s, %s, TRUE)",
                    (title, author_id, isbn, publication_year)
                )
                conn.commit()
                flash('Book added successfully.')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding book: {e}')

    return render_template('add_book.html', authors=authors)

@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    book = None
    authors = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = cur.fetchone()
            cur.execute("SELECT author_id, name FROM author")
            authors = cur.fetchall()
    except Exception as e:
        conn.rollback()
        flash(f'Error fetching book or authors: {e}')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        author_id = request.form['author_id']
        isbn = request.form['isbn']
        publication_year = request.form['publication_year']

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE books SET title = %s, author_id = %s, isbn = %s, publish_year = %s WHERE book_id = %s",
                    (title, author_id, isbn, publication_year, book_id)
                )
                conn.commit()
                flash('Book updated successfully.')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating book: {e}')

    return render_template('edit_book.html', book=book, authors=authors)

@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            conn.commit()
            flash('Book deleted successfully.')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting book: {e}')

    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
