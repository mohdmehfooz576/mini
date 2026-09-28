from flask import Blueprint, jsonify, request

from utils.auth import (
    token_required,
    admin_required
)

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