
from flask import Blueprint, request, jsonify

from database.db import get_connection

from models.voter import (
    update_voter_status,
    delete_voter
)

from utils.auth import admin_required


admin_routes = Blueprint(
    "admin_routes",
    __name__,
    url_prefix="/api/admin"
)


# ==========================================
# ADMIN DASHBOARD STATISTICS
# ==========================================

@admin_routes.route("/stats", methods=["GET"])
@admin_required
def dashboard_stats():

    connection = get_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        stats = {}

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM voters
        """)
        stats["total_voters"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM voters
            WHERE status = 'Approved'
        """)
        stats["approved_voters"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM voters
            WHERE status = 'Pending'
        """)
        stats["pending_voters"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM voters
            WHERE status = 'Rejected'
        """)
        stats["rejected_voters"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM elections
        """)
        stats["total_elections"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM elections
            WHERE status = 'Active'
        """)
        stats["active_elections"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM elections
            WHERE status = 'Stopped'
        """)
        stats["stopped_elections"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM votes
        """)
        stats["total_votes"] = cursor.fetchone()["total"]

        return jsonify({
            "success": True,
            "stats": stats
        }), 200

    except Exception as error:
        print("Dashboard stats error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load dashboard statistics"
        }), 500

    finally:
        cursor.close()
        connection.close()


# ==========================================
# CHANGE VOTER STATUS
# ==========================================

@admin_routes.route(
    "/voters/<int:voter_id>/status",
    methods=["PUT"]
)
@admin_required
def change_voter_status(voter_id):

    data = request.get_json(silent=True) or {}

    status = data.get("status")
    rejection_reason = data.get("rejection_reason")

    allowed_statuses = [
        "Pending",
        "Approved",
        "Rejected"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid voter status"
        }), 400

    if status == "Rejected":

        if not isinstance(rejection_reason, str):
            return jsonify({
                "success": False,
                "message": "Please provide a rejection reason"
            }), 400

        rejection_reason = rejection_reason.strip()

        if not rejection_reason:
            return jsonify({
                "success": False,
                "message": "Rejection reason cannot be empty"
            }), 400

    else:
        rejection_reason = None

    changed = update_voter_status(
        voter_id,
        status,
        rejection_reason
    )

    if not changed:
        return jsonify({
            "success": False,
            "message": "Voter not found or status could not be updated"
        }), 404

    response = {
        "success": True,
        "message": f"Voter status changed to {status}",
        "status": status
    }

    if status == "Rejected":
        response["rejection_reason"] = rejection_reason

    return jsonify(response), 200


# ==========================================
# DELETE VOTER - PROTECT CAST VOTES
# ==========================================

@admin_routes.route(
    "/voters/<int:voter_id>",
    methods=["DELETE"]
)
@admin_required
def remove_voter(voter_id):

    connection = get_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = connection.cursor()

    try:
        # Check whether voter exists.
        cursor.execute("""
            SELECT id
            FROM voters
            WHERE id = %s
        """, (voter_id,))

        voter = cursor.fetchone()

        if not voter:
            return jsonify({
                "success": False,
                "message": "Voter not found"
            }), 404

        # Check whether voter has already cast a vote.
        cursor.execute("""
            SELECT COUNT(*)
            FROM votes
            WHERE voter_id = %s
        """, (voter_id,))

        vote_count = cursor.fetchone()[0]

        if vote_count > 0:
            return jsonify({
                "success": False,
                "message": (
                    "This voter has already voted and "
                    "cannot be deleted. Voting records "
                    "and receipts are protected."
                ),
                "votes_found": vote_count
            }), 409

    except Exception as error:
        print("Voter deletion check error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to verify voter voting records"
        }), 500

    finally:
        cursor.close()
        connection.close()

    # Model performs its own vote-protection check as well.
    deleted = delete_voter(voter_id)

    if not deleted:
        return jsonify({
            "success": False,
            "message": (
                "Voter could not be deleted. "
                "The voter may have a protected voting record."
            )
        }), 409

    return jsonify({
        "success": True,
        "message": "Voter deleted successfully"
    }), 200
