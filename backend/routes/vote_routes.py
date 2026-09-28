from datetime import date

from flask import Blueprint, request, jsonify

from models.voter import get_voter_by_user_id

from models.election import get_election_by_id

from models.vote import (
    create_vote,
    has_voted,
    get_votes_by_voter
)

from utils.auth import token_required


vote_routes = Blueprint(
    "vote_routes",
    __name__,
    url_prefix="/api/votes"
)


# ==========================================
# CAST VOTE
# ==========================================

@vote_routes.route(
    "/cast",
    methods=["POST"]
)
@token_required
def cast_vote():

    # Only voters can vote
    if request.user["role"] != "voter":

        return jsonify({
            "success": False,
            "message": "Only voters can vote"
        }), 403

    # Get voter profile
    voter = get_voter_by_user_id(
        request.user["id"]
    )

    if not voter:

        return jsonify({
            "success": False,
            "message": "Voter profile not found"
        }), 404

    # Voter must be approved
    if voter["status"] != "Approved":

        return jsonify({
            "success": False,
            "message": (
                "Your voter account is not approved"
            )
        }), 403

    data = request.get_json() or {}

    election_id = data.get(
        "election_id"
    )

    candidate_id = data.get(
        "candidate_id"
    )

    if not election_id or not candidate_id:

        return jsonify({
            "success": False,
            "message": (
                "Election ID and candidate ID "
                "are required"
            )
        }), 400

    # Get election
    election = get_election_by_id(
        election_id
    )

    if not election:

        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    # Election must be active
    if election["status"] != "Active":

        return jsonify({
            "success": False,
            "message": "Election is stopped"
        }), 403

    # Check voting dates
    today = date.today()

    if today < election["start_date"]:

        return jsonify({
            "success": False,
            "message": (
                "Voting has not started yet"
            )
        }), 403

    if today > election["end_date"]:

        return jsonify({
            "success": False,
            "message": (
                "Voting period has ended"
            )
        }), 403

    # One vote per voter per election
    if has_voted(
        voter["id"],
        election_id
    ):

        return jsonify({
            "success": False,
            "message": (
                "You have already voted "
                "in this election"
            )
        }), 409

    # Create vote
    success, message = create_vote(
        voter["id"],
        election_id,
        candidate_id
    )

    if not success:

        return jsonify({
            "success": False,
            "message": message
        }), 400

    return jsonify({
        "success": True,
        "message": message
    }), 201


# ==========================================
# GET MY VOTES
# ==========================================

@vote_routes.route(
    "/my-votes",
    methods=["GET"]
)
@token_required
def my_votes():

    voter = get_voter_by_user_id(
        request.user["id"]
    )

    if not voter:

        return jsonify({
            "success": False,
            "message": "Voter profile not found"
        }), 404

    votes = get_votes_by_voter(
        voter["id"]
    )

    return jsonify({
        "success": True,
        "votes": votes
    }), 200