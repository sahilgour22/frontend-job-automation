import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Your email credentials from GitHub Secrets
import os
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['EMAIL_PASSWORD']

jobs = []

# Search Wellfound API (startup jobs)
url = "https://api.ashbyhq.com/posting-api/job-board/wellfound"

try:
    response = requests.get(url)
    data = response.json()

    for job in data.get("jobs", []):

        title = job.get("title", "").lower()

        if any(keyword in title for keyword in ["frontend", "react", "ui", "front-end"]):

            jobs.append({
                "company": job.get("companyName", "Startup"),
                "role": job.get("title"),
                "location": job.get("location", "Remote"),
                "link": job.get("applyUrl"),
                "keywords": "Frontend, React, UI, Product, Web",
                "skills": "React, Next.js, TypeScript, CSS, API"
            })

except:
    pass


# Build HTML table
html = """
<h2>Daily Frontend Jobs</h2>
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

for job in jobs:
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
msg["Subject"] = f"Frontend Jobs {datetime.now().date()}"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()
