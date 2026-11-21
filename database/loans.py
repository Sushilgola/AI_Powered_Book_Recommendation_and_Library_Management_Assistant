
# database/loans.py

from datetime import date, timedelta

from database.connection import get_connection


def borrow_book(book_id, user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        conn.start_transaction()

        # Lock the book record while checking availability
        cursor.execute(
            """
            SELECT available_copies, is_active
            FROM books
            WHERE book_id = %s
            FOR UPDATE
            """,
            (book_id,)
        )

        book = cursor.fetchone()

        if not book or not book["is_active"]:
            conn.rollback()
            return False, "Book not found."

        if book["available_copies"] <= 0:
            conn.rollback()
            return False, "Book is currently unavailable."

        # Reduce available quantity
        cursor.execute(
            """
            UPDATE books
            SET available_copies = available_copies - 1
            WHERE book_id = %s
            AND available_copies > 0
            """,
            (book_id,)
        )

        if cursor.rowcount != 1:
            conn.rollback()
            return False, "Book is no longer available."

        # Set borrowing dates
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=14)

        # Check whether this user has already borrowed this book
        cursor.execute(
            """
            SELECT loan_id
            FROM book_loans
            WHERE user_id = %s
            AND book_id = %s
            AND status = 'BORROWED'
            LIMIT 1
            """,
            (user_id, book_id)
        )

        existing_loan = cursor.fetchone()

        if existing_loan:
            conn.rollback()
            return False, "You have already borrowed this book. Please return it before borrowing again."
       
        # Create borrowing record
        cursor.execute(
            """
            INSERT INTO book_loans
            (user_id, book_id, borrow_date, due_date, status)
            VALUES (%s, %s, %s, %s, 'BORROWED')
            """,
            (user_id, book_id, borrow_date, due_date)
        )

        conn.commit()

        return True, f"Borrowed successfully! Return by {due_date}."

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


def return_book(loan_id, user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        conn.start_transaction()

        # A user can return only their own active borrowing
        cursor.execute(
            """
            SELECT book_id
            FROM book_loans
            WHERE loan_id = %s
            AND user_id = %s
            AND status = 'BORROWED'
            FOR UPDATE
            """,
            (loan_id, user_id)
        )

        loan = cursor.fetchone()

        if not loan:
            conn.rollback()
            return False, "Active borrowing record not found."

        # Update borrowing record
        cursor.execute(
            """
            UPDATE book_loans
            SET status = 'RETURNED',
                return_date = %s
            WHERE loan_id = %s
            """,
            (date.today(), loan_id)
        )

        # Restore available quantity
        cursor.execute(
            """
            UPDATE books
            SET available_copies = available_copies + 1
            WHERE book_id = %s
            """,
            (loan["book_id"],)
        )

        conn.commit()

        return True, "Book returned successfully!"

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


def get_user_loans(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                l.loan_id,
                b.title,
                b.author,
                l.borrow_date,
                l.due_date,
                l.return_date,
                l.status

            FROM book_loans l

            JOIN books b
            ON l.book_id = b.book_id

            WHERE l.user_id = %s

            ORDER BY l.loan_id DESC
            """,
            (user_id,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conn.close()


def get_all_loans():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                l.loan_id,
                u.full_name,
                u.email,
                b.title,
                l.borrow_date,
                l.due_date,
                l.return_date,
                l.status

            FROM book_loans l

            JOIN users u
            ON l.user_id = u.user_id

            JOIN books b
            ON l.book_id = b.book_id

            ORDER BY l.loan_id DESC
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conn.close()
