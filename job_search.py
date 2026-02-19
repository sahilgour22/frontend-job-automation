import requests
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['EMAIL_PASSWORD']

jobs = []

# STRICT engineering include keywords
INCLUDE = [
    "frontend engineer",
    "front-end engineer",
    "software engineer",
    "fullstack engineer",
    "full-stack engineer",
    "frontend developer",
    "front-end developer",
    "software developer",
    "fullstack developer",
    "full-stack developer",
    "react engineer",
    "react developer"
]

# Exclude non-engineering jobs
EXCLUDE = [
    "recruit",
    "recruiter",
    "talent",
    "manager",
    "marketing",
    "designer",
    "ux designer",
    "ui designer",
    "product manager",
    "hr",
    "human resources",
    "sales"
]

# Target locations
TARGET_LOCATIONS = [
    "remote",
    "united arab emirates",
    "uae",
    "dubai",
    "abu dhabi",
    "germany",
    "netherlands",
    "canada",
    "uk",
    "united kingdom",
    "japan",
    "india"
]


def is_valid_job(title, location=""):
    title = title.lower()
    location = location.lower()

    include_match = any(word in title for word in INCLUDE)
    exclude_match = any(word in title for word in EXCLUDE)
    location_match = any(loc in location for loc in TARGET_LOCATIONS)

    return include_match and not exclude_match


# SOURCE 1: RemoteOK
def fetch_remoteok():
    try:
        response = requests.get("https://remoteok.com/api")
        data = response.json()

        for job in data:

            if isinstance(job, dict):

                title = job.get("position", "")
                company = job.get("company", "")
                link = job.get("url", "")

                if is_valid_job(title, "remote"):

                    jobs.append({
                        "company": company,
                        "role": title,
                        "location": "Remote",
                        "link": f"https://remoteok.com{link}",
                        "keywords": "Frontend, Software, Fullstack, React, Remote",
                        "skills": "React, Next.js, TypeScript, APIs, CSS"
                    })

    except Exception as e:
        print("RemoteOK error:", e)


# SOURCE 2: WeWorkRemotely
def fetch_weworkremotely():
    try:
        response = requests.get("https://weworkremotely.com/remote-jobs.json")
        data = response.json()

        for category in data:

            for job in category.get("jobs", []):

                title = job.get("title", "")
                company = job.get("company_name", "")
                link = job.get("url", "")

                if is_valid_job(title, "remote"):

                    jobs.append({
                        "company": company,
                        "role": title,
                        "location": "Remote",
                        "link": link,
                        "keywords": "Frontend, Software, Fullstack, Startup, Remote",
                        "skills": "React, Next.js, TypeScript, Node.js, CSS"
                    })

    except Exception as e:
        print("WWR error:", e)


# SOURCE 3: UAE / Dubai via Remotive API
def fetch_remotive():
    try:
        response = requests.get("https://remotive.com/api/remote-jobs")
        data = response.json()

        for job in data.get("jobs", []):

            title = job.get("title", "")
            company = job.get("company_name", "")
            location = job.get("candidate_required_location", "")
            link = job.get("url", "")

            if is_valid_job(title, location):

                jobs.append({
                    "company": company,
                    "role": title,
                    "location": location,
                    "link": link,
                    "keywords": "Frontend, Software, Fullstack, Visa, Remote",
                    "skills": "React, Next.js, TypeScript, APIs, CSS"
                })

    except Exception as e:
        print("Remotive error:", e)


# Run all sources
fetch_remoteok()
fetch_weworkremotely()
fetch_remotive()

# Remove duplicates
unique_jobs = []
seen = set()

for job in jobs:
    key = job["company"] + job["role"]

    if key not in seen:
        unique_jobs.append(job)
        seen.add(key)

jobs = unique_jobs


# Build HTML email
html = f"""
<h2>Frontend / Software Engineering Jobs ({len(jobs)} found)</h2>
<table border="1" cellpadding="5">
<tr>
<th>Company</th>
<th>Role</th>
<th>Location</th>
<th>Apply Link</th>
<th>Role Keywords</th>
<th>Technical Skills</th>
</tr>
"""

for job in jobs[:100]:

    html += f"""
    <tr>
    <td>{job['company']}</td>
    <td>{job['role']}</td>
    <td>{job['location']}</td>
    <td><a href="{job['link']}">Apply</a></td>
    <td>{job['keywords']}</td>
    <td>{job['skills']}</td>
    </tr>
    """

html += "</table>"


# Send email
msg = MIMEText(html, "html")
msg["Subject"] = f"Frontend Engineering Jobs - {datetime.now().date()}"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()

print(f"Sent {len(jobs)} jobs")
