from database.db import get_connection


def get_user_by_email(email):
    connection = get_connection()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        return cursor.fetchone()

    except Exception as error:
        print("Get user by email error:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_user_by_id(user_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )

        return cursor.fetchone()

    except Exception as error:
        print("Get user by ID error:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def create_user(name, email, password, role="voter"):
    connection = get_connection()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, password, role)
        )

        connection.commit()
        return cursor.lastrowid

    except Exception as error:
        connection.rollback()
        print("Create user error:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def update_user_password(user_id, password_hash):
    connection = get_connection()

    if not connection:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (password_hash, user_id)
        )

        connection.commit()
        return cursor.rowcount == 1

    except Exception as error:
        connection.rollback()
        print("Update user password error:", error)
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()


# SECURITY QUESTION FUNCTIONS

def update_security_question(user_id, question, answer_hash):
    connection = get_connection()

    if not connection:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET security_question = %s,
                security_answer_hash = %s
            WHERE id = %s
            """,
            (question, answer_hash, user_id)
        )

        connection.commit()
        return cursor.rowcount == 1

    except Exception as error:
        connection.rollback()
        print("Update security question error:", error)
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_security_question_by_email(email):
    connection = get_connection()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, security_question
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        return cursor.fetchone()

    except Exception as error:
        print("Get security question error:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_security_answer_hash(user_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT security_answer_hash
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        result = cursor.fetchone()

        return result["security_answer_hash"] if result else None

    except Exception as error:
        print("Get security answer hash error:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()