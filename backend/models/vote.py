from database.db import get_connection


def has_voted(voter_id, election_id):
    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    query = """
        SELECT id
        FROM votes
        WHERE voter_id = %s
        AND election_id = %s
        LIMIT 1
    """

    cursor.execute(
        query,
        (
            voter_id,
            election_id
        )
    )

    vote = cursor.fetchone()

    cursor.close()
    connection.close()

    return vote is not None


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

        # Check that candidate belongs to this election
        cursor.execute(
            """
            SELECT id
            FROM candidates
            WHERE id = %s
            AND election_id = %s
            """,
            (
                candidate_id,
                election_id
            )
        )

        candidate = cursor.fetchone()

        if not candidate:
            return (
                False,
                "Candidate does not belong to this election"
            )

        # Check whether voter has already voted
        cursor.execute(
            """
            SELECT id
            FROM votes
            WHERE voter_id = %s
            AND election_id = %s
            LIMIT 1
            """,
            (
                voter_id,
                election_id
            )
        )

        existing_vote = cursor.fetchone()

        if existing_vote:
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

        # Increase candidate vote count
        cursor.execute(
            """
            UPDATE candidates
            SET vote_count = vote_count + 1
            WHERE id = %s
            """,
            (candidate_id,)
        )

        connection.commit()

        return (
            True,
            "Vote submitted successfully"
        )

    except Exception as error:

        connection.rollback()

        print(
            "Vote error:",
            error
        )

        return (
            False,
            "Vote could not be submitted"
        )

    finally:

        if cursor:
            cursor.close()

        connection.close()


def get_votes_by_voter(voter_id):
    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
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
    """

    cursor.execute(
        query,
        (voter_id,)
    )

    votes = cursor.fetchall()

    cursor.close()
    connection.close()

    return votes


def get_results_by_election(election_id):
    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            election_id,
            name,
            year_position,
            vote_count
        FROM candidates
        WHERE election_id = %s
        ORDER BY vote_count DESC, id ASC
    """

    cursor.execute(
        query,
        (election_id,)
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results