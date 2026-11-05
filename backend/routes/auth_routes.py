
import re

from flask import Blueprint, request, jsonify
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.db import get_connection

from models.user import (
    get_user_by_email,
    create_user,
    update_user_password,
    update_security_question,
    get_security_question_by_email,
    get_security_answer_hash
)

from models.voter import create_voter, get_voter_by_user_id

from utils.auth import create_token, token_required


auth_routes = Blueprint(
    "auth_routes",
    __name__,
    url_prefix="/api/auth"
)


# ==========================================
# VALIDATION HELPERS
# ==========================================

SECURITY_QUESTIONS = {
    "Which historical personality inspires you?",
    "Who is your best friend?"
}


def normalize_department(value):
    return re.sub(r"[^A-Z]", "", str(value or "").upper())


def normalize_year(value):
    return re.sub(
        r"\s*YEAR\s*$",
        "",
        str(value or "").strip(),
        flags=re.IGNORECASE
    ).strip().lower()


def normalize_security_answer(value):
    return str(value or "").strip().casefold()


def is_valid_email(email):
    allowed_domains = {
        "gmail.com", "yahoo.com", "yahoo.in",
        "outlook.com", "hotmail.com", "live.com",
        "icloud.com", "me.com", "proton.me",
        "protonmail.com", "zoho.com", "zohomail.com",
        "aol.com", "gmx.com", "rediffmail.com"
    }

    pattern = r"^[a-z][a-z0-9._%+-]*@[a-z0-9.-]+\.[a-z]{2,}$"

    if not re.fullmatch(pattern, email):
        return False

    return email.split("@")[1] in allowed_domains


def eligible_student_matches(
    name,
    enrolment_no,
    department,
    email,
    year,
    mobile
):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT name, enrolment_no, department, email, year, mobile
            FROM eligible_students
            WHERE UPPER(TRIM(enrolment_no)) = %s
              AND LOWER(TRIM(email)) = %s
              AND mobile = %s
            """,
            (enrolment_no, email, mobile)
        )

        students = cursor.fetchall()

        for student in students:
            if (
                str(student["name"]).strip().casefold()
                == name.strip().casefold()
                and normalize_department(student["department"])
                == normalize_department(department)
                and normalize_year(student["year"])
                == normalize_year(year)
            ):
                return True

        return False

    except Exception as error:
        print("Eligible student matching error:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# REGISTER
# ==========================================

@auth_routes.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()

    enrolment_no = str(
        data.get("enrolment_no", data.get("roll_no", ""))
    ).strip().upper()

    mobile = str(data.get("mobile", "")).strip()
    department = str(data.get("department", "")).strip().upper()
    year = str(data.get("year", "")).strip()

    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    security_question = str(
        data.get("security_question", "")
    ).strip()

    security_answer = normalize_security_answer(
        data.get("security_answer", "")
    )

    if not all([
        name,
        email,
        enrolment_no,
        mobile,
        department,
        year,
        password,
        confirm_password,
        security_question,
        security_answer
    ]):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    if len(name) > 150:
        return jsonify({
            "success": False,
            "message": "Name is too long"
        }), 400

    if not is_valid_email(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email from an approved provider"
        }), 400

    if not re.fullmatch(r"ECCU\d{7,9}", enrolment_no):
        return jsonify({
            "success": False,
            "message": "Enrolment number must be ECCU followed by 7 to 9 digits"
        }), 400

    if not re.fullmatch(r"\d{10}", mobile):
        return jsonify({
            "success": False,
            "message": "Mobile number must contain exactly 10 digits"
        }), 400

    allowed_departments = {
        "BA", "BSC", "BCOM", "BCA", "BVOC", "BED"
    }

    if department not in allowed_departments:
        return jsonify({
            "success": False,
            "message": "Please select a valid department"
        }), 400

    allowed_years = {
        "1st", "1st year",
        "2nd", "2nd year",
        "3rd", "3rd year"
    }

    if year.lower() not in allowed_years:
        return jsonify({
            "success": False,
            "message": "Please select a valid year"
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters"
        }), 400

    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Password and Confirm Password do not match"
        }), 400

    if security_question not in SECURITY_QUESTIONS:
        return jsonify({
            "success": False,
            "message": "Please select a valid security question"
        }), 400

    if len(security_answer) < 2 or len(security_answer) > 150:
        return jsonify({
            "success": False,
            "message": "Security answer must contain 2 to 150 characters"
        }), 400

    if get_user_by_email(email):
        return jsonify({
            "success": False,
            "message": "This email is already registered"
        }), 409

    eligible = eligible_student_matches(
        name,
        enrolment_no,
        department,
        email,
        year,
        mobile
    )

    if eligible is None:
        return jsonify({
            "success": False,
            "message": "Unable to verify student details. Please try again."
        }), 500

    status = "Approved" if eligible else "Pending"

    hashed_password = generate_password_hash(password)

    user_id = create_user(
        name,
        email,
        hashed_password,
        "voter"
    )

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Unable to create user account"
        }), 500

    # Save security question and hashed answer.
    answer_hash = generate_password_hash(security_answer)

    security_saved = update_security_question(
        user_id,
        security_question,
        answer_hash
    )

    if not security_saved:

        connection = get_connection()

        if connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM users WHERE id = %s",
                    (user_id,)
                )
                connection.commit()

            except Exception as error:
                connection.rollback()
                print("Registration cleanup error:", error)

            finally:
                cursor.close()
                connection.close()

        return jsonify({
            "success": False,
            "message": "Unable to save security question. Please try again."
        }), 500

    voter_id = create_voter(
        user_id,
        enrolment_no,
        mobile,
        department,
        year,
        status
    )

    if not voter_id:

        connection = get_connection()

        if connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM users WHERE id = %s",
                    (user_id,)
                )
                connection.commit()

            except Exception as error:
                connection.rollback()
                print("Registration cleanup error:", error)

            finally:
                cursor.close()
                connection.close()

        return jsonify({
            "success": False,
            "message": "Unable to complete voter registration"
        }), 500

    application_ref = f"VR-{voter_id:06d}"

    return jsonify({
        "success": True,
        "message": (
            "Registration approved successfully"
            if status == "Approved"
            else "Registration submitted for admin approval"
        ),
        "user_id": user_id,
        "voter_id": voter_id,
        "application_ref": application_ref,
        "status": status
    }), 201


# ==========================================
# LOGIN
# ==========================================

@auth_routes.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

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

    if not check_password_hash(user["password"], password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    if user["role"] == "voter":

        voter = get_voter_by_user_id(user["id"])

        if not voter:
            return jsonify({
                "success": False,
                "message": "Voter account not found"
            }), 404

        if voter["status"] == "Pending":
            return jsonify({
                "success": False,
                "message": "Your registration is waiting for admin approval"
            }), 403

        if voter["status"] == "Rejected":
            return jsonify({
                "success": False,
                "message": "Your registration has been rejected"
            }), 403

    token = create_token(user["id"], user["role"])

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


# ==========================================
# GET FORGOT PASSWORD SECURITY QUESTION
# ==========================================

@auth_routes.route("/forgot-password/question", methods=["POST"])
def forgot_password_question():

    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()

    if not email:
        return jsonify({
            "success": False,
            "message": "Email address is required"
        }), 400

    if not is_valid_email(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address"
        }), 400

    result = get_security_question_by_email(email)

    if not result or not result.get("security_question"):
        return jsonify({
            "success": False,
            "message": "No security question is configured for this account"
        }), 404

    return jsonify({
        "success": True,
        "message": "Security question found",
        "security_question": result["security_question"]
    }), 200


# ==========================================
# VERIFY SECURITY ANSWER AND RESET PASSWORD
# ==========================================

@auth_routes.route("/forgot-password/reset", methods=["POST"])
def forgot_password_reset():

    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()

    security_answer = normalize_security_answer(
        data.get("security_answer", "")
    )

    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not all([
        email,
        security_answer,
        new_password,
        confirm_password
    ]):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    if not isinstance(new_password, str) or len(new_password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters"
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "New password and confirmation do not match"
        }), 400

    user = get_user_by_email(email)

    if not user:
        return jsonify({
            "success": False,
            "message": "Unable to verify account details"
        }), 400

    answer_hash = get_security_answer_hash(user["id"])

    if not answer_hash:
        return jsonify({
            "success": False,
            "message": "Security question is not configured for this account"
        }), 400

    if not check_password_hash(answer_hash, security_answer):
        return jsonify({
            "success": False,
            "message": "Incorrect security answer"
        }), 401

    if check_password_hash(user["password"], new_password):
        return jsonify({
            "success": False,
            "message": "New password must be different from current password"
        }), 400

    password_hash = generate_password_hash(new_password)

    updated = update_user_password(
        user["id"],
        password_hash
    )

    if not updated:
        return jsonify({
            "success": False,
            "message": "Password could not be reset"
        }), 500

    return jsonify({
        "success": True,
        "message": "Password reset successfully. Please log in again."
    }), 200


# ==========================================
# CHANGE PASSWORD
# ==========================================

@auth_routes.route("/change-password", methods=["POST"])
@token_required
def change_password():

    data = request.get_json(silent=True) or {}

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not all([
        current_password,
        new_password,
        confirm_password
    ]):
        return jsonify({
            "success": False,
            "message": "All password fields are required"
        }), 400

    if not isinstance(new_password, str) or len(new_password) < 8:
        return jsonify({
            "success": False,
            "message": "New password must contain at least 8 characters"
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "New password and confirmation do not match"
        }), 400

    if not check_password_hash(
        request.user["password"],
        current_password
    ):
        return jsonify({
            "success": False,
            "message": "Current password is incorrect"
        }), 400

    if current_password == new_password:
        return jsonify({
            "success": False,
            "message": "New password must be different from current password"
        }), 400

    password_hash = generate_password_hash(new_password)

    updated = update_user_password(
        request.user["id"],
        password_hash
    )

    if not updated:
        return jsonify({
            "success": False,
            "message": "Password could not be updated"
        }), 500

    return jsonify({
        "success": True,
        "message": "Password changed successfully. Please log in again."
    }), 200
