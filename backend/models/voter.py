
from database.db import get_connection


# ==========================================
# CREATE VOTER
# ==========================================

def create_voter(
    user_id,
    enrolment_no,
    mobile,
    department,
    year,
    status="Pending"
):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO voters (
                user_id,
                enrolment_no,
                mobile,
                department,
                year,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            enrolment_no,
            mobile,
            department,
            year,
            status
        ))

        voter_id = cursor.lastrowid
        connection.commit()
        return voter_id

    except Exception as error:
        connection.rollback()
        print("Create voter error:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET VOTER BY USER ID
# ==========================================

def get_voter_by_user_id(user_id):

    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM voters
            WHERE user_id = %s
        """, (user_id,))

        return cursor.fetchone()

    except Exception as error:
        print("Get voter error:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET ALL VOTERS
# ==========================================

def get_all_voters():

    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                voters.id,
                voters.user_id,
                voters.enrolment_no,
                voters.mobile,
                voters.department,
                voters.year,
                voters.status,
                voters.rejection_reason,
                voters.created_at,
                users.name,
                users.email
            FROM voters
            INNER JOIN users
                ON voters.user_id = users.id
            ORDER BY voters.created_at DESC
        """)

        return cursor.fetchall()

    except Exception as error:
        print("Get all voters error:", error)
        return []

    finally:
        cursor.close()
        connection.close()


# ==========================================
# UPDATE VOTER STATUS
# ==========================================

def update_voter_status(
    voter_id,
    status,
    rejection_reason=None
):

    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    try:
        if status == "Rejected":

            cursor.execute("""
                UPDATE voters
                SET
                    status = %s,
                    rejection_reason = %s
                WHERE id = %s
            """, (
                status,
                rejection_reason,
                voter_id
            ))

        else:

            cursor.execute("""
                UPDATE voters
                SET
                    status = %s,
                    rejection_reason = NULL
                WHERE id = %s
            """, (
                status,
                voter_id
            ))

        connection.commit()
        return cursor.rowcount > 0

    except Exception as error:
        connection.rollback()
        print("Update voter status error:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# ==========================================
# DELETE VOTER - VOTE PROTECTION
# ==========================================

def delete_voter(voter_id):

    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    try:
        # Lock voter record while checking and deleting.
        cursor.execute("""
            SELECT user_id
            FROM voters
            WHERE id = %s
            FOR UPDATE
        """, (voter_id,))

        result = cursor.fetchone()

        if not result:
            connection.rollback()
            return False

        user_id = result[0]

        # Check whether this voter has cast any vote.
        cursor.execute("""
            SELECT COUNT(*)
            FROM votes
            WHERE voter_id = %s
        """, (voter_id,))

        vote_count = cursor.fetchone()[0]

        if vote_count > 0:
            connection.rollback()
            print(
                f"Voter deletion blocked: voter {voter_id} "
                f"has {vote_count} vote(s)."
            )
            return False

        # Delete only if no vote exists.
        cursor.execute("""
            DELETE FROM users
            WHERE id = %s
        """, (user_id,))

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        connection.commit()
        return True

    except Exception as error:
        connection.rollback()
        print("Delete voter error:", error)
        return False

    finally:
        cursor.close()
        connection.close()
