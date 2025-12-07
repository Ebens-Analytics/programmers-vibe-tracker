import os
from flask import Flask, render_template, request, redirect
import sqlite3
import datetime

# -------------------------------
# PATH SETUP (ANDROID SAFE)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(BASE_DIR, "vibe.db")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# -------------------------------
# DATABASE SETUP
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Vibes Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS vibes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mood INTEGER,
            energy INTEGER,
            focus INTEGER
        )
    """)

    # Project Tracker Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            stage TEXT,
            progress INTEGER,
            blocker TEXT,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# HOME / VIBE TRACKER
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mood = int(request.form.get("mood"))
        energy = int(request.form.get("energy"))
        focus = int(request.form.get("focus"))
        today = datetime.date.today().isoformat()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO vibes (date, mood, energy, focus) VALUES (?, ?, ?, ?)",
            (today, mood, energy, focus),
        )
        conn.commit()
        conn.close()

        return redirect("/history")

    return render_template("index.html")

# -------------------------------
# VIBE HISTORY + CHART DATA
# -------------------------------
@app.route("/history")
def history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT date, mood, energy, focus FROM vibes ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()

    dates = [r[0] for r in rows]
    moods = [r[1] for r in rows]
    energies = [r[2] for r in rows]
    focus = [r[3] for r in rows]

    return render_template(
        "history.html",
        rows=rows,
        dates=dates,
        moods=moods,
        energies=energies,
        focus=focus,
    )

# -------------------------------
# PROJECT TRACKER
# -------------------------------
@app.route("/project", methods=["GET", "POST"])
def project():
    if request.method == "POST":
        project_name = request.form.get("project_name")
        stage = request.form.get("stage")
        progress = int(request.form.get("progress"))
        blocker = request.form.get("blocker")
        today = datetime.date.today().isoformat()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO projects (project_name, stage, progress, blocker, date)
            VALUES (?, ?, ?, ?, ?)
        """, (project_name, stage, progress, blocker, today))
        conn.commit()
        conn.close()

        return redirect("/project")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT project_name, stage, progress, blocker, date FROM projects ORDER BY id DESC")
    projects = c.fetchall()
    conn.close()

    return render_template("project.html", projects=projects)

# -------------------------------
# MAIN ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)