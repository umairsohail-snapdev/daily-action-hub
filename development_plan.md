# Project Blueprint: Daily Action Hub (MVP Remediation & Completion)

This blueprint outlines the focused development plan to complete the **Daily Action Hub** MVP. It is adapted from the original plan to address specific findings in the current codebase: valid Gmail/Notion-Auth logic exists, but content fetching is mocked, and background sync is blocked by client-side Google Auth.

## 1. Current State Assessment

| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Gmail Drafts** | ✅ Implemented | `backend/app/services/actions/gmail.py` contains real logic using `googleapiclient`. Needs verification. |
| **Notion Auth** | ✅ Implemented | `backend/app/routers/auth.py` handles server-side token exchange. |
| **Calendar Actions** | ✅ Implemented | Uses "Low-Code" URL templates on frontend. Valid MVP strategy. |
| **Google Auth** | ⚠️ Partial | Currently uses Implicit Flow (Client-side). **Must upgrade** to Server-Side (Refresh Tokens) for background sync. |
| **Content Fetching** | ❌ Mocked | `notion.py` and `granola.py` return hardcoded strings. Needs real API calls. |
| **Background Sync** | ❌ Missing | `scheduler.py` exists but only sends notifications; no logic to fetch/update data from APIs. |

---

## 2. Technical Decisions & Stack Adjustments

### 2.1 Google Authentication Upgrade
*   **Change:** Switch from Client-Side Implicit Flow to **Server-Side Authorization Code Flow**.
*   **Rationale:** We need an `access_token` and `refresh_token` stored securely on the backend to allow the `scheduler.py` to fetch Calendar events and send emails even when the user is offline.
*   **Implementation:**
    *   Frontend: Send `auth_code` to backend instead of token.
    *   Backend: Exchange `auth_code` for tokens; encrypt and store `refresh_token` in `User` model.

### 2.2 Content Provider Strategy
*   **Notion:** Use the stored `notion_access_token` to query the Notion Search API. Filter by title (fuzzy match with meeting title) and date (created_time).
*   **Granola:** Since Granola has no public API, we will keep the **Mock** or implement a simple "Paste Text" fallback in the UI as the primary "Fetch" mechanism for now, unless a workaround is found. *For the purpose of this plan, we will focus on enabling the Notion integration fully.*

---

## 3. Tactical Sprint Plan

### Sprint S1: Fix & Verify (Infrastructure)
**Goal:** Verify existing features work end-to-end and upgrade the authentication infrastructure to support background tasks.

**Tasks:**
1.  **Test Gmail Drafting (End-to-End):**
    *   **Action:** Manually trigger the "Draft Email" action from the frontend for a dummy meeting.
    *   **Verification:** Confirm a real draft appears in the user's Gmail `Drafts` folder.
    *   *Fix (if needed):* Debug `backend/app/services/actions/gmail.py` if permissions/tokens fail.

2.  **Test Notion Authentication:**
    *   **Action:** Go to Settings -> Connect Notion. Complete the OAuth flow.
    *   **Verification:** Check database `User` record to ensure `notion_access_token` and `bot_id` are saved.

3.  **Upgrade Google Auth (Server-Side):**
    *   **Backend:** Update `POST /api/v1/auth/google` to accept `code` instead of `token`. Implement token exchange using `google-auth-oauthlib`. Update `User` model to store `google_refresh_token`.
    *   **Frontend:** Switch `react-google-login` (or custom button) to request `response_type='code'` and `access_type='offline'`.
    *   **Verification:** Login works, and DB shows a stored refresh token.

### Sprint S2: Fill Gaps (Logic & Sync)
**Goal:** Replace mocks with real API calls and enable the background scheduler.

**Tasks:**
1.  **Implement Notion Content Fetch:**
    *   **File:** `backend/app/services/content_providers/notion.py`
    *   **Logic:** Replace mock strings. Use `requests` to call `https://api.notion.com/v1/search`.
    *   **Query:** Search for pages where `property: 'Name'` contains `meeting.title` AND `created_time` is roughly today.
    *   **Fallback:** If no page found, return `None` (UI handles manual entry).

2.  **Implement Scheduler Data Sync:**
    *   **File:** `backend/app/services/scheduler.py`
    *   **Logic:** Add a new job `sync_calendars`.
    *   **Flow:**
        1. Iterate all users.
        2. Refresh Google Access Token using stored Refresh Token.
        3. Fetch "Today's" events from Google Calendar.
        4. Update/Insert into `Meeting` table in MongoDB.
    *   **Frequency:** Run every 15-30 minutes.

3.  **Refine Dashboard "Refresh" Action:**
    *   Ensure the "Sync" button on the dashboard triggers an immediate backend sync for the current user, utilizing the new server-side sync logic.

### Sprint S3: Polish & Release
**Goal:** Final cleanup and user acceptance testing.

**Tasks:**
1.  **Error Handling:** Ensure API failures (e.g., Notion token expired, Google Auth revoked) show friendly "Re-connect" toasts in the UI.
2.  **Empty States:** Verify "No meetings today" or "No actions found" states look good.
3.  **Documentation:** Update `README.md` with instructions on how to set up the Google Cloud Project (adding redirect URIs) and Notion Integration.

---

## 4. Immediate Next Step
Begin **Sprint S1** by verifying the Gmail implementation.
