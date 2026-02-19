import requests
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['EMAIL_PASSWORD']

jobs = []

# =========================
# YOUR STACK PROFILE
# =========================

YOUR_SKILLS = [
    "react",
    "next.js",
    "next",
    "typescript",
    "javascript",
    "frontend",
    "fullstack",
    "node",
    "node.js",
    "web",
    "api",
    "tailwind",
    "redux"
]

PREFERRED_LOCATIONS = [
    "remote",
    "worldwide",
    "anywhere",
    "uae",
    "dubai",
    "india",
    "germany",
    "netherlands",
    "canada",
    "uk",
    "europe"
]

ENGINEERING_KEYWORDS = [
    "frontend engineer",
    "frontend developer",
    "software engineer",
    "software developer",
    "fullstack engineer",
    "fullstack developer",
    "react engineer",
    "react developer",
    "web engineer",
    "javascript engineer"
]

EXCLUDE = [
    "recruiter",
    "designer",
    "manager",
    "marketing",
    "sales",
    "hr",
    "talent",
    "intern recruiter"
]

# =========================
# SCORING SYSTEM
# =========================

def calculate_score(title, company, location):

    score = 0
    text = f"{title} {company} {location}".lower()

    # Skill match
    for skill in YOUR_SKILLS:
        if skill in text:
            score += 12

    # React bonus
    if "react" in text:
        score += 25

    # Next.js bonus
    if "next" in text:
        score += 20

    # Frontend specific bonus
    if "frontend" in text:
        score += 20

    # Fullstack bonus
    if "fullstack" in text:
        score += 15

    # Remote bonus
    if "remote" in location.lower():
        score += 35

    # Dubai / UAE bonus
    if "dubai" in location.lower() or "uae" in location.lower():
        score += 30

    # Visa sponsorship bonus
    visa_words = ["visa", "sponsor", "relocation"]
    for word in visa_words:
        if word in text:
            score += 25

    # Big tech bonus
    big_companies = [
        "google",
        "meta",
        "amazon",
        "microsoft",
        "shopify",
        "stripe",
        "vercel",
        "netflix",
        "airbnb",
        "uber"
    ]

    for bc in big_companies:
        if bc in company.lower():
            score += 20

    return min(score, 100)


# =========================
# VALIDATION FILTER
# =========================

def is_valid(title):

    title = title.lower()

    if any(bad in title for bad in EXCLUDE):
        return False

    if any(good in title for good in ENGINEERING_KEYWORDS):
        return True

    return False


# =========================
# FETCH REMOTEOK
# =========================

def fetch_remoteok():

    try:

        response = requests.get("https://remoteok.com/api")
        data = response.json()

        for job in data:

            if isinstance(job, dict):

                title = job.get("position", "")
                company = job.get("company", "")
                location = "Remote"
                link = job.get("url", "")

                if is_valid(title):

                    score = calculate_score(title, company, location)

                    jobs.append({
                        "company": company,
                        "role": title,
                        "location": location,
                        "link": f"https://remoteok.com{link}",
                        "score": score
                    })

    except Exception as e:
        print("RemoteOK error:", e)


# =========================
# FETCH REMOTIVE
# =========================

def fetch_remotive():

    try:

        response = requests.get("https://remotive.com/api/remote-jobs")
        data = response.json()

        for job in data["jobs"]:

            title = job["title"]
            company = job["company_name"]
            location = job["candidate_required_location"]
            link = job["url"]

            if is_valid(title):

                score = calculate_score(title, company, location)

                jobs.append({
                    "company": company,
                    "role": title,
                    "location": location,
                    "link": link,
                    "score": score
                })

    except Exception as e:
        print("Remotive error:", e)


# =========================
# FETCH WEWORKREMOTELY
# =========================

def fetch_weworkremotely():

    try:

        response = requests.get(
            "https://weworkremotely.com/remote-jobs.json"
        )

        data = response.json()

        for category in data:

            for job in data[category]:

                title = job["title"]
                company = job["company_name"]
                location = job["region"]
                link = job["url"]

                if is_valid(title):

                    score = calculate_score(title, company, location)

                    jobs.append({
                        "company": company,
                        "role": title,
                        "location": location,
                        "link": link,
                        "score": score
                    })

    except Exception as e:
        print("WWR error:", e)


# =========================
# RUN FETCHERS
# =========================

fetch_remoteok()
fetch_remotive()
fetch_weworkremotely()

print("Fetched jobs:", len(jobs))


# =========================
# REMOVE DUPLICATES
# =========================

unique = {}

for job in jobs:
    key = job["company"] + job["role"]
    unique[key] = job

jobs = list(unique.values())


# =========================
# SORT BEST MATCH FIRST
# =========================

jobs.sort(key=lambda x: x["score"], reverse=True)


# =========================
# BUILD EMAIL
# =========================

html = f"""
<h2>Best Frontend Jobs for You ({len(jobs)} found)</h2>

<p>Top matches based on your React / Next.js profile</p>

<table border="1" cellpadding="6">
<tr>
<th>Match %</th>
<th>Company</th>
<th>Role</th>
<th>Location</th>
<th>Apply</th>
</tr>
"""

for job in jobs[:150]:

    html += f"""
    <tr>
    <td>{job['score']}%</td>
    <td>{job['company']}</td>
    <td>{job['role']}</td>
    <td>{job['location']}</td>
    <td><a href="{job['link']}">Apply</a></td>
    </tr>
    """

html += "</table>"


# =========================
# SEND EMAIL
# =========================

msg = MIMEText(html, "html")

msg["Subject"] = f"Best React / Frontend Jobs - {datetime.now().date()}"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()

print("Email sent successfully")
