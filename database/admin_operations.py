
# database/admin_operations.py

from database.connection import get_connection


def list_users():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT user_id, full_name, email,
                   role, is_active, created_at
            FROM users
            ORDER BY user_id DESC
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conn.close()


def set_user_active(user_id, active):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # Only ordinary user accounts can be disabled here
        cursor.execute(
            """
            UPDATE users
            SET is_active = %s
            WHERE user_id = %s
            AND role = 'user'
            """,
            (active, user_id)
        )

        conn.commit()

        return cursor.rowcount == 1

    finally:

        cursor.close()
        conn.close()
