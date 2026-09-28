from database.db import get_connection


def get_user_by_email(email):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM users
        WHERE email = %s
    """

    cursor.execute(query, (email,))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


def get_user_by_id(user_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM users
        WHERE id = %s
    """

    cursor.execute(query, (user_id,))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


def create_user(name, email, password, role="voter"):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor()

    query = """
        INSERT INTO users
        (name, email, password, role)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (name, email, password, role)
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return user_id