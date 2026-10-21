from database.db import get_connection


# ==========================================
# GET ALL PUBLISHED NOTICES
# ==========================================

def get_published_notices():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                id,
                title,
                message,
                type,
                status,
                created_by,
                created_at,
                updated_at
            FROM notices
            WHERE status = 'Published'
            ORDER BY created_at DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


# ==========================================
# GET ALL NOTICES - ADMIN
# ==========================================

def get_all_notices():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                id,
                title,
                message,
                type,
                status,
                created_by,
                created_at,
                updated_at
            FROM notices
            ORDER BY created_at DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


# ==========================================
# GET NOTICE BY ID
# ==========================================

def get_notice_by_id(notice_id):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                id,
                title,
                message,
                type,
                status,
                created_by,
                created_at,
                updated_at
            FROM notices
            WHERE id = %s
        """

        cursor.execute(
            query,
            (notice_id,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        connection.close()


# ==========================================
# CREATE NOTICE
# ==========================================

def create_notice(
    title,
    message,
    notice_type,
    created_by
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO notices
            (
                title,
                message,
                type,
                status,
                created_by
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'Published',
                %s
            )
        """

        cursor.execute(
            query,
            (
                title,
                message,
                notice_type,
                created_by
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        cursor.close()
        connection.close()


# ==========================================
# UPDATE NOTICE
# ==========================================

def update_notice(
    notice_id,
    title,
    message,
    notice_type,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        query = """
            UPDATE notices
            SET
                title = %s,
                message = %s,
                type = %s,
                status = %s
            WHERE id = %s
        """

        cursor.execute(
            query,
            (
                title,
                message,
                notice_type,
                status,
                notice_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        cursor.close()
        connection.close()


# ==========================================
# DELETE NOTICE
# ==========================================

def delete_notice(notice_id):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        query = """
            DELETE FROM notices
            WHERE id = %s
        """

        cursor.execute(
            query,
            (notice_id,)
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        cursor.close()
        connection.close()