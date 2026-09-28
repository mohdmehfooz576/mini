from database.db import get_connection


def create_candidate(
    election_id,
    name,
    year_position
):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor()

    query = """
        INSERT INTO candidates
        (
            election_id,
            name,
            year_position
        )
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (
            election_id,
            name,
            year_position
        )
    )

    connection.commit()

    candidate_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return candidate_id


def get_candidates_by_election(election_id):
    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM candidates
        WHERE election_id = %s
        ORDER BY id ASC
    """

    cursor.execute(
        query,
        (election_id,)
    )

    candidates = cursor.fetchall()

    cursor.close()
    connection.close()

    return candidates


def get_candidate_by_id(candidate_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM candidates
        WHERE id = %s
    """

    cursor.execute(
        query,
        (candidate_id,)
    )

    candidate = cursor.fetchone()

    cursor.close()
    connection.close()

    return candidate


def delete_candidate(candidate_id):
    connection = get_connection()

    if not connection:
        return False, "Database connection failed"

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT vote_count
        FROM candidates
        WHERE id = %s
        """,
        (candidate_id,)
    )

    candidate = cursor.fetchone()

    if not candidate:
        cursor.close()
        connection.close()

        return False, "Candidate not found"

    if candidate["vote_count"] > 0:
        cursor.close()
        connection.close()

        return (
            False,
            "Candidate cannot be deleted after receiving votes"
        )

    cursor.close()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM candidates
        WHERE id = %s
        """,
        (candidate_id,)
    )

    connection.commit()

    deleted = cursor.rowcount > 0

    cursor.close()
    connection.close()

    if deleted:
        return True, "Candidate deleted"

    return False, "Candidate could not be deleted"