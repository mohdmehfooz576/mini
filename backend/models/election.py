
from datetime import date
from database.db import get_connection


VALID_STATUSES = {
    "Draft",
    "Published",
    "Active",
    "Stopped",
    "Completed",
    "Archived"
}


# ==========================================
# AUTOMATIC ELECTION STATUS UPDATE
# ==========================================

def stop_expired_elections():

    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    try:
        today = date.today()

        cursor.execute(
            """
            UPDATE elections
            SET status = 'Stopped'
            WHERE status IN ('Published', 'Active')
              AND end_date < %s
            """,
            (today,)
        )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# CREATE ELECTION
# ==========================================

def create_election(name, description, start_date, end_date):

    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO elections
            (name, description, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, 'Draft')
            """,
            (name, description, start_date, end_date)
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# UPDATE ELECTION DETAILS - DRAFT ONLY
# ==========================================

def update_election_details(
    election_id,
    name,
    description,
    start_date,
    end_date
):

    connection = get_connection()

    if not connection:
        raise Exception("Database connection failed")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, status
            FROM elections
            WHERE id = %s
            FOR UPDATE
            """,
            (election_id,)
        )

        election = cursor.fetchone()

        if not election:
            connection.rollback()
            return False

        if election["status"] != "Draft":
            connection.rollback()
            raise ValueError(
                "Only Draft elections can be modified"
            )

        if not name or not name.strip():
            connection.rollback()
            raise ValueError("Election name is required")

        if start_date > end_date:
            connection.rollback()
            raise ValueError(
                "End date cannot be before start date"
            )

        cursor.execute(
            """
            UPDATE elections
            SET
                name = %s,
                description = %s,
                start_date = %s,
                end_date = %s
            WHERE id = %s
              AND status = 'Draft'
            """,
            (
                name.strip(),
                description.strip(),
                start_date,
                end_date,
                election_id
            )
        )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET ALL ELECTIONS
# Archived elections excluded by default
# ==========================================

def get_all_elections(include_archived=False):

    stop_expired_elections()

    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    try:

        if include_archived:
            cursor.execute(
                """
                SELECT *
                FROM elections
                ORDER BY id DESC
                """
            )
        else:
            cursor.execute(
                """
                SELECT *
                FROM elections
                WHERE status != 'Archived'
                ORDER BY id DESC
                """
            )

        elections = cursor.fetchall()
        today = date.today()

        for election in elections:

            if election["status"] == "Published":

                if election["start_date"] <= today:
                    election["status"] = "Active"

            elif election["status"] == "Active":

                if today < election["start_date"]:
                    election["status"] = "Published"

        for election in elections:

            if election["status"] in ("Published", "Active"):

                cursor.execute(
                    """
                    UPDATE elections
                    SET status = %s
                    WHERE id = %s
                      AND status IN ('Published', 'Active')
                    """,
                    (
                        election["status"],
                        election["id"]
                    )
                )

        connection.commit()

        return elections

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET SINGLE ELECTION
# ==========================================

def get_election_by_id(election_id):

    stop_expired_elections()

    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM elections
            WHERE id = %s
            """,
            (election_id,)
        )

        election = cursor.fetchone()

        if not election:
            return None

        today = date.today()

        if election["status"] == "Published":

            if election["start_date"] <= today:
                election["status"] = "Active"

        elif election["status"] == "Active":

            if today < election["start_date"]:
                election["status"] = "Published"

        if election["status"] in ("Published", "Active"):

            cursor.execute(
                """
                UPDATE elections
                SET status = %s
                WHERE id = %s
                  AND status IN ('Published', 'Active')
                """,
                (
                    election["status"],
                    election_id
                )
            )

            connection.commit()

        return election

    finally:
        cursor.close()
        connection.close()


# ==========================================
# UPDATE ELECTION STATUS
# ==========================================

def update_election_status(election_id, status):

    if status not in VALID_STATUSES:
        raise ValueError("Invalid election status")

    stop_expired_elections()

    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM elections
            WHERE id = %s
            FOR UPDATE
            """,
            (election_id,)
        )

        election = cursor.fetchone()

        if not election:
            connection.rollback()
            return False

        if election["status"] in ("Archived", "Completed"):
            connection.rollback()
            raise ValueError(
                "Archived or completed elections cannot be reopened"
            )

        if status == "Published":

            if election["status"] != "Draft":
                connection.rollback()
                raise ValueError(
                    "Only draft elections can be published"
                )

        if status == "Active":

            if election["status"] not in ("Published", "Stopped"):
                connection.rollback()
                raise ValueError(
                    "Only published or stopped elections can be activated"
                )

            today = date.today()

            if not (
                election["start_date"] <= today <= election["end_date"]
            ):
                connection.rollback()
                raise ValueError(
                    "Voting can only be activated during the election period"
                )

        if status == "Stopped":

            if election["status"] not in ("Active", "Published"):
                connection.rollback()
                raise ValueError(
                    "Only published or active elections can be stopped"
                )

        cursor.execute(
            """
            UPDATE elections
            SET status = %s
            WHERE id = %s
            """,
            (status, election_id)
        )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# ARCHIVE ELECTION
# ==========================================

def archive_election(election_id):

    stop_expired_elections()

    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT status
            FROM elections
            WHERE id = %s
            FOR UPDATE
            """,
            (election_id,)
        )

        election = cursor.fetchone()

        if not election:
            connection.rollback()
            return False

        if election["status"] not in (
            "Published",
            "Stopped",
            "Completed"
        ):
            connection.rollback()
            raise ValueError(
                "Only scheduled, stopped or completed elections can be archived"
            )

        cursor.execute(
            """
            UPDATE elections
            SET status = 'Archived'
            WHERE id = %s
            """,
            (election_id,)
        )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# DELETE ELECTION
# ==========================================

def delete_election(election_id):

    connection = get_connection()

    if not connection:
        raise Exception("Database connection failed")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, name, status
            FROM elections
            WHERE id = %s
            FOR UPDATE
            """,
            (election_id,)
        )

        election = cursor.fetchone()

        if not election:
            connection.rollback()
            return None

        cursor.execute(
            """
            SELECT COUNT(*) AS total_votes
            FROM votes
            WHERE election_id = %s
            """,
            (election_id,)
        )

        total_votes = cursor.fetchone()["total_votes"]

        if total_votes > 0:

            cursor.execute(
                """
                UPDATE elections
                SET status = 'Archived'
                WHERE id = %s
                """,
                (election_id,)
            )

            connection.commit()

            return {
                "id": election["id"],
                "name": election["name"],
                "total_votes": total_votes,
                "archived": True
            }

        if election["status"] != "Draft":
            connection.rollback()
            raise ValueError(
                "Only draft elections without votes can be permanently deleted"
            )

        cursor.execute(
            """
            DELETE FROM elections
            WHERE id = %s
            """,
            (election_id,)
        )

        connection.commit()

        return {
            "id": election["id"],
            "name": election["name"],
            "total_votes": 0,
            "archived": False
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
