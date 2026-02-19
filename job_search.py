import requests
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['EMAIL_PASSWORD']

jobs = []

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# YOUR PROFILE
# =========================

ENGINEERING_KEYWORDS = [
    "frontend engineer",
    "frontend developer",
    "software engineer",
    "software developer",
    "fullstack engineer",
    "fullstack developer",
    "react engineer",
    "react developer"
]

EXCLUDE = [
    "recruiter",
    "designer",
    "manager",
    "marketing",
    "sales",
    "hr"
]

PREFERRED_LOCATIONS = [
    "remote",
    "india",
    "delhi",
    "gurgaon",
    "bangalore",
    "uae",
    "dubai",
    "germany",
    "netherlands",
    "canada",
    "japan",
    "uk"
]

# =========================
# FILTER
# =========================

def valid(title):

    title = title.lower()

    if any(x in title for x in EXCLUDE):
        return False

    if any(x in title for x in ENGINEERING_KEYWORDS):
        return True

    return False


# =========================
# SCORING SYSTEM
# =========================

def score_job(title, company, location):

    text = f"{title} {company} {location}".lower()
    score = 0

    if "frontend" in text:
        score += 30

    if "react" in text:
        score += 30

    if "next" in text:
        score += 20

    if "fullstack" in text:
        score += 15

    if "remote" in location.lower():
        score += 30

    if any(loc in location.lower() for loc in PREFERRED_LOCATIONS):
        score += 20

    if any(x in company.lower() for x in ["tech", "ai", "labs", "cloud"]):
        score += 10

    if "visa" in text or "sponsor" in text:
        score += 25

    return min(score, 100)


# =========================
# LINKEDIN
# =========================

def fetch_linkedin():

    print("LinkedIn...")

    for keyword in ENGINEERING_KEYWORDS:

        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location=Remote&start=0"

        try:

            res = requests.get(url, headers=HEADERS)

            parts = res.text.split('href="')

            for part in parts:

                if "/jobs/view/" in part:

                    link = part.split('"')[0]

                    jobs.append({
                        "company": "LinkedIn Company",
                        "role": keyword,
                        "location": "Remote",
                        "link": link,
                        "score": score_job(keyword, "LinkedIn", "Remote")
                    })

        except:
            pass


# =========================
# GREENHOUSE
# =========================

def fetch_greenhouse():

    print("Greenhouse...")

    companies = [
        "stripe",
        "shopify",
        "vercel",
        "coinbase",
        "airbnb",
        "razorpay",
        "swiggy",
        "postman",
        "careem",
        "talabat",
        "noon"
    ]

    for company in companies:

        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        try:

            res = requests.get(url)
            data = res.json()

            for job in data["jobs"]:

                title = job["title"]
                location = job["location"]["name"]
                link = job["absolute_url"]

                if valid(title):

                    jobs.append({
                        "company": company.capitalize(),
                        "role": title,
                        "location": location,
                        "link": link,
                        "score": score_job(title, company, location)
                    })

        except:
            pass


# =========================
# LEVER (STARTUPS)
# =========================

def fetch_lever():

    print("Lever...")

    companies = [
        "figma",
        "supabase",
        "vercel",
        "sourcegraph"
    ]

    for company in companies:

        url = f"https://api.lever.co/v0/postings/{company}?mode=json"

        try:

            res = requests.get(url)
            data = res.json()

            for job in data:

                title = job["text"]
                location = job["categories"]["location"]
                link = job["hostedUrl"]

                if valid(title):

                    jobs.append({
                        "company": company.capitalize(),
                        "role": title,
                        "location": location,
                        "link": link,
                        "score": score_job(title, company, location)
                    })

        except:
            pass


# =========================
# REMOTIVE
# =========================

def fetch_remotive():

    print("Remotive...")

    try:

        res = requests.get("https://remotive.com/api/remote-jobs")
        data = res.json()

        for job in data["jobs"]:

            title = job["title"]

            if valid(title):

                jobs.append({
                    "company": job["company_name"],
                    "role": title,
                    "location": job["candidate_required_location"],
                    "link": job["url"],
                    "score": score_job(title, job["company_name"], job["candidate_required_location"])
                })

    except:
        pass


# =========================
# REMOTEOK
# =========================

def fetch_remoteok():

    print("RemoteOK...")

    try:

        res = requests.get("https://remoteok.com/api")
        data = res.json()

        for job in data:

            if isinstance(job, dict):

                title = job.get("position", "")

                if valid(title):

                    jobs.append({
                        "company": job.get("company", ""),
                        "role": title,
                        "location": "Remote",
                        "link": "https://remoteok.com" + job.get("url", ""),
                        "score": score_job(title, job.get("company", ""), "Remote")
                    })

    except:
        pass


# =========================
# YC STARTUPS
# =========================

def fetch_yc():

    print("YC...")

    try:

        res = requests.get("https://www.ycombinator.com/jobs", headers=HEADERS)

        parts = res.text.split('href="')

        for part in parts:

            if "/companies/" in part and "/jobs/" in part:

                link = part.split('"')[0]

                jobs.append({
                    "company": "YC Startup",
                    "role": "Software Engineer",
                    "location": "Remote",
                    "link": "https://www.ycombinator.com" + link,
                    "score": 85
                })

    except:
        pass


# =========================
# RUN ALL SOURCES
# =========================

fetch_linkedin()
fetch_greenhouse()
fetch_lever()
fetch_remotive()
fetch_remoteok()
fetch_yc()

print("Total raw jobs:", len(jobs))


# =========================
# REMOVE DUPLICATES
# =========================

unique = {}

for job in jobs:
    unique[job["link"]] = job

jobs = list(unique.values())

print("Unique jobs:", len(jobs))


# =========================
# SORT BEST MATCH FIRST
# =========================

jobs.sort(key=lambda x: x["score"], reverse=True)


# =========================
# BUILD EMAIL
# =========================

html = f"""
<h2>Best Frontend / Software Jobs ({len(jobs)} found)</h2>

<table border="1" cellpadding="6">

<tr>
<th>Match %</th>
<th>Company</th>
<th>Role</th>
<th>Location</th>
<th>Apply</th>
</tr>
"""

for job in jobs[:300]:

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

msg["Subject"] = f"Best Jobs {datetime.now().date()}"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()

print("Email sent successfully")
