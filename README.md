# Daily Action Hub

Daily Action Hub is a productivity platform that integrates with Google Calendar, Gmail, and Notion to streamline your post-meeting workflows. It automates capturing meeting outcomes, extracting next steps via AI, and executing one-click actions.

## Features

* **Google Calendar Sync:** Automatically fetch and classify meetings (Online vs. Offline).
* **AI-Powered Summaries:** Extract actionable next steps from meeting notes using Groq (Llama 3).
* **One-Click Execution:**
    * **Send Email:** Draft follow-up emails in Gmail with context.
    * **Create Task:** Push action items directly to your Notion database.
    * **Schedule Meeting:** Generate Google Calendar invites for follow-ups.
* **Daily Dashboard:** A focused view of today's meetings and pending actions.

## Tech Stack

* **Frontend:** React (Vite), Tailwind CSS, shadcn/ui
* **Backend:** Python (FastAPI), SQLModel (SQLite/PostgreSQL)
* **AI:** Groq API (Llama 3)
* **Integrations:** Google OAuth2, Notion API

## Prerequisites

* Node.js (v18+)
* Python (v3.10+)
* **Google Cloud Console Project:**
    * APIs enabled: Google Calendar API, Gmail API.
    * **IMPORTANT:** Add `http://localhost:8000/auth/callback` (or your specific callback path) to the **Authorized Redirect URIs**.
* **Notion Integration:** Internal Integration Token.
* **Groq API Key:** For AI processing.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/daily-action-hub.git](https://github.com/your-username/daily-action-hub.git)
cd daily-action-hub
