
from flask import Blueprint, jsonify, request

from utils.auth import (
    token_required,
    admin_required
)

from database.db import get_connection

from models.voter import (
    get_voter_by_user_id,
    get_all_voters
)


voter_routes = Blueprint(
    "voter_routes",
    __name__,
    url_prefix="/api/voters"
)


# ==========================================
# GET LOGGED-IN VOTER PROFILE
# ==========================================

@voter_routes.route("/me", methods=["GET"])
@token_required
def my_profile():

    if request.user.get("role") != "voter":
        return jsonify({
            "success": False,
            "message": "Only voters can access this profile"
        }), 403

    connection = get_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                users.id,
                users.name,
                users.email,
                voters.enrolment_no,
                voters.mobile,
                voters.department,
                voters.year,
                voters.status
            FROM voters
            INNER JOIN users
                ON voters.user_id = users.id
            WHERE users.id = %s
            LIMIT 1
            """,
            (request.user["id"],)
        )

        voter = cursor.fetchone()

        if not voter:
            return jsonify({
                "success": False,
                "message": "Voter profile not found"
            }), 404

        return jsonify({
            "success": True,
            "voter": voter
        }), 200

    except Exception as error:
        print("Voter profile error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load voter profile"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# UPDATE LOGGED-IN VOTER PROFILE
# VOTER CAN UPDATE ONLY THEIR OWN DETAILS
# ==========================================

@voter_routes.route("/me", methods=["PUT"])
@token_required
def update_my_profile():

    if request.user.get("role") != "voter":
        return jsonify({
            "success": False,
            "message": "Only voters can update their profile"
        }), 403

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    enrolment_no = data.get("enrolment_no")
    mobile = data.get("mobile")
    department = data.get("department")
    year = data.get("year")

    fields = {
        "Name": name,
        "Enrolment Number": enrolment_no,
        "Mobile": mobile,
        "Department": department,
        "Year": year
    }

    for field_name, value in fields.items():
        if not isinstance(value, str) or not value.strip():
            return jsonify({
                "success": False,
                "message": f"{field_name} is required"
            }), 400

    name = name.strip()
    enrolment_no = enrolment_no.strip().upper()
    mobile = mobile.strip()
    department = department.strip()
    year = year.strip()

    if len(name) > 100:
        return jsonify({
            "success": False,
            "message": "Name must not exceed 100 characters"
        }), 400

    if len(enrolment_no) > 50:
        return jsonify({
            "success": False,
            "message": "Enrolment number is too long"
        }), 400

    if len(mobile) > 20:
        return jsonify({
            "success": False,
            "message": "Mobile number is too long"
        }), 400

    if len(department) > 100 or len(year) > 30:
        return jsonify({
            "success": False,
            "message": "Department or year value is too long"
        }), 400

    connection = get_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        user_id = request.user["id"]

        # Check that the voter profile exists
        cursor.execute(
            """
            SELECT id
            FROM voters
            WHERE user_id = %s
            LIMIT 1
            """,
            (user_id,)
        )

        voter = cursor.fetchone()

        if not voter:
            return jsonify({
                "success": False,
                "message": "Voter profile not found"
            }), 404

        # Check duplicate enrolment number
        cursor.execute(
            """
            SELECT id
            FROM voters
            WHERE UPPER(enrolment_no) = %s
              AND user_id != %s
            LIMIT 1
            """,
            (enrolment_no, user_id)
        )

        duplicate = cursor.fetchone()

        if duplicate:
            return jsonify({
                "success": False,
                "message": "This enrolment number is already registered"
            }), 409

        # Update user name
        cursor.execute(
            """
            UPDATE users
            SET name = %s
            WHERE id = %s
            """,
            (name, user_id)
        )

        # Update voter details
        cursor.execute(
            """
            UPDATE voters
            SET
                enrolment_no = %s,
                mobile = %s,
                department = %s,
                year = %s
            WHERE user_id = %s
            """,
            (
                enrolment_no,
                mobile,
                department,
                year,
                user_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Profile updated successfully"
        }), 200

    except Exception as error:
        connection.rollback()
        print("Update voter profile error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to update profile"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# GET ALL VOTERS
# ADMIN ONLY
# ==========================================

@voter_routes.route("/", methods=["GET"])
@admin_required
def all_voters():

    voters = get_all_voters()

    return jsonify({
        "success": True,
        "voters": voters
    }), 200


# ==========================================
# CHECK REGISTRATION STATUS
# PUBLIC STATUS LOOKUP
# ==========================================

@voter_routes.route("/check-status", methods=["POST"])
def check_registration_status():

    data = request.get_json(silent=True) or {}

    enrolment_no = (
        data.get("enrolment_no")
        or data.get("roll_no")
    )

    email = data.get("email")

    if not isinstance(enrolment_no, str) or not isinstance(email, str):
        return jsonify({
            "success": False,
            "message": "Enrolment number and registered email are required"
        }), 400

    enrolment_no = enrolment_no.strip().upper()
    email = email.strip()

    if not enrolment_no or not email:
        return jsonify({
            "success": False,
            "message": "Please enter both enrolment number and registered email"
        }), 400

    connection = get_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                voters.enrolment_no,
                voters.status,
                voters.rejection_reason,
                users.name,
                users.email
            FROM voters
            JOIN users
                ON voters.user_id = users.id
            WHERE UPPER(voters.enrolment_no) = %s
              AND LOWER(users.email) = LOWER(%s)
            LIMIT 1
            """,
            (enrolment_no, email)
        )

        voter = cursor.fetchone()

    except Exception as error:
        print("Registration status error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to check registration status"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()

    if not voter:
        return jsonify({
            "success": False,
            "message": "No registration matched those details. Check your enrolment number and registered email."
        }), 404

    return jsonify({
        "success": True,
        "message": "Registration status found",
        "enrolment_no": voter["enrolment_no"],
        "name": voter["name"],
        "status": voter["status"],
        "rejection_reason": (
            voter["rejection_reason"]
            if voter["status"] == "Rejected"
            else None
        )
    }), 200
