from flask import Flask, render_template, request, redirect, session, jsonify
from services.user_service import UserService
from database.neo4j_service import Neo4jGraphService
from services.gnn_recommender import GNNRecommender
import json
import os

app = Flask(__name__, template_folder="views")
app.secret_key = "secret_key"


HISTORY_PATH = os.path.join("data", "user_history.json")


neo4j_service = Neo4jGraphService(
    "bolt://localhost:7687",
    "neo4j",
    "22228888"
)

user_service = UserService(neo4j_service)
gnn_recommender = GNNRecommender()


def update_history(username, video_id):

    if not os.path.exists(HISTORY_PATH) or os.path.getsize(HISTORY_PATH) == 0:
        history = {}
    else:
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = {}

    if username not in history:
        history[username] = []

    if video_id not in history[username]:
        history[username].append(video_id)

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    if user_service.login(username, password):
        session["username"] = username
        return redirect("/home")

    return "Login failed"


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        user_service.register(
            request.form["username"],
            request.form["password"]
        )
        return redirect("/")

    return render_template("register.html")


@app.route("/home")
def home():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    recommended = gnn_recommender.recommend(username, top_k=20)
    all_videos = neo4j_service.get_all_videos()

    return render_template(
        "home.html",
        username=username,
        recommended=recommended,
        all_videos=all_videos
    )


@app.route("/watch/<video_id>")
def watch(video_id):

    if "username" not in session:
        return "", 401

    username = session["username"]

    user_service.add_watch(username, video_id)
    update_history(username, video_id)

    return "", 204


@app.route("/watch_ajax", methods=["POST"])
def watch_ajax():

    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401

    username = session["username"]
    video_id = request.json["video_id"]

    user_service.add_watch(username, video_id)
    update_history(username, video_id)

    recommended = gnn_recommender.recommend(username)

    return jsonify({
        "recommended": recommended
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)