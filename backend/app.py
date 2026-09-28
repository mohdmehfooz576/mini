from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "VoteRight Backend is running"
    })


@app.route("/api/health")
def health():

    return jsonify({
        "success": True,
        "message": "VoteRight API is working"
    })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )