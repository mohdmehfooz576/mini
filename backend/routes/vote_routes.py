
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
            "message": "Your voter account is not approved"
        }), 403

    data = request.get_json(silent=True) or {}

    election_id = data.get("election_id")
    candidate_id = data.get("candidate_id")

    if not election_id or not candidate_id:

        return jsonify({
            "success": False,
            "message": (
                "Election ID and candidate ID are required"
            )
        }), 400

    # Validate election ID
    try:
        election_id = int(election_id)
        candidate_id = int(candidate_id)

        if election_id <= 0 or candidate_id <= 0:
            raise ValueError

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "Invalid election or candidate ID"
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

    today = date.today()

    # ======================================
    # CHECK ELECTION EXPIRY FIRST
    # ======================================

    if today > election["end_date"]:

        return jsonify({
            "success": False,
            "message": (
                "Voting period has ended. "
                "This election is now stopped."
            )
        }), 403

    # Voting cannot start before start date
    if today < election["start_date"]:

        return jsonify({
            "success": False,
            "message": "Voting has not started yet"
        }), 403

    # Election must be Active
    if election["status"] != "Active":

        return jsonify({
            "success": False,
            "message": "Election is not currently active"
        }), 403

    # ======================================
    # ONE VOTE PER VOTER PER ELECTION
    # ======================================

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

    # ======================================
    # CREATE VOTE
    # ======================================

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

    # Preserve database wall-clock time
    # for existing vote receipts.
    for vote in votes:

        voted_at = vote.get("voted_at")

        if voted_at is not None:

            vote["voted_at"] = voted_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    return jsonify({
        "success": True,
        "votes": votes
    }), 200
