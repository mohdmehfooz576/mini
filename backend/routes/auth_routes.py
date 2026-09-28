from flask import Blueprint, request, jsonify

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models.user import (
    get_user_by_email,
    create_user
)

from models.voter import (
    create_voter,
    get_voter_by_user_id
)

from utils.auth import create_token


auth_routes = Blueprint(
    "auth_routes",
    __name__,
    url_prefix="/api/auth"
)


@auth_routes.route(
    "/register",
    methods=["POST"]
)
def register():

    data = request.get_json() or {}

    name = str(
        data.get("name", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip().lower()

    password = str(
        data.get("password", "")
    )

    roll_no = str(
        data.get("roll_no", "")
    ).strip()

    mobile = str(
        data.get("mobile", "")
    ).strip()

    department = str(
        data.get("department", "")
    ).strip()

    year = str(
        data.get("year", "")
    ).strip()

    # Required fields
    if not name or not email or not password:

        return jsonify({
            "success": False,
            "message": "Name, email and password are required"
        }), 400

    if not roll_no:

        return jsonify({
            "success": False,
            "message": "Roll number is required"
        }), 400

    # Check duplicate email
    if get_user_by_email(email):

        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 409

    hashed_password = generate_password_hash(
        password
    )

    try:

        # Create user
        user_id = create_user(
            name,
            email,
            hashed_password,
            "voter"
        )

        if not user_id:

            return jsonify({
                "success": False,
                "message": "Could not create user"
            }), 500

        # Create voter profile
        voter_id = create_voter(
            user_id,
            roll_no,
            mobile,
            department,
            year
        )

        if not voter_id:

            return jsonify({
                "success": False,
                "message": "Could not create voter profile"
            }), 500

        return jsonify({
            "success": True,
            "message": (
                "Registration successful. "
                "Wait for admin approval."
            ),
            "user_id": user_id,
            "voter_id": voter_id
        }), 201

    except Exception as error:

        print(
            "Registration error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Registration failed"
        }), 500


@auth_routes.route(
    "/login",
    methods=["POST"]
)
def login():

    data = request.get_json() or {}

    email = str(
        data.get("email", "")
    ).strip().lower()

    password = str(
        data.get("password", "")
    )

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    user = get_user_by_email(email)

    if not user:

        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(
        user["password"],
        password
    ):

        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    # Voter approval check
    if user["role"] == "voter":

        voter = get_voter_by_user_id(
            user["id"]
        )

        if not voter:

            return jsonify({
                "success": False,
                "message": "Voter profile not found"
            }), 404

        if voter["status"] == "Pending":

            return jsonify({
                "success": False,
                "message": (
                    "Your registration is waiting "
                    "for admin approval."
                )
            }), 403

        if voter["status"] == "Rejected":

            return jsonify({
                "success": False,
                "message": (
                    "Your voter registration "
                    "has been rejected."
                )
            }), 403

    # Create JWT token
    token = create_token(user)

    return jsonify({

        "success": True,

        "message": "Login successful",

        "token": token,

        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }

    }), 200