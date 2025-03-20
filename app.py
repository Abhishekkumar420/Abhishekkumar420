import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "super_secret_key"

UPLOAD_FOLDER = "uploaded_bots"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Login Credentials
USERNAME = "admin"
PASSWORD = "1234"

# ✅ Running Bots Ko Track Karne Ke Liye Dictionary
bot_processes = {}

# ✅ Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Invalid Login!", "danger")
    return render_template("login.html")

# ✅ Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ✅ Dashboard Page
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    bot_files = os.listdir(UPLOAD_FOLDER)
    return render_template("dashboard.html", bot_files=bot_files, running_bots=bot_processes)

# ✅ Upload Bot Script
@app.route("/upload", methods=["POST"])
def upload_bot():
    if "user" not in session:
        return redirect(url_for("login"))

    file = request.files["file"]
    if file.filename.endswith(".py"):
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        flash("✅ Bot Uploaded Successfully!", "success")
    else:
        flash("❌ Only .py files are allowed!", "danger")

    return redirect(url_for("dashboard"))

# ✅ Install Modules
@app.route("/install_modules")
def install_modules():
    if "user" not in session:
        return redirect(url_for("login"))

    os.system("pip install python-telegram-bot flask werkzeug")
    flash("✅ Required Modules Installed!", "success")
    return redirect(url_for("dashboard"))

# ✅ Start a Bot
@app.route("/start_bot/<bot_name>")
def start_bot(bot_name):
    if "user" not in session:
        return redirect(url_for("login"))

    bot_path = os.path.join(UPLOAD_FOLDER, bot_name)
    process = subprocess.Popen(["python", bot_path])  # Bot run karega background me
    bot_processes[bot_name] = process.pid  # Process ID (PID) store karenge

    flash(f"✅ {bot_name} Started!", "success")
    return redirect(url_for("dashboard"))

# ✅ Stop a Bot
@app.route("/stop_bot/<bot_name>")
def stop_bot(bot_name):
    if "user" not in session:
        return redirect(url_for("login"))

    if bot_name in bot_processes:
        os.system(f"kill -9 {bot_processes[bot_name]}")  # Bot ko terminate karega
        del bot_processes[bot_name]  # Bot list se hata do
        flash(f"✅ {bot_name} Stopped!", "success")
    else:
        flash(f"❌ {bot_name} is not running!", "danger")

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
