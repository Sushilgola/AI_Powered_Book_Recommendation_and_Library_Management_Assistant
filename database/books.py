
# database/books.py

from database.connection import get_connection


def list_books(search="", include_inactive=False):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if not include_inactive:
        query += " AND is_active = TRUE"

    if search:
        query += " AND (title LIKE %s OR author LIKE %s)"
        value = f"%{search}%"
        params.extend([value, value])

    query += " ORDER BY title"

    try:

        cursor.execute(query, params)
        return cursor.fetchall()

    finally:

        cursor.close()
        conn.close()


def add_book(title, author, isbn, description,
             total_copies, ebook_url):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO books
            (title, author, isbn, description,
             total_copies, available_copies, ebook_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                title,
                author,
                isbn or None,
                description,
                total_copies,
                total_copies,
                ebook_url or None
            )
        )

        conn.commit()

        return True, "Book added successfully!"

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


def update_book(book_id, title, author,
                description, total_copies, ebook_url):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        conn.start_transaction()

        cursor.execute(
            """
            SELECT total_copies, available_copies
            FROM books
            WHERE book_id = %s
            FOR UPDATE
            """,
            (book_id,)
        )

        current = cursor.fetchone()

        if not current:
            conn.rollback()
            return False, "Book not found."

        borrowed_copies = (
            current["total_copies"] -
            current["available_copies"]
        )

        if total_copies < borrowed_copies:
            conn.rollback()
            return False, "Total copies cannot be less than copies currently borrowed."

        available_copies = total_copies - borrowed_copies

        cursor.execute(
            """
            UPDATE books
            SET title = %s,
                author = %s,
                description = %s,
                total_copies = %s,
                available_copies = %s,
                ebook_url = %s
            WHERE book_id = %s
            """,
            (
                title,
                author,
                description,
                total_copies,
                available_copies,
                ebook_url or None,
                book_id
            )
        )

        conn.commit()

        return True, "Book updated successfully!"

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


def set_book_active(book_id, active):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE books
            SET is_active = %s
            WHERE book_id = %s
            """,
            (active, book_id)
        )

        conn.commit()

    finally:

        cursor.close()
        conn.close()
