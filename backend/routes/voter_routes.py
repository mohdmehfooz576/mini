
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

@voter_routes.route(
    "/me",
    methods=["GET"]
)
@token_required
def my_profile():

    voter = get_voter_by_user_id(
        request.user["id"]
    )

    if not voter:
        return jsonify({
            "success": False,
            "message": "Voter profile not found"
        }), 404

    return jsonify({
        "success": True,
        "voter": voter
    }), 200


# ==========================================
# GET ALL VOTERS
# ADMIN ONLY
# ==========================================

@voter_routes.route(
    "/",
    methods=["GET"]
)
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

@voter_routes.route(
    "/check-status",
    methods=["POST"]
)
def check_registration_status():

    data = request.get_json(silent=True) or {}

    roll_no = data.get("roll_no")
    email = data.get("email")

    if not isinstance(roll_no, str) or not isinstance(email, str):
        return jsonify({
            "success": False,
            "message": "Roll number and registered email are required"
        }), 400

    roll_no = roll_no.strip()
    email = email.strip()

    if not roll_no or not email:
        return jsonify({
            "success": False,
            "message": "Please enter both roll number and registered email"
        }), 400

    connection = get_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                voters.roll_no,
                voters.status,
                voters.rejection_reason,
                users.name,
                users.email
            FROM voters
            JOIN users
                ON voters.user_id = users.id
            WHERE voters.roll_no = %s
              AND LOWER(users.email) = LOWER(%s)
            LIMIT 1
            """,
            (roll_no, email)
        )

        voter = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if not voter:
        return jsonify({
            "success": False,
            "message": "No registration matched those details. Check your roll number and registered email."
        }), 404

    return jsonify({
        "success": True,
        "message": "Registration status found",
        "status": voter["status"],
        "rejection_reason": (
            voter["rejection_reason"]
            if voter["status"] == "Rejected"
            else None
        )
    }), 200
