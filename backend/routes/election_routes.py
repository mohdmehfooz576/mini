from flask import Blueprint, request, jsonify

from models.election import (
    create_election,
    get_all_elections,
    get_election_by_id,
    update_election_details,
    update_election_status,
    archive_election,
    delete_election
)

from models.candidate import get_candidates_by_election
from models.vote import get_results_by_election

from utils.auth import admin_required
from utils.helpers import is_valid_date


election_routes = Blueprint(
    "election_routes",
    __name__,
    url_prefix="/api/elections"
)


# ==========================================
# GET ALL NON-ARCHIVED ELECTIONS
# ==========================================

@election_routes.route("/", methods=["GET"])
def all_elections():

    try:
        elections = get_all_elections(
            include_archived=False
        )

        # Voter-facing pages must never receive Draft or Published elections.
        # Admin pages keep the complete non-archived list for management.
        if request.args.get("audience", "").strip().lower() == "voter":
            elections = [
                election
                for election in elections
                if election.get("status") in ("Active", "Stopped")
            ]

        return jsonify({
            "success": True,
            "elections": elections
        }), 200

    except Exception as error:
        print("Get elections error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load elections"
        }), 500


# ==========================================
# GET ARCHIVED ELECTIONS - ADMIN ONLY
# ==========================================

@election_routes.route("/archived", methods=["GET"])
@admin_required
def archived_elections():

    try:
        all_elections = get_all_elections(
            include_archived=True
        )

        archived = [
            election
            for election in all_elections
            if election["status"] == "Archived"
        ]

        return jsonify({
            "success": True,
            "total": len(archived),
            "elections": archived
        }), 200

    except Exception as error:
        print("Archived elections error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load archived elections"
        }), 500


# ==========================================
# GET SINGLE ELECTION WITH CANDIDATES
# ==========================================

@election_routes.route("/<int:election_id>", methods=["GET"])
def single_election(election_id):

    try:
        election = get_election_by_id(election_id)

        if not election:
            return jsonify({
                "success": False,
                "message": "Election not found"
            }), 404

        election["candidates"] = get_candidates_by_election(
            election_id
        )

        return jsonify({
            "success": True,
            "election": election
        }), 200

    except Exception as error:
        print("Single election error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load election"
        }), 500


# ==========================================
# CREATE ELECTION - DRAFT
# ==========================================

@election_routes.route("/", methods=["POST"])
@admin_required
def add_election():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()

    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not name:
        return jsonify({
            "success": False,
            "message": "Election name is required"
        }), 400

    if not start_date or not end_date:
        return jsonify({
            "success": False,
            "message": "Start date and end date are required"
        }), 400

    if (
        not is_valid_date(start_date)
        or not is_valid_date(end_date)
    ):
        return jsonify({
            "success": False,
            "message": "Date must be in YYYY-MM-DD format"
        }), 400

    if start_date > end_date:
        return jsonify({
            "success": False,
            "message": "End date cannot be before start date"
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
                "message": "Election could not be created"
            }), 500

        return jsonify({
            "success": True,
            "message": "Election created as Draft successfully",
            "election_id": election_id,
            "status": "Draft"
        }), 201

    except Exception as error:
        print("Election creation error:", error)

        return jsonify({
            "success": False,
            "message": "Election creation failed"
        }), 500


# ==========================================
# UPDATE ELECTION DETAILS - DRAFT ONLY
# ==========================================

@election_routes.route("/<int:election_id>", methods=["PUT"])
@admin_required
def edit_election(election_id):

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()

    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not name:
        return jsonify({
            "success": False,
            "message": "Election name is required"
        }), 400

    if not start_date or not end_date:
        return jsonify({
            "success": False,
            "message": "Start date and end date are required"
        }), 400

    if (
        not is_valid_date(start_date)
        or not is_valid_date(end_date)
    ):
        return jsonify({
            "success": False,
            "message": "Date must be in YYYY-MM-DD format"
        }), 400

    if start_date > end_date:
        return jsonify({
            "success": False,
            "message": "End date cannot be before start date"
        }), 400

    try:
        updated = update_election_details(
            election_id,
            name,
            description,
            start_date,
            end_date
        )

        if not updated:
            return jsonify({
                "success": False,
                "message": "Election not found or no changes were made"
            }), 400

        return jsonify({
            "success": True,
            "message": "Draft election updated successfully"
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception as error:
        print("Election edit error:", error)

        return jsonify({
            "success": False,
            "message": "Election could not be updated"
        }), 500


# ==========================================
# PUBLISH / STOP / REOPEN ELECTION
# ==========================================

@election_routes.route("/<int:election_id>/status", methods=["PUT"])
@admin_required
def change_status(election_id):

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    allowed_statuses = [
        "Published",
        "Active",
        "Stopped"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": (
                "Status must be Published, Active or Stopped"
            )
        }), 400

    election = get_election_by_id(election_id)

    if not election:
        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    try:
        changed = update_election_status(
            election_id,
            status
        )

        if not changed:
            return jsonify({
                "success": False,
                "message": "Election status could not be updated"
            }), 400

        messages = {
            "Published": "Election published successfully",
            "Active": "Election activated successfully",
            "Stopped": "Election stopped successfully"
        }

        return jsonify({
            "success": True,
            "message": messages[status],
            "status": status
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception as error:
        print("Election status error:", error)

        return jsonify({
            "success": False,
            "message": "Election status update failed"
        }), 500


# ==========================================
# ARCHIVE ELECTION - ADMIN ONLY
# ==========================================

@election_routes.route("/<int:election_id>/archive", methods=["PUT"])
@admin_required
def archive_election_route(election_id):

    try:
        archived = archive_election(election_id)

        if not archived:
            return jsonify({
                "success": False,
                "message": "Election not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Election archived successfully",
            "status": "Archived"
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception as error:
        print("Election archive error:", error)

        return jsonify({
            "success": False,
            "message": "Election could not be archived"
        }), 500


# ==========================================
# DELETE ELECTION - ADMIN ONLY
# ==========================================

@election_routes.route("/<int:election_id>", methods=["DELETE"])
@admin_required
def remove_election(election_id):

    try:
        result = delete_election(election_id)

        if not result:
            return jsonify({
                "success": False,
                "message": "Election not found"
            }), 404

        if result["archived"]:
            message = (
                "Election has been archived. "
                "All votes and voter receipts have been preserved."
            )
        else:
            message = "Draft election deleted successfully"

        return jsonify({
            "success": True,
            "message": message,
            "election": result["name"],
            "total_votes": result["total_votes"],
            "archived": result["archived"]
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception as error:
        print("Election deletion error:", error)

        return jsonify({
            "success": False,
            "message": "Election could not be deleted"
        }), 500


# ==========================================
# GET ELECTION RESULTS
# ==========================================

@election_routes.route("/<int:election_id>/results", methods=["GET"])
def election_results(election_id):

    try:
        election = get_election_by_id(election_id)

        if not election:
            return jsonify({
                "success": False,
                "message": "Election not found"
            }), 404

        results = get_results_by_election(election_id)

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

    except Exception as error:
        print("Election results error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load election results"
        }), 500