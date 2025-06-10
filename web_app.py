from flask import Flask, render_template, request, redirect, url_for
import logging
from dashboard_data_parser import read_creds, read_cmds

app = Flask(__name__)

creds_logger = logging.getLogger('WebCredLogger')
creds_logger.setLevel(logging.INFO)
handler = logging.FileHandler("log_files/creds_audits.log")
creds_logger.addHandler(handler)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/wp-admin")
def wp_admin():
    return render_template("wp-admin.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    ip = request.remote_addr
    creds_logger.info(f"{ip}, {username}, {password}")
    print(f"[LOGIN ATTEMPT] Username: {username}, Password: {password}")
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", creds=read_creds(), commands=read_cmds())
