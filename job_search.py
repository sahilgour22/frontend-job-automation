import requests
import smtplib
import os
import re
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['EMAIL_PASSWORD']

jobs = []

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==========================================
# YOUR PROFILE (FROM YOUR RESUME)
# ==========================================

YOUR_EXPERIENCE = 3.5

ALLOWED_STACK = [
    "react",
    "next",
    "javascript",
    "typescript",
    "frontend",
    "front-end",
    "fullstack",
    "full stack",
    "node"
]

REJECT_STACK = [
    "react native",
    "angular",
    "vue native",
    "ios",
    "android",
    "swift",
    "kotlin",
    "c++",
    "embedded",
    "firmware",
    "php",
    ".net",
    "golang",
    "rust",
    "backend only"
]

REJECT_TITLES = [
    "senior",
    "staff",
    "principal",
    "lead",
    "manager",
    "architect"
]

PREFERRED_LOCATIONS = [
    "remote",
    "india",
    "delhi",
    "gurgaon",
    "bangalore",
    "uae",
    "dubai",
    "netherlands",
    "germany",
    "canada",
    "uk"
]


# ==========================================
# EXPERIENCE DETECTION
# ==========================================

def extract_experience(text):

    text = text.lower()

    matches = re.findall(r'(\d+)\+?\s*years', text)

    if matches:
        return int(matches[0])

    return 2


# ==========================================
# PERFECT MATCH FILTER
# ==========================================

def is_perfect_match(title, company, location):

    text = f"{title} {company} {location}".lower()

    # Reject unwanted tech
    for bad in REJECT_STACK:
        if bad in text:
            return False

    # Reject senior roles
    for bad in REJECT_TITLES:
        if bad in title.lower():
            return False

    # Must match your stack
    if not any(skill in text for skill in ALLOWED_STACK):
        return False

    # Experience check
    exp = extract_experience(text)

    if exp > 4:
        return False

    return True


# ==========================================
# SMART SCORING
# ==========================================

def calculate_score(title, company, location):

    text = f"{title} {company} {location}".lower()

    score = 0

    if "react" in text:
        score += 40

    if "next" in text:
        score += 35

    if "frontend" in text:
        score += 30

    if "fullstack" in text:
        score += 25

    if "node" in text:
        score += 20

    if "typescript" in text:
        score += 15

    if "remote" in location.lower():
        score += 40

    if any(loc in location.lower() for loc in PREFERRED_LOCATIONS):
        score += 20

    if any(x in company.lower() for x in ["tech", "labs", "ai", "cloud"]):
        score += 10

    return score


# ==========================================
# REMOTEOK
# ==========================================

def fetch_remoteok():

    print("RemoteOK...")

    try:

        res = requests.get("https://remoteok.com/api")
        data = res.json()

        for job in data:

            if isinstance(job, dict):

                title = job.get("position", "")
                company = job.get("company", "")
                location = "Remote"
                link = "https://remoteok.com" + job.get("url", "")

                if is_perfect_match(title, company, location):

                    score = calculate_score(title, company, location)

                    jobs.append({
                        "company": company,
                        "role": title,
                        "location": location,
                        "link": link,
                        "score": score
                    })

    except:
        pass


# ==========================================
# REMOTIVE
# ==========================================

def fetch_remotive():

    print("Remotive...")

    try:

        res = requests.get("https://remotive.com/api/remote-jobs")
        data = res.json()

        for job in data["jobs"]:

            title = job["title"]
            company = job["company_name"]
            location = job["candidate_required_location"]
            link = job["url"]

            if is_perfect_match(title, company, location):

                score = calculate_score(title, company, location)

                jobs.append({
                    "company": company,
                    "role": title,
                    "location": location,
                    "link": link,
                    "score": score
                })

    except:
        pass


# ==========================================
# GREENHOUSE (BEST PRODUCT COMPANIES)
# ==========================================

def fetch_greenhouse():

    print("Greenhouse...")

    companies = [
        "vercel",
        "supabase",
        "stripe",
        "shopify",
        "postman",
        "razorpay",
        "careem",
        "swiggy"
    ]

    for company in companies:

        try:

            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

            res = requests.get(url)
            data = res.json()

            for job in data["jobs"]:

                title = job["title"]
                location = job["location"]["name"]
                link = job["absolute_url"]

                if is_perfect_match(title, company, location):

                    score = calculate_score(title, company, location)

                    jobs.append({
                        "company": company.capitalize(),
                        "role": title,
                        "location": location,
                        "link": link,
                        "score": score
                    })

        except:
            pass


# ==========================================
# YC STARTUPS
# ==========================================

def fetch_yc():

    print("YC Startups...")

    try:

        res = requests.get("https://www.ycombinator.com/jobs", headers=HEADERS)

        parts = res.text.split('href="')

        for part in parts:

            if "/companies/" in part and "/jobs/" in part:

                link = part.split('"')[0]

                jobs.append({
                    "company": "YC Startup",
                    "role": "Frontend Engineer",
                    "location": "Remote",
                    "link": "https://www.ycombinator.com" + link,
                    "score": 90
                })

    except:
        pass


# ==========================================
# RUN ALL
# ==========================================

fetch_remoteok()
fetch_remotive()
fetch_greenhouse()
fetch_yc()

print("Raw jobs:", len(jobs))


# ==========================================
# REMOVE DUPLICATES
# ==========================================

unique = {}

for job in jobs:
    unique[job["link"]] = job

jobs = list(unique.values())


# ==========================================
# SORT BEST MATCH
# ==========================================

jobs.sort(key=lambda x: x["score"], reverse=True)


# ==========================================
# KEEP ONLY BEST 25
# ==========================================

jobs = jobs[:25]


print("Final jobs:", len(jobs))


# ==========================================
# BUILD EMAIL
# ==========================================

html = f"""
<h2>Top 25 Best Matching Jobs For You</h2>

<p>Based on your React, Next.js, Node.js experience</p>

<table border="1" cellpadding="6">

<tr>
<th>Match %</th>
<th>Company</th>
<th>Role</th>
<th>Location</th>
<th>Apply</th>
</tr>
"""

for job in jobs:

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


# ==========================================
# SEND EMAIL
# ==========================================

msg = MIMEText(html, "html")

msg["Subject"] = f"Top 25 Jobs For Sahil - {datetime.now().date()}"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()

print("Sent best 25 jobs")
