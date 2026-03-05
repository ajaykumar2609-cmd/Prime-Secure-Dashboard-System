import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/smartnotes")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/portfolio")
def portfolio():
    return render_template(
        "portfolio.html",
        current_year=datetime.now().year,
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        mongo.db.users.insert_one({
            "username": username,
            "password": password
        })
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
    user = mongo.db.users.find_one({"username": request.form["username"]})

    if user and bcrypt.check_password_hash(user["password"], request.form["password"]):
        token = create_access_token(identity=user["username"])
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# --------- CRUD API --------- #

@app.route("/add_note", methods=["POST"])
def add_note():
    data = request.json
    mongo.db.notes.insert_one({
        "username": data["username"],
        "note": data["note"]
    })
    return jsonify({"message": "Note added"})


@app.route("/get_notes/<username>")
def get_notes(username):
    notes = list(mongo.db.notes.find({"username": username}, {"_id": 0}))
    return jsonify(notes)


if __name__ == "__main__":
    app.run(debug=True)