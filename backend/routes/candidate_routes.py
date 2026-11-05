
import os
import uuid

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app
)
from werkzeug.utils import secure_filename

from models.candidate import (
    create_candidate,
    get_candidates_by_election,
    get_candidate_by_id,
    delete_candidate
)

from models.election import get_election_by_id
from utils.auth import admin_required


candidate_routes = Blueprint(
    "candidate_routes",
    __name__,
    url_prefix="/api/candidates"
)


# ==========================================
# PHOTO SETTINGS
# ==========================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def save_candidate_photo(file):

    if not file or not file.filename:
        return None, "Please select a candidate photo"

    if not allowed_file(file.filename):
        return None, "Only JPG, JPEG, PNG and WEBP images are allowed"

    upload_folder = current_app.config.get(
        "CANDIDATE_UPLOAD_FOLDER"
    )

    if not upload_folder:
        return None, "Upload folder is not configured"

    os.makedirs(upload_folder, exist_ok=True)

    extension = file.filename.rsplit(".", 1)[1].lower()

    filename = secure_filename(
        f"{uuid.uuid4().hex}.{extension}"
    )

    file_path = os.path.join(
        upload_folder,
        filename
    )

    try:
        file.save(file_path)

        return (
            f"assets/uploads/candidates/{filename}",
            None
        )

    except Exception as error:
        print("Photo upload error:", error)
        return None, "Candidate photo upload failed"


# ==========================================
# GET CANDIDATES BY ELECTION
# ==========================================

@candidate_routes.route(
    "/election/<int:election_id>",
    methods=["GET"]
)
def candidates(election_id):

    election = get_election_by_id(election_id)

    if not election:
        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    candidates_list = get_candidates_by_election(
        election_id
    )

    return jsonify({
        "success": True,
        "candidates": candidates_list
    }), 200


# ==========================================
# ADD CANDIDATE WITH PHOTO
# ADMIN ONLY
# ONLY DRAFT ELECTIONS
# ==========================================

@candidate_routes.route(
    "/",
    methods=["POST"]
)
@admin_required
def add_candidate():

    election_id = request.form.get("election_id")

    name = request.form.get(
        "name", ""
    ).strip()

    year_position = request.form.get(
        "year_position", ""
    ).strip()

    photo = request.files.get("photo")

    if not election_id or not name:
        return jsonify({
            "success": False,
            "message": "Election and candidate name are required"
        }), 400

    try:
        election_id = int(election_id)
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid election ID"
        }), 400

    # Check election
    election = get_election_by_id(election_id)

    if not election:
        return jsonify({
            "success": False,
            "message": "Election not found"
        }), 404

    # ======================================
    # IMPORTANT: CANDIDATE ADD RESTRICTION
    # Candidates can only be added in Draft.
    # ======================================

    election_status = str(
        election.get("status", "")
    ).strip().lower()

    if election_status != "draft":
        return jsonify({
            "success": False,
            "message": (
                "Candidates can only be added to Draft elections. "
                "This election has already been published or started."
            ),
            "election_status": election.get("status")
        }), 403

    # ======================================
    # PREVENT DUPLICATE CANDIDATE NAMES
    # ======================================

    candidates_list = get_candidates_by_election(
        election_id
    )

    for candidate in candidates_list:

        if candidate["name"].strip().lower() == name.lower():

            return jsonify({
                "success": False,
                "message": "Candidate already exists"
            }), 409

    # ======================================
    # PHOTO UPLOAD
    # ======================================

    photo_path = None

    if photo and photo.filename:

        photo_path, photo_error = save_candidate_photo(photo)

        if photo_error:
            return jsonify({
                "success": False,
                "message": photo_error
            }), 400

    # ======================================
    # CREATE CANDIDATE
    # ======================================

    try:

        candidate_id = create_candidate(
            election_id,
            name,
            year_position,
            photo_path
        )

        if not candidate_id:

            # Remove uploaded photo if DB insertion fails
            if photo_path:

                full_path = os.path.join(
                    current_app.config["CANDIDATE_UPLOAD_FOLDER"],
                    os.path.basename(photo_path)
                )

                if os.path.exists(full_path):
                    os.remove(full_path)

            return jsonify({
                "success": False,
                "message": "Candidate could not be added"
            }), 500

        return jsonify({
            "success": True,
            "message": "Candidate added successfully",
            "candidate_id": candidate_id,
            "photo": photo_path
        }), 201

    except Exception as error:

        print("Candidate creation error:", error)

        # Remove uploaded photo if creation fails
        if photo_path:

            try:
                full_path = os.path.join(
                    current_app.config["CANDIDATE_UPLOAD_FOLDER"],
                    os.path.basename(photo_path)
                )

                if os.path.exists(full_path):
                    os.remove(full_path)

            except Exception as photo_error:
                print("Photo cleanup error:", photo_error)

        return jsonify({
            "success": False,
            "message": "Candidate creation failed"
        }), 500


# ==========================================
# GET SINGLE CANDIDATE
# ==========================================

@candidate_routes.route(
    "/<int:candidate_id>",
    methods=["GET"]
)
def single_candidate(candidate_id):

    candidate = get_candidate_by_id(candidate_id)

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

    success, message = delete_candidate(candidate_id)

    if not success:
        return jsonify({
            "success": False,
            "message": message
        }), 400

    return jsonify({
        "success": True,
        "message": message
    }), 200
