
from database.db import get_connection


# ==========================================
# CREATE CANDIDATE
# ==========================================

def create_candidate(
    election_id,
    name,
    year_position,
    photo=None
):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor()

    try:
        query = """
            INSERT INTO candidates
            (
                election_id,
                name,
                year_position,
                photo
            )
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                election_id,
                name,
                year_position,
                photo
            )
        )

        connection.commit()

        candidate_id = cursor.lastrowid

        return candidate_id

    except Exception as error:
        connection.rollback()
        print("Create candidate error:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET CANDIDATES BY ELECTION
# ==========================================

def get_candidates_by_election(election_id):

    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
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

        return candidates

    except Exception as error:
        print("Get candidates error:", error)
        return []

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET CANDIDATE BY ID
# ==========================================

def get_candidate_by_id(candidate_id):

    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
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

        return candidate

    except Exception as error:
        print("Get candidate error:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# UPDATE CANDIDATE PHOTO
# ==========================================

def update_candidate_photo(
    candidate_id,
    photo
):

    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    try:
        query = """
            UPDATE candidates
            SET photo = %s
            WHERE id = %s
        """

        cursor.execute(
            query,
            (
                photo,
                candidate_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception as error:
        connection.rollback()
        print("Update candidate photo error:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# ==========================================
# DELETE CANDIDATE
# ==========================================

def delete_candidate(candidate_id):

    connection = get_connection()

    if not connection:
        return False, "Database connection failed"

    cursor = connection.cursor(dictionary=True)

    try:
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
            return False, "Candidate not found"

        if candidate["vote_count"] > 0:
            return (
                False,
                "Candidate cannot be deleted after receiving votes"
            )

        cursor.execute(
            """
            DELETE FROM candidates
            WHERE id = %s
            """,
            (candidate_id,)
        )

        connection.commit()

        if cursor.rowcount > 0:
            return True, "Candidate deleted"

        return False, "Candidate could not be deleted"

    except Exception as error:
        connection.rollback()
        print("Delete candidate error:", error)
        return False, "Candidate deletion failed"

    finally:
        cursor.close()
        connection.close()
