📧 Gmail-to-Calendar Booking Automator
A Python-based microservice for automated coaching session management.

🌟 Overview
This project automates the scheduling of coaching sessions from Gmail into Google Calendar. It was specifically designed to handle the "VA Coaching with Big Sis" workflow, ensuring that no session is missed due to manual entry errors.

🛠️ Key Features
Multi-Layered Data Extraction:

Primary: Extracts high-fidelity metadata from official .ics (iCalendar) attachments.

Secondary: Parses email subject lines using customized string-splitting logic.

Fallback: Uses Natural Language Processing (NLP) via dateparser to identify dates in the email body.

Intelligent Logic: Uses Regex and string partitioning to clean "noisy" email data (e.g., removing email addresses and timezones from subject lines).

Automatic Inbox Management: Marks processed emails as "Read" via the Gmail API to prevent duplicate bookings.

Headless Deployment: Set up as a background process (Cron Job) on a Linux-based environment (SteamOS/Steam Deck).

🧰 Tech Stack
Language: Python 3.13

APIs: Google Gmail API v1, Google Calendar API v3

Authentication: OAuth 2.0 (Google Auth Library)

Libraries: dateparser (NLP), icalendar (Attachment parsing), pytz (Timezone management)

📈 Value for VA Roles
This tool demonstrates advanced technical competency in:

API Integration: Connecting different platforms to streamline workflows.

Data Accuracy: Handling complex date formats (e.g., Sun Feb 15, 2026 10pm) with 100% reliability.

Process Automation: Reducing manual admin time to near-zero.
