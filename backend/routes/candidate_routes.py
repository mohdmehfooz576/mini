from flask import Blueprint, request, jsonify

from models.candidate import (
    create_candidate,
    get_candidates_by_election,
    get_candidate_by_id,
    delete_candidate
)

from models.election import (
    get_election_by_id
)

from utils.auth import admin_required


candidate_routes = Blueprint(
    "candidate_routes",
    __name__,
    url_prefix="/api/candidates"
)


# ==========================================
# GET CANDIDATES BY ELECTION
# ==========================================

@candidate_routes.route(
    "/election/<int:election_id>",
    methods=["GET"]
)
def candidates(election_id):

    election = get_election_by_id(
        election_id
    )

    if not election:

        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    candidates_list = (
        get_candidates_by_election(
            election_id
        )
    )

    return jsonify({
        "success": True,
        "candidates": candidates_list
    }), 200


# ==========================================
# ADD CANDIDATE
# ADMIN ONLY
# ==========================================

@candidate_routes.route(
    "/",
    methods=["POST"]
)
@admin_required
def add_candidate():

    data = request.get_json() or {}

    election_id = data.get(
        "election_id"
    )

    name = str(
        data.get("name", "")
    ).strip()

    year_position = str(
        data.get("year_position", "")
    ).strip()

    if not election_id or not name:

        return jsonify({
            "success": False,
            "message": (
                "Election and candidate "
                "name are required"
            )
        }), 400

    election = get_election_by_id(
        election_id
    )

    if not election:

        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    # Prevent duplicate candidate names
    candidates_list = (
        get_candidates_by_election(
            election_id
        )
    )

    for candidate in candidates_list:

        if (
            candidate["name"].strip().lower()
            == name.lower()
        ):

            return jsonify({
                "success": False,
                "message": (
                    "Candidate already exists"
                )
            }), 409

    try:

        candidate_id = create_candidate(
            election_id,
            name,
            year_position
        )

        if not candidate_id:

            return jsonify({
                "success": False,
                "message": (
                    "Candidate could not be added"
                )
            }), 500

        return jsonify({
            "success": True,
            "message": (
                "Candidate added successfully"
            ),
            "candidate_id": candidate_id
        }), 201

    except Exception as error:

        print(
            "Candidate creation error:",
            error
        )

        return jsonify({
            "success": False,
            "message": (
                "Candidate creation failed"
            )
        }), 500


# ==========================================
# GET SINGLE CANDIDATE
# ==========================================

@candidate_routes.route(
    "/<int:candidate_id>",
    methods=["GET"]
)
def single_candidate(candidate_id):

    candidate = get_candidate_by_id(
        candidate_id
    )

    if not candidate:

        return jsonify({
            "success": False,
            "message": "Candidate not found"
        }), 404

    return jsonify({
        "success": True,
        "candidate": candidate
    }), 200


# ==========================================
# DELETE CANDIDATE
# ADMIN ONLY
# ==========================================

@candidate_routes.route(
    "/<int:candidate_id>",
    methods=["DELETE"]
)
@admin_required
def remove_candidate(candidate_id):

    success, message = delete_candidate(
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
    }), 200