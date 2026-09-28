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

@admin_routes.route(
    "/stats",
    methods=["GET"]
)
@admin_required
def dashboard_stats():

    connection = get_connection()

    if not connection:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    stats = {}

    # Total voters
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM voters
        """
    )

    stats["total_voters"] = (
        cursor.fetchone()["total"]
    )

    # Approved voters
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM voters
        WHERE status = 'Approved'
        """
    )

    stats["approved_voters"] = (
        cursor.fetchone()["total"]
    )

    # Pending voters
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM voters
        WHERE status = 'Pending'
        """
    )

    stats["pending_voters"] = (
        cursor.fetchone()["total"]
    )

    # Rejected voters
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM voters
        WHERE status = 'Rejected'
        """
    )

    stats["rejected_voters"] = (
        cursor.fetchone()["total"]
    )

    # Total elections
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM elections
        """
    )

    stats["total_elections"] = (
        cursor.fetchone()["total"]
    )

    # Active elections
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM elections
        WHERE status = 'Active'
        """
    )

    stats["active_elections"] = (
        cursor.fetchone()["total"]
    )

    # Stopped elections
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM elections
        WHERE status = 'Stopped'
        """
    )

    stats["stopped_elections"] = (
        cursor.fetchone()["total"]
    )

    # Total votes
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM votes
        """
    )

    stats["total_votes"] = (
        cursor.fetchone()["total"]
    )

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "stats": stats
    }), 200


# ==========================================
# CHANGE VOTER STATUS
# ==========================================

@admin_routes.route(
    "/voters/<int:voter_id>/status",
    methods=["PUT"]
)
@admin_required
def change_voter_status(voter_id):

    data = request.get_json() or {}

    status = data.get(
        "status"
    )

    allowed_statuses = [
        "Pending",
        "Approved",
        "Rejected"
    ]

    if status not in allowed_statuses:

        return jsonify({
            "success": False,
            "message": (
                "Invalid voter status"
            )
        }), 400

    changed = update_voter_status(
        voter_id,
        status
    )

    if not changed:

        return jsonify({
            "success": False,
            "message": "Voter not found"
        }), 404

    return jsonify({
        "success": True,
        "message": (
            f"Voter status changed to {status}"
        )
    }), 200


# ==========================================
# DELETE VOTER
# ==========================================

@admin_routes.route(
    "/voters/<int:voter_id>",
    methods=["DELETE"]
)
@admin_required
def remove_voter(voter_id):

    deleted = delete_voter(
        voter_id
    )

    if not deleted:

        return jsonify({
            "success": False,
            "message": "Voter not found"
        }), 404

    return jsonify({
        "success": True,
        "message": (
            "Voter deleted successfully"
        )
    }), 200