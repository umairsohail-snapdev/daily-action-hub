# Daily Action Hub

Daily Action Hub is a productivity platform that integrates with Google Calendar, Gmail, and Notion to streamline your post-meeting workflows. It automates capturing meeting outcomes, extracting next steps via AI, and executing one-click actions.

![Daily Action Hub Dashboard](./public/placeholder.svg)

## Features

*   **Google Calendar Sync:** Automatically fetch and classify meetings (Online vs. Offline).
*   **AI-Powered Summaries:** Extract actionable next steps from meeting notes.
*   **One-Click Execution:**
    *   **Send Email:** Draft follow-up emails in Gmail with context.
    *   **Create Task:** Push action items directly to your Notion database.
    *   **Schedule Meeting:** Generate Google Calendar invites for follow-ups.
*   **Daily Dashboard:** A focused view of today's meetings and pending actions.
*   **Automated Daily Brief:** (Optional) Morning email digest of your schedule.

## Tech Stack

*   **Frontend:** React (Vite), Tailwind CSS, shadcn/ui
*   **Backend:** Python (FastAPI), SQLModel (SQLite)
*   **AI:** Groq API (Llama 3)
*   **Integrations:** Google OAuth2, Notion API

## Prerequisites

*   Node.js (v18+)
*   Python (v3.10+)
*   Google Cloud Console Project (with Calendar & Gmail APIs enabled)
*   Notion Integration (Internal Integration Token)
*   Groq API Key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/daily-action-hub.git
cd daily-action-hub
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=sqlite:///./daily_action_hub_v2.db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173

# Google Integration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# AI Provider
GROQ_API_KEY=your_groq_api_key

# Notion Integration (Optional if using OAuth flow, required for manual dev)
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
```

**Run Database Migrations:**
```bash
python migrate_db.py
```

**Start the Server:**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Access the app at `http://localhost:5173`.

## Deployment Guide

### GitHub Repository
You can safely push this code to GitHub. The root `.gitignore` is configured to exclude sensitive files like `.env`, `venv/`, and `node_modules/`.

1.  Initialize Git:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    ```
2.  Create a repo on GitHub and push:
    ```bash
    git remote add origin https://github.com/your-username/daily-action-hub.git
    git push -u origin main
    ```

### Production Deployment
*   **Frontend:** Vercel or Netlify (Connect your GitHub repo).
*   **Backend:** Render, Railway, or Heroku.
    *   Ensure you set the Environment Variables in your deployment provider's dashboard.
    *   Update `FRONTEND_URL` in backend env and API endpoint in frontend config.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)