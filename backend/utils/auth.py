
from functools import wraps
from datetime import datetime, timedelta, timezone

import jwt
from flask import request, jsonify

from config import Config
from models.user import get_user_by_id


def create_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    return jwt.encode(
        payload,
        Config.JWT_SECRET,
        algorithm="HS256"
    )


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Authorization token required"
            }), 401

        try:
            parts = auth_header.split()

            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({
                    "success": False,
                    "message": "Invalid authorization format"
                }), 401

            payload = jwt.decode(
                parts[1],
                Config.JWT_SECRET,
                algorithms=["HS256"]
            )

            user_id = payload.get("user_id")

            if not user_id:
                return jsonify({
                    "success": False,
                    "message": "Invalid token"
                }), 401

            user = get_user_by_id(user_id)

            if not user:
                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 401

            request.user = user

        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid token"
            }), 401

        except Exception as error:
            print("Authentication error:", error)
            return jsonify({
                "success": False,
                "message": "Authentication failed"
            }), 401

        return function(*args, **kwargs)

    return decorated


def admin_required(function):
    @wraps(function)
    @token_required
    def decorated(*args, **kwargs):
        if request.user["role"] != "admin":
            return jsonify({
                "success": False,
                "message": "Admin access required"
            }), 403

        return function(*args, **kwargs)

    return decorated
