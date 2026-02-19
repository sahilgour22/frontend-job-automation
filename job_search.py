import requests
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['EMAIL_PASSWORD']

jobs = []

# RemoteOK API
try:
    response = requests.get("https://remoteok.com/api")
    data = response.json()

    for job in data:

        if isinstance(job, dict):

            title = str(job.get("position", "")).lower()

            if any(x in title for x in ["frontend", "react", "front-end", "ui"]):

                jobs.append({
                    "company": job.get("company", "Remote Company"),
                    "role": job.get("position"),
                    "location": "Remote",
                    "link": f"https://remoteok.com{job.get('url','')}",
                    "keywords": "Frontend, React, UI, Web, Product",
                    "skills": "React, Next.js, TypeScript, CSS, API"
                })

except Exception as e:
    print(e)


# Build email HTML
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

for job in jobs[:50]:

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
