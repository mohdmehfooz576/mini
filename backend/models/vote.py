
from database.db import get_connection


# ==========================================
# CHECK WHETHER VOTER HAS VOTED
# ==========================================

def has_voted(voter_id, election_id):

    connection = get_connection()

    if not connection:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM votes
            WHERE voter_id = %s
            AND election_id = %s
            LIMIT 1
            """,
            (voter_id, election_id)
        )

        return cursor.fetchone() is not None

    except Exception as error:

        print("Has voted error:", error)
        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# CREATE VOTE
# ==========================================

def create_vote(
    voter_id,
    election_id,
    candidate_id
):

    connection = get_connection()

    if not connection:
        return False, "Database connection failed"

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # Check candidate belongs to this election
        cursor.execute(
            """
            SELECT id
            FROM candidates
            WHERE id = %s
            AND election_id = %s
            """,
            (candidate_id, election_id)
        )

        candidate = cursor.fetchone()

        if not candidate:

            connection.rollback()

            return (
                False,
                "Candidate does not belong to this election"
            )

        # Check existing vote
        cursor.execute(
            """
            SELECT id
            FROM votes
            WHERE voter_id = %s
            AND election_id = %s
            LIMIT 1
            """,
            (voter_id, election_id)
        )

        existing_vote = cursor.fetchone()

        if existing_vote:

            connection.rollback()

            return (
                False,
                "You have already voted in this election"
            )

        # Insert vote
        cursor.execute(
            """
            INSERT INTO votes
            (
                voter_id,
                election_id,
                candidate_id
            )
            VALUES (%s, %s, %s)
            """,
            (
                voter_id,
                election_id,
                candidate_id
            )
        )

        # Update candidate vote count
        cursor.execute(
            """
            UPDATE candidates
            SET vote_count = vote_count + 1
            WHERE id = %s
            AND election_id = %s
            """,
            (
                candidate_id,
                election_id
            )
        )

        connection.commit()

        return (
            True,
            "Vote submitted successfully"
        )

    except Exception as error:

        connection.rollback()

        print("Vote error:", error)

        # Duplicate database entry protection
        if getattr(error, "errno", None) == 1062:

            return (
                False,
                "You have already voted in this election"
            )

        return (
            False,
            "Vote could not be submitted"
        )

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# GET VOTES BY VOTER
# ==========================================

def get_votes_by_voter(voter_id):

    connection = get_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                votes.id,
                votes.voter_id,
                votes.election_id,
                votes.candidate_id,
                votes.voted_at,
                elections.name AS election_name,
                candidates.name AS candidate_name

            FROM votes

            JOIN elections
                ON votes.election_id = elections.id

            JOIN candidates
                ON votes.candidate_id = candidates.id

            WHERE votes.voter_id = %s

            ORDER BY votes.voted_at DESC
            """,
            (voter_id,)
        )

        return cursor.fetchall()

    except Exception as error:

        print("Get voter votes error:", error)
        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# GET ELECTION RESULTS
# ==========================================

def get_results_by_election(election_id):

    connection = get_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                election_id,
                name,
                year_position,
                photo,
                vote_count

            FROM candidates

            WHERE election_id = %s

            ORDER BY vote_count DESC, id ASC
            """,
            (election_id,)
        )

        return cursor.fetchall()

    except Exception as error:

        print("Get election results error:", error)
        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()
