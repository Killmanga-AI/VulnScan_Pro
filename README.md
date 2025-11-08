
VulnScan Pro

AI-enhanced Web Security Scanner — Built for Developers Actually needs

> A solo-built security testing platform designed to detect the vulnerabilities that others miss. It's fast, simple, and affordable.




Project Overview

VulnScan Pro is an AI-assisted web vulnerability scanner that helps developers, freelancers, and small teams identify real-world security flaws,especially business logic vulnerabilities that typical scanners overlook.

I built this project to learn deeply about application security and build something practical that could evolve into a professional, enterprise-grade SaaS platform.

It’s currently an MVP, but already includes a working web interface, real-time scan engine, and a full backend system ready for production scaling.



Latest Update — Web Interface Launched

The newest version introduces a professional web dashboard:

 Dark theme for comfortable use

 Real-time scan progress tracking

 Color-coded vulnerability results

 Responsive design (mobile-friendly)

 Full frontend-backend integration



Core Features (MVP Achieved)

Hybrid Scanning Engine: Async detection using FastAPI & AIOHTTP

Database-Driven System: SQLAlchemy models for users, scans, vulnerabilities

REST API: Start, manage, and retrieve scans easily

Modern UI: Clean HTML/CSS/JS interface

Payment Foundation: Stripe and PayFast ready for future SaaS use



Quick Setup (Local Demo)

# 1. Clone and setup
git clone https://github.com/Killmanga-AI/VulnScan_Pro.git
cd VulnScan_Pro

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python scripts/init_db.py

# 5. Launch app
uvicorn app.main:app --reload

Then visit: http://localhost:8000
 

Technical Stack

Layer	Technology	Purpose

Backend	FastAPI + SQLAlchemy	High-performance API
Scanner Engine	AIOHTTP + BeautifulSoup	Async vulnerability detection
Frontend	HTML5, CSS3, JavaScript	Web interface
Database	SQLite (→ PostgreSQL)	Data persistence
Payments (future)	Stripe and PayFast Integration	Subscription management




Vulnerabilities Detected (So Far)

SQL Injection

Cross-Site Scripting (XSS)

Missing Security Headers

CVSS-Based Risk Scoring


Coming Soon:
CSRF, CORS issues, exposed files, SSL/TLS configuration checks.


Project Structure

vulnscan-pro/
├── app/
│   ├── core/          # Database models & setup
│   ├── scanning/      # Vulnerability detection engine
│   ├── services/      # Business logic & integration
│   ├── static/        # Web interface (HTML, CSS, JS)
│   ├── main.py        # FastAPI application
│   └── config.py      # Configuration management
├── scripts/           # DB initialization
├── tests/             # Test suite
└── data/              # Database & file storage


For Developers

Example: Using the API

import requests

response = requests.post(
    "http://localhost:8000/api/scans",
    params={"target_url": "https://example.com"}
)
scan_id = response.json()["scan_id"]

results = requests.get(f"http://localhost:8000/api/scans/{scan_id}").json()
print(results)


Current Pricing Model (Prototype)

Plan	Price	Scans/Month	Features

Starter	$49	20	Basic scanning, PDF reports
Professional	$149	100	API access, advanced detection
Enterprise	$499	500	Custom configs, white-label options


(Not live yet — pricing model under development)


🧭 Roadmap & Vision

Completed (MVP):
✅ Core scanning engine
✅ Database + REST API
✅ Web interface
✅ Basic user system

In Progress:
 User authentication & token-based access
 Stripe payment integration
 Email notifications

Planned (Enterprise Phase):
 PDF report generation
 Team collaboration features
 Docker deployment
 AI-driven vulnerability explanations



🧍 About the Developer

I’m a solo software developer/student passionate about cybersecurity, DevOps, and full-stack development.
This project is my way of:

Learning deeply about web application security

Building a professional-grade security tool from scratch

Proving my technical and business readiness for a cybersecurity career


Future goal:
→ Transform VulnScan Pro into a full enterprise-grade SaaS platform with a public web presence, CI/CD integrations, and advanced scanning intelligence.


Feedback & Contributions

This is an open project. I welcome bug reports, suggestions, or ideas!
You can:

Open an issue on GitHub

Fork the repo and contribute improvements


(No official contact site yet, everything happens here on GitHub for now.)


Summary

VulnScan Pro is a practical, working prototype of what I believe the next generation of web vulnerability scanners should be:

Transparent about what it finds

Fast and easy to use

Affordable for developers and small teams

Expandable toward enterprise-grade needs



Clone the repo and start scanning today.
Your website security - simplified, automated, and built by someone who actually cares about what developers need.
