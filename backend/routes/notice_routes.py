from flask import Blueprint, request, jsonify

from models.notice import (
    get_published_notices,
    get_all_notices,
    get_notice_by_id,
    create_notice,
    update_notice,
    delete_notice
)

from utils.auth import (
    token_required,
    admin_required
)


notice_routes = Blueprint(
    "notice_routes",
    __name__,
    url_prefix="/api/notices"
)


# ==========================================
# PUBLIC / VOTER
# GET PUBLISHED NOTICES
# ==========================================

@notice_routes.route(
    "/",
    methods=["GET"]
)
def published_notices():

    try:

        notices = get_published_notices()

        return jsonify({
            "success": True,
            "notices": notices
        }), 200

    except Exception as error:

        print(
            "Get notices error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Could not load notices"
        }), 500


# ==========================================
# ADMIN
# GET ALL NOTICES
# ==========================================

@notice_routes.route(
    "/admin",
    methods=["GET"]
)
@admin_required
def admin_notices():

    try:

        notices = get_all_notices()

        return jsonify({
            "success": True,
            "notices": notices
        }), 200

    except Exception as error:

        print(
            "Admin notices error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Could not load notices"
        }), 500


# ==========================================
# ADMIN
# CREATE NOTICE
# ==========================================

@notice_routes.route(
    "/",
    methods=["POST"]
)
@admin_required
def add_notice():

    data = request.get_json() or {}

    title = str(
        data.get("title", "")
    ).strip()

    message = str(
        data.get("message", "")
    ).strip()

    notice_type = str(
        data.get("type", "Announcement")
    ).strip()

    if not title:

        return jsonify({
            "success": False,
            "message": "Notice title is required"
        }), 400

    if not message:

        return jsonify({
            "success": False,
            "message": "Notice message is required"
        }), 400

    if not notice_type:

        notice_type = "Announcement"

    try:

        notice_id = create_notice(
            title,
            message,
            notice_type,
            request.user["id"]
        )

        if not notice_id:

            return jsonify({
                "success": False,
                "message": "Could not create notice"
            }), 500

        notice = get_notice_by_id(
            notice_id
        )

        return jsonify({
            "success": True,
            "message": "Notice published successfully",
            "notice": notice
        }), 201

    except Exception as error:

        print(
            "Create notice error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Could not create notice"
        }), 500


# ==========================================
# ADMIN
# UPDATE NOTICE
# ==========================================

@notice_routes.route(
    "/<int:notice_id>",
    methods=["PUT"]
)
@admin_required
def edit_notice(notice_id):

    data = request.get_json() or {}

    title = str(
        data.get("title", "")
    ).strip()

    message = str(
        data.get("message", "")
    ).strip()

    notice_type = str(
        data.get("type", "Announcement")
    ).strip()

    status = str(
        data.get("status", "Published")
    ).strip()

    if not title:

        return jsonify({
            "success": False,
            "message": "Notice title is required"
        }), 400

    if not message:

        return jsonify({
            "success": False,
            "message": "Notice message is required"
        }), 400

    if status not in [
        "Published",
        "Hidden"
    ]:

        return jsonify({
            "success": False,
            "message": "Invalid notice status"
        }), 400

    try:

        existing_notice = get_notice_by_id(
            notice_id
        )

        if not existing_notice:

            return jsonify({
                "success": False,
                "message": "Notice not found"
            }), 404

        updated = update_notice(
            notice_id,
            title,
            message,
            notice_type,
            status
        )

        if not updated:

            return jsonify({
                "success": False,
                "message": "Notice could not be updated"
            }), 500

        notice = get_notice_by_id(
            notice_id
        )

        return jsonify({
            "success": True,
            "message": "Notice updated successfully",
            "notice": notice
        }), 200

    except Exception as error:

        print(
            "Update notice error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Could not update notice"
        }), 500


# ==========================================
# ADMIN
# DELETE NOTICE
# ==========================================

@notice_routes.route(
    "/<int:notice_id>",
    methods=["DELETE"]
)
@admin_required
def remove_notice(notice_id):

    try:

        existing_notice = get_notice_by_id(
            notice_id
        )

        if not existing_notice:

            return jsonify({
                "success": False,
                "message": "Notice not found"
            }), 404

        deleted = delete_notice(
            notice_id
        )

        if not deleted:

            return jsonify({
                "success": False,
                "message": "Notice could not be deleted"
            }), 500

        return jsonify({
            "success": True,
            "message": "Notice deleted successfully"
        }), 200

    except Exception as error:

        print(
            "Delete notice error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Could not delete notice"
        }), 500