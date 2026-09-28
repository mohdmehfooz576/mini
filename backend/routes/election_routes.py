from flask import Blueprint, request, jsonify

from models.election import (
    create_election,
    get_all_elections,
    get_election_by_id,
    update_election_status
)

from models.candidate import (
    get_candidates_by_election
)

from models.vote import (
    get_results_by_election
)

from utils.auth import admin_required

from utils.helpers import is_valid_date


election_routes = Blueprint(
    "election_routes",
    __name__,
    url_prefix="/api/elections"
)


# ==========================================
# GET ALL ELECTIONS
# ==========================================

@election_routes.route(
    "/",
    methods=["GET"]
)
def all_elections():

    elections = get_all_elections()

    return jsonify({
        "success": True,
        "elections": elections
    }), 200


# ==========================================
# GET SINGLE ELECTION
# WITH CANDIDATES
# ==========================================

@election_routes.route(
    "/<int:election_id>",
    methods=["GET"]
)
def single_election(election_id):

    election = get_election_by_id(
        election_id
    )

    if not election:

        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    election["candidates"] = (
        get_candidates_by_election(
            election_id
        )
    )

    return jsonify({
        "success": True,
        "election": election
    }), 200


# ==========================================
# CREATE ELECTION
# ADMIN ONLY
# ==========================================

@election_routes.route(
    "/",
    methods=["POST"]
)
@admin_required
def add_election():

    data = request.get_json() or {}

    name = str(
        data.get("name", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

    start_date = data.get(
        "start_date"
    )

    end_date = data.get(
        "end_date"
    )

    if not name:

        return jsonify({
            "success": False,
            "message": "Election name is required"
        }), 400

    if not start_date or not end_date:

        return jsonify({
            "success": False,
            "message": (
                "Start date and end date "
                "are required"
            )
        }), 400

    if not is_valid_date(
        start_date
    ) or not is_valid_date(
        end_date
    ):

        return jsonify({
            "success": False,
            "message": (
                "Date must be in "
                "YYYY-MM-DD format"
            )
        }), 400

    if start_date > end_date:

        return jsonify({
            "success": False,
            "message": (
                "End date cannot be before "
                "start date"
            )
        }), 400

    try:

        election_id = create_election(
            name,
            description,
            start_date,
            end_date
        )

        if not election_id:

            return jsonify({
                "success": False,
                "message": (
                    "Election could not be created"
                )
            }), 500

        return jsonify({
            "success": True,
            "message": (
                "Election created successfully"
            ),
            "election_id": election_id
        }), 201

    except Exception as error:

        print(
            "Election creation error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Election creation failed"
        }), 500


# ==========================================
# STOP / REOPEN ELECTION
# ADMIN ONLY
# ==========================================

@election_routes.route(
    "/<int:election_id>/status",
    methods=["PUT"]
)
@admin_required
def change_status(election_id):

    data = request.get_json() or {}

    status = data.get(
        "status"
    )

    if status not in [
        "Active",
        "Stopped"
    ]:

        return jsonify({
            "success": False,
            "message": (
                "Status must be "
                "Active or Stopped"
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

    changed = update_election_status(
        election_id,
        status
    )

    if not changed:

        return jsonify({
            "success": False,
            "message": (
                "Election status could "
                "not be updated"
            )
        }), 500

    if status == "Stopped":

        message = (
            "Election stopped successfully"
        )

    else:

        message = (
            "Election reopened successfully"
        )

    return jsonify({
        "success": True,
        "message": message
    }), 200


# ==========================================
# GET ELECTION RESULTS
# ==========================================

@election_routes.route(
    "/<int:election_id>/results",
    methods=["GET"]
)
def election_results(election_id):

    election = get_election_by_id(
        election_id
    )

    if not election:

        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    results = get_results_by_election(
        election_id
    )

    total_votes = sum(
        candidate["vote_count"]
        for candidate in results
    )

    return jsonify({
        "success": True,
        "election": {
            "id": election["id"],
            "name": election["name"],
            "description": election["description"],
            "start_date": election["start_date"],
            "end_date": election["end_date"],
            "status": election["status"]
        },
        "total_votes": total_votes,
        "results": results
    }), 200