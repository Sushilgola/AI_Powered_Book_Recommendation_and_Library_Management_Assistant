
# authentication/auth.py

import bcrypt
import mysql.connector

from database.connection import get_connection


def register_user(name, email, password):

    if not name.strip() or not email.strip() or not password:
        return False, "All fields are required."

    if len(password.encode("utf-8")) > 72:
        return False, "Password is too long."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:

        query = """
            INSERT INTO users
            (full_name, email, password_hash, role)
            VALUES (%s, %s, %s, 'user')
        """

        cursor.execute(
            query,
            (name.strip(), email.strip().lower(), hashed_password)
        )

        conn.commit()

        return True, "Registration successful!"

    except mysql.connector.IntegrityError:

        conn.rollback()
        return False, "Email already registered."

    finally:

        cursor.close()
        conn.close()


def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s AND is_active = TRUE
            """,
            (email.strip().lower(),)
        )

        user = cursor.fetchone()

        if user:

            valid = bcrypt.checkpw(
                password.encode("utf-8"),
                user["password_hash"].encode("utf-8")
            )

            if valid:

                user.pop("password_hash")

                return user

        return None

    finally:

        cursor.close()
        conn.close()
