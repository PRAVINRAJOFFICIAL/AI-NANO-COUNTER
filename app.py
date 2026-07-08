from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Response,
    jsonify,
    session,
    flash
)

from functools import wraps
from dotenv import load_dotenv

import os
import hashlib
import sqlite3

from firebase_auth import verify_token

from ai.detector import (
    detect_image,
    generate_frames,
    release_camera,
    get_live_counts
)

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

# ==========================================
# Flask Configuration
# ==========================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "ainanocounter"
)

app.config["UPLOAD_FOLDER"] = "static/uploads/images"

app.config["OUTPUT_FOLDER"] = "static/output"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}

# ==========================================
# Allowed File
# ==========================================

def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(".", 1)[1].lower()

        in

        ALLOWED_EXTENSIONS

    )

# ==========================================
# Login Required
# ==========================================

def login_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        if "user" not in session:

            flash(

                "Please login first",

                "warning"

            )

            return redirect(

                url_for("login")

            )

        return f(*args, **kwargs)

    return decorated

# ==========================================
# Home
# ==========================================

@app.route("/")
def home():

    if "user" in session:

        return redirect(

            url_for("dashboard")

        )

    return render_template(

        "home.html"

    )



# ==========================================
# Login Page
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user" in session:
        return redirect(url_for("dashboard"))

    # Firebase Google Login only
    if request.method == "POST":

        flash(
            "Please use Google Login.",
            "warning"
        )

    return render_template("login.html")
# ==========================================
# Dashboard
# ==========================================
@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        user=session["user"]
    )


# ==========================================
# Image Detection Page
# ==========================================
@app.route("/image")
@login_required
def image():

    return render_template(
        "image.html",
        user=session["user"]
    )


# ==========================================
# Live Camera Page
# ==========================================
@app.route("/camera")
@login_required
def camera():

    return render_template(
        "camera.html",
        user=session["user"]
    )

# ==========================================
# Reports Page
# ==========================================
@app.route("/reports")
@login_required
def reports():

    conn = sqlite3.connect("analytics.db")
    cursor = conn.cursor()

    # Total Images
    cursor.execute("SELECT COUNT(*) FROM detections")
    total_images = cursor.fetchone()[0]

    # Total Objects
    cursor.execute("SELECT SUM(total_objects) FROM detections")
    total_objects = cursor.fetchone()[0] or 0

    # Most Detected Object
    cursor.execute("""
        SELECT object_name,
               SUM(object_count)
        FROM detections
        GROUP BY object_name
        ORDER BY SUM(object_count) DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    most_object = row[0] if row else "None"

    # Detection History
    cursor.execute("""
        SELECT
            image_name,
            object_name,
            object_count,
            detected_at
        FROM detections
        ORDER BY detected_at DESC
        LIMIT 10
    """)

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "reports.html",
        total_images=total_images,
        total_objects=total_objects,
        most_object=most_object,
        history=history,
        user=session["user"]
    )
# ==========================================
# Detect Image
# ==========================================
@app.route("/detect", methods=["POST"])
@login_required
def detect():

    # Check image uploaded
    if "image" not in request.files:

        flash("Please upload an image.", "warning")

        return redirect(url_for("image"))

    image = request.files["image"]

    # Empty filename
    if image.filename == "":

        flash("No image selected.", "warning")

        return redirect(url_for("image"))

    # File validation
    if not allowed_file(image.filename):

        flash(
            "Only JPG, JPEG and PNG images are supported.",
            "danger"
        )

        return redirect(url_for("image"))

    # Create folders
    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    os.makedirs(
        app.config["OUTPUT_FOLDER"],
        exist_ok=True
    )

    # Save uploaded image
    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image.filename
    )

    image.save(filepath)

    # Run YOLO Detection
    results = detect_image(filepath)

    names = results[0].names

    detected = []

    counts = {}

    # Object Counting
    for box in results[0].boxes:

        cls = int(box.cls[0])

        label = names[cls]

        detected.append(label)

        counts[label] = counts.get(label, 0) + 1

    total = sum(counts.values())

    # =====================================
    # Save Analytics
    # =====================================

    conn = sqlite3.connect("analytics.db")

    cursor = conn.cursor()

    for key, value in counts.items():

        cursor.execute("""

        INSERT INTO detections(

            user_id,

            image_name,

            object_name,

            object_count,

            total_objects

        )

        VALUES(?,?,?,?,?)

        """,

        (

            session["user"]["user_id"],

            image.filename,

            key,

            value,

            total

        ))

    conn.commit()

    conn.close()

    # =====================================
    # Result Page
    # =====================================

    return render_template(

        "result.html",

        image="output/result.jpg",

        detected=detected,

        counts=counts,

        total=total,

        user=session["user"]

    )
# ==========================================
# Live Camera Feed
# ==========================================
@app.route("/video_feed")
@login_required
def video_feed():

    return Response(

        generate_frames(),

        mimetype="multipart/x-mixed-replace; boundary=frame"

    )


# ==========================================
# Live Count API
# ==========================================
@app.route("/counts")
@login_required
def counts():

    return jsonify(

        get_live_counts()

    )


# ==========================================
# Stop Camera
# ==========================================
@app.route("/stop_camera")
@login_required
def stop_camera():

    release_camera()

    return jsonify({

        "success": True,

        "message": "Camera Stopped"

    })


# ==========================================
# Verify Firebase Login
# ==========================================
@app.route("/verify_token", methods=["POST"])
def verify_google_login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No Data"
        }), 400

    id_token = data.get("idToken")

    if not id_token:
        return jsonify({
            "success": False,
            "message": "Missing Token"
        }), 400

    try:

        decoded = verify_token(id_token)

        uid = decoded["uid"]

        user_id = (
            int(hashlib.sha256(uid.encode()).hexdigest(), 16)
            % 900000
        ) + 100000

        session["user"] = {

            "uid": uid,

            "user_id": user_id,

            "email": decoded.get("email"),

            "name": decoded.get("name", "User"),

            "picture": decoded.get("picture", "")

        }

        return jsonify({

            "success": True,

            "redirect": "/dashboard"

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 401
# ==========================================
# Current User API
# ==========================================
@app.route("/current_user")
@login_required
def current_user():

    return jsonify(

        session["user"]

    )

# ==========================================
# Profile Page
# ==========================================

@app.route("/profile")
@login_required
def profile():

    return render_template(

        "profile.html",

        user=session["user"]

    )
# ==========================================
# Logout
# ==========================================
@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash(
        "Logged Out Successfully",
        "success"
    )

    return redirect(url_for("login"))



# ==========================================
# 404 Page
# ==========================================
@app.errorhandler(404)
def page_not_found(e):

    return render_template(

        "404.html"

    ),404


# ==========================================
# 500 Page
# ==========================================
@app.errorhandler(500)
def internal_error(e):

    return render_template(

        "500.html"

    ),500


# ==========================================
# Run Flask
# ==========================================
if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )

