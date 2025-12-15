# Project Analysis Report: Daily Action Hub

## Executive Summary
The current codebase represents an early-stage MVP (Minimum Viable Product). While the basic structure for a React frontend and FastAPI backend is in place, the application relies heavily on mock implementations, placeholders, and fragile authentication mechanisms. Critical integrations defined in the PRD (Granola, Notion, Action Execution) are missing.

## detailed Findings

### 1. Authentication & Security (Critical)
*   **Current State:** The application uses a "Client-Side Only" auth model. The frontend obtains a Google Access Token and sends it to the backend.
*   **Backend (`backend/app/auth.py`):** Validates the token against Google's UserInfo endpoint on *every request*.
*   **Risks:**
    *   **No Session Management:** There is no server-side session (JWT/Cookie). Reliability depends entirely on the short-lived Google Access Token.
    *   **No Token Refresh:** When the Google token expires (usually ~1 hour), the user will be abruptly locked out. There is no logic to handle refresh tokens.
    *   **Security:** Passing the raw Google Access Token as the primary authentication credential to your own API is non-standard. Typically, you would exchange it for a session token (JWT) for your own app.

### 2. Google Calendar Integration
*   **Current State:** Partially Functional.
*   **Backend (`backend/app/services/calendar.py`):** Contains valid logic to fetch events from the primary calendar.
*   **Constraint:** It relies on the `X-Google-Access-Token` header. Since there is no background sync or refresh token storage, the sync can *only* happen when the user is actively logged in and triggers it manually (or on page load).

### 3. Content Retrieval (Missing)
*   **Current State:** Non-Existent.
*   **Gap:** The PRD mentions integration with **Granola**, **Notion**, or **Otter** to retrieve meeting notes/transcripts.
*   **Implementation:** The `POST /meetings/{id}/process` endpoint exists but expects the `content` to be provided in the request body. There is no backend logic to fetch this content from external APIs.

### 4. Action Execution (Missing)
*   **Current State:** UI Placeholders.
*   **Gap:**
    *   **Send Email:** Frontend shows a toast. No backend endpoint or Gmail API integration exists.
    *   **Create Task:** Frontend shows a toast. No integration with Notion/Asana.
    *   **Create Calendar Invite:** Frontend shows a toast. No Google Calendar write integration.
    *   **Add to Obsidian:** Frontend shows a toast. No mechanism to write to local files (browser security restriction) or interact with an Obsidian plugin.

### 5. AI Integration
*   **Current State:** Basic Wrapper.
*   **Backend (`backend/app/services/ai.py`):** Connects to OpenAI.
*   **Gap:** The prompt is generic. It does not actually have access to the *context* of previous meetings or specific user preferences.

## Recommended Remediation Plan

### Phase 1: Solidify Foundation (Auth & State)
1.  **Implement Real Auth:**
    *   Update Backend to issue its own **JWT** after verifying the Google Token.
    *   Store the **Google Refresh Token** securely in the backend database (encrypted) to allow background syncing and token refreshing.
2.  **Database Migration:** Ensure the `User` model can store OAuth credentials (refresh token, expiry).

### Phase 2: Content Integrations
1.  **Granola/Notion Connectors:** Create a standard interface (`ContentProvider`) in the backend.
2.  **Implement Adapters:** Write specific adapters for Granola (if API exists) or Notion to fetch page content based on meeting dates/titles.

### Phase 3: Action Execution Engine
1.  **Backend Endpoints:** Create `POST /actions/{id}/execute` endpoint.
2.  **Service Layer:** Implement services for:
    *   `GmailService` (using the stored Google credentials).
    *   `NotionService` (for creating tasks).
    *   `CalendarService` (add `create_event` method).

### Phase 4: Frontend Polish
1.  **Remove Mocks:** Update `api.ts` to handle the new JWT auth flow.
2.  **Error Handling:** Add graceful handling for expired tokens (auto-refresh or redirect to login).