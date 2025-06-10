# 🕵️‍♂️ Honeypot Trap: Fake Login Collector (Instagram/WordPress)

This is a cybersecurity honeypot that simulates fake login portals (e.g., WordPress or Instagram) to collect and analyze malicious login attempts. It also includes an SSH honeypot to capture attacker commands.

## 🔒 Features

- ✅ Fake Instagram/WordPress login interface
- 📥 Captures username, password, IP, timestamp, and country
- 🌍 GeoIP mapping of attackers using CleanTalk API
- 📊 Web dashboard to visualize:
  - Captured credentials
  - Top login attempts
  - Executed SSH commands
- 📡 SSH honeypot with command logging via Paramiko
- 📁 Rotating log files stored locally

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/honeypot-trap.git
cd honeypot-trap
