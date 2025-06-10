# 🛡️ SSH & Web Honeypot Project

This project is a dual-purpose cybersecurity honeypot designed to detect and log malicious login attempts against both:
- A **fake SSH service** using Paramiko.
- A **fake web login interface** styled to mimic popular platforms like WordPress or Instagram.

## 🔍 Features

- **SSH Honeypot**:
  - Captures login credentials.
  - Logs attacker IPs and commands.
  - Uses rotating log files for persistence.

- **Web Honeypot**:
  - Fake login page (WordPress or Instagram style).
  - Captures usernames, passwords, IP, timestamp, and geolocation.
  - Redirects attackers to a fake dashboard or message.

- **Dashboard**:
  - Visual interface to view captured credentials and executed commands.
  - Optional login attempts chart.

## 🧰 Tech Stack

- Python 3.x
- Flask
- Paramiko
- Pandas
- Requests
- HTML/CSS

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/honeypot-project.git
cd honeypot-project

