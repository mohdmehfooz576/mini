from database.db import get_connection


def create_election(
    name,
    description,
    start_date,
    end_date
):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor()

    query = """
        INSERT INTO elections
        (
            name,
            description,
            start_date,
            end_date
        )
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            name,
            description,
            start_date,
            end_date
        )
    )

    connection.commit()

    election_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return election_id


def get_all_elections():
    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM elections
        ORDER BY id DESC
    """

    cursor.execute(query)

    elections = cursor.fetchall()

    cursor.close()
    connection.close()

    return elections


def get_election_by_id(election_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM elections
        WHERE id = %s
    """

    cursor.execute(
        query,
        (election_id,)
    )

    election = cursor.fetchone()

    cursor.close()
    connection.close()

    return election


def update_election_status(
    election_id,
    status
):
    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    query = """
        UPDATE elections
        SET status = %s
        WHERE id = %s
    """

    cursor.execute(
        query,
        (
            status,
            election_id
        )
    )

    connection.commit()

    changed = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return changed