from database.db import get_connection


def create_voter(
    user_id,
    roll_no,
    mobile,
    department,
    year
):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor()

    query = """
        INSERT INTO voters
        (
            user_id,
            roll_no,
            mobile,
            department,
            year
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            user_id,
            roll_no,
            mobile,
            department,
            year
        )
    )

    connection.commit()

    voter_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return voter_id


def get_voter_by_user_id(user_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            voters.*,
            users.name,
            users.email
        FROM voters
        JOIN users
            ON voters.user_id = users.id
        WHERE voters.user_id = %s
    """

    cursor.execute(
        query,
        (user_id,)
    )

    voter = cursor.fetchone()

    cursor.close()
    connection.close()

    return voter


def get_all_voters():
    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            voters.id,
            voters.user_id,
            voters.roll_no,
            voters.mobile,
            voters.department,
            voters.year,
            voters.status,
            voters.created_at,
            users.name,
            users.email
        FROM voters
        JOIN users
            ON voters.user_id = users.id
        ORDER BY voters.id DESC
    """

    cursor.execute(query)

    voters = cursor.fetchall()

    cursor.close()
    connection.close()

    return voters


def update_voter_status(voter_id, status):
    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    query = """
        UPDATE voters
        SET status = %s
        WHERE id = %s
    """

    cursor.execute(
        query,
        (
            status,
            voter_id
        )
    )

    connection.commit()

    changed = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return changed


def delete_voter(voter_id):
    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT user_id
        FROM voters
        WHERE id = %s
        """,
        (voter_id,)
    )

    voter = cursor.fetchone()

    cursor.close()

    if not voter:
        connection.close()
        return False

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM users
        WHERE id = %s
        """,
        (voter["user_id"],)
    )

    connection.commit()

    deleted = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return deleted