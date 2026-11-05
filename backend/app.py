
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from database.db import get_connection

from models.user import get_user_by_email, create_user
from models.election import stop_expired_elections

from routes.auth_routes import auth_routes
from routes.voter_routes import voter_routes
from routes.election_routes import election_routes
from routes.candidate_routes import candidate_routes
from routes.vote_routes import vote_routes
from routes.admin_routes import admin_routes
from routes.notice_routes import notice_routes


# ==========================================
# PROJECT ROOT DIRECTORY
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================
# FLASK APP
# ==========================================

app = Flask(
    __name__,
    static_folder=BASE_DIR,
    static_url_path=""
)

CORS(app)


# ==========================================
# CANDIDATE PHOTO UPLOAD SETTINGS
# ==========================================

CANDIDATE_UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "assets",
    "uploads",
    "candidates"
)

os.makedirs(
    CANDIDATE_UPLOAD_FOLDER,
    exist_ok=True
)

app.config["CANDIDATE_UPLOAD_FOLDER"] = (
    CANDIDATE_UPLOAD_FOLDER
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# ==========================================
# REGISTER API ROUTES
# ==========================================

app.register_blueprint(auth_routes)
app.register_blueprint(voter_routes)
app.register_blueprint(election_routes)
app.register_blueprint(candidate_routes)
app.register_blueprint(vote_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(notice_routes)


# ==========================================
# CREATE DEMO ADMIN
# ==========================================

def initialize_demo_admin():

    try:

        existing_admin = get_user_by_email(
            "admin@voteright.com"
        )

        if existing_admin:
            return

        password_hash = generate_password_hash(
            "admin123"
        )

        create_user(
            "VoteRight Admin",
            "admin@voteright.com",
            password_hash,
            "admin"
        )

        print("Demo admin created successfully.")

    except Exception as error:

        print("Demo admin setup error:", error)


# ==========================================
# AUTOMATIC ELECTION STOP SCHEDULER
# ==========================================

scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)


def start_election_scheduler():

    if scheduler.running:
        return

    try:
        # Check expired elections immediately at startup
        stop_expired_elections()

        print("Expired election check completed.")

    except Exception as error:
        print("Initial election status check failed:", error)

    # Check expired elections every 60 seconds
    scheduler.add_job(
        func=stop_expired_elections,
        trigger="interval",
        minutes=1,
        id="automatic_election_stop",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()

    print("Automatic election scheduler started.")
    print("Election expiry check interval: 1 minute.")


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/api/health", methods=["GET"])
def health():

    connection = get_connection()

    if connection:

        connection.close()

        return jsonify({
            "success": True,
            "message": (
                "VoteRight backend is running "
                "and MySQL is connected."
            )
        }), 200

    return jsonify({
        "success": False,
        "message": (
            "Backend is running but "
            "MySQL connection failed."
        )
    }), 500


# ==========================================
# FRONTEND HOME PAGE
# ==========================================

@app.route("/")
def home():

    return send_from_directory(
        BASE_DIR,
        "home.html"
    )


# ==========================================
# FRONTEND FILES
# ==========================================

@app.route("/<path:path>")
def frontend_files(path):

    file_path = os.path.join(
        BASE_DIR,
        path
    )

    if os.path.isfile(file_path):

        return send_from_directory(
            BASE_DIR,
            path
        )

    return jsonify({
        "success": False,
        "message": "Page not found"
    }), 404


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    initialize_demo_admin()

    print("====================================")
    print("VoteRight Backend Starting...")
    print("====================================")

    print("Server: http://127.0.0.1:5000")
    print("Admin Email: admin@voteright.com")
    print("Admin Password: admin123")
    print("Candidate Upload Folder:")
    print(CANDIDATE_UPLOAD_FOLDER)

    print("====================================")

    start_election_scheduler()

    try:

        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True,
            use_reloader=False
        )

    finally:

        if scheduler.running:
            scheduler.shutdown(wait=False)
            print("Election scheduler stopped.")
