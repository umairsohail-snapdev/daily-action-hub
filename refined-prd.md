# Product Requirements Document (PRD)

**Product Name:** Daily Action Hub
**Version:** 1.0
**Status:** Draft

## EXECUTIVE SUMMARY

*   **Product Vision:** Daily Action Hub empowers busy professionals to reclaim their time by automating the transition from "meeting" to "action." It acts as an intelligent layer between the calendar and execution tools, ensuring that every meeting results in clear, executable next steps without the manual drudgery of reviewing recordings or transcribing notes.
*   **Core Purpose:** To bridge the gap between meeting attendance and task execution by automating the capture, summarization, and action-item creation process.
*   **Target Users:** Product Managers, Executives, and Project Coordinators who have calendar-heavy days and struggle to keep up with follow-ups.
*   **Key Features:**
    *   Automated Google Calendar Sync & Meeting Classification (Online vs. Offline).
    *   AI-Powered Action Item Extraction from meeting notes/transcripts.
    *   One-Click Action Execution (Draft Emails, Create Invites).
    *   Manual "Offline Meeting" Capture workflow.
    *   Centralized Daily Dashboard for managing today's and past commitments.
*   **Complexity Assessment:** Moderate
    *   **State Management:** Local/Basic (Syncing calendar state, tracking action item status).
    *   **External Integrations:** High count (Google Calendar, Gmail, Granola/Notion), but standard API usage.
    *   **Business Logic:** Moderate (Parsing unstructured text into structured actions).
    *   **Data Synchronization:** Basic (Daily sync).
*   **MVP Success Metrics:**
    *   Users can successfully sync their Google Calendar and see a correct classification of Online/Offline meetings.
    *   Users can generate at least one valid Action Item from a meeting summary or manual input.
    *   Users can execute an action (e.g., draft an email) directly from the dashboard.

---

## 1. USERS & PERSONAS

*   **Primary Persona: "The Back-to-Back Manager" (Alex)**
    *   **Context:** A Product Manager with 5-8 meetings a day. Uses Google Workspace, Granola, and Notion.
    *   **Goals:** Ensure team alignment, send timely follow-ups, and not drop the ball on client promises.
    *   **Needs:** A way to quickly process "what just happened" in the last meeting before the next one starts, or do it all in a batch at the end of the day without re-watching hours of video.

*   **Secondary Persona: "The Deal Closer" (Sam)**
    *   **Context:** Sales/Consulting professional.
    *   **Goals:** Send proposals and follow-up emails immediately after calls.
    *   **Needs:** Speed and accuracy in capturing client requests.

---

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 User-Requested Features (Core MVP)

*   **FR-001: Google Calendar Integration & Classification**
    *   **Description:** The system syncs with the user's Google Calendar to retrieve daily events and classifies them as "Online" (has video link) or "Offline" (no link/location based).
    *   **Entity Type:** Meeting (External Source)
    *   **User Benefit:** Provides an automatic "to-do list" of meetings to process without manual entry.
    *   **Primary User:** All Personas
    *   **Lifecycle Operations:**
        *   **Create:** Imported via API Sync.
        *   **View:** Visible on Daily Dashboard.
        *   **Edit:** Read-only (source is GCal).
        *   **Delete:** Hidden if deleted in GCal (sync update).
        *   **List/Search:** Filter by date, title.
    *   **Acceptance Criteria:**
        *   - [ ] Connect Google Calendar via OAuth.
        *   - [ ] Fetch events for the current day and past 7 days.
        *   - [ ] Auto-detect "Online" if Zoom/Meet/Teams link exists.
        *   - [ ] Auto-detect "Offline" if no video link is present.

*   **FR-002: Recording/Note Retrieval & AI Extraction**
    *   **Description:** For online meetings, the system fetches existing notes/transcripts from connected accounts (Granola/Notion). It then uses AI to extract structured action items.
    *   **Entity Type:** Content (Meeting Summary)
    *   **User Benefit:** Eliminates the need to re-read or re-watch full content to find tasks.
    *   **Primary User:** Alex (Manager)
    *   **Lifecycle Operations:**
        *   **Create:** System fetches text via API -> AI Generates Summary.
        *   **View:** User views summary on Meeting Card.
        *   **Edit:** User can manually edit the AI summary/actions.
        *   **Delete:** N/A (Part of Meeting entity).
    *   **Acceptance Criteria:**
        *   - [ ] API integration with Granola/Notion to fetch text for a specific meeting time/title.
        *   - [ ] Fallback: If no note found, prompt user for manual input.
        *   - [ ] AI parses text to identify: Action Items, Owners, Deadlines.

*   **FR-003: Action Item Management & Execution**
    *   **Description:** Users can view, edit, and execute suggested next steps. Execution triggers specific integrations (Gmail draft, Calendar Invite).
    *   **Entity Type:** Action Item
    *   **User Benefit:** Drastically reduces time to complete follow-ups.
    *   **Primary User:** All Personas
    *   **Lifecycle Operations:**
        *   **Create:** AI Auto-generation or Manual Add.
        *   **View:** Displayed in a list under the Meeting.
        *   **Edit:** Modify text, change action type (e.g., Email -> Task).
        *   **Delete:** Remove irrelevant action items.
        *   **Execute:** Trigger the associated external action.
        *   **Status:** Pending -> Completed.
    *   **Acceptance Criteria:**
        *   - [ ] Support Action Types: "Send Email" (Gmail), "Schedule Meeting" (GCal).
        *   - [ ] "Send Email" creates a draft in Gmail with pre-filled subject/body.
        *   - [ ] "Schedule Meeting" opens GCal event creation with context.
        *   - [ ] User can mark items as "Done" without triggering an integration.

*   **FR-004: Offline Meeting Workflow (Manual Entry)**
    *   **Description:** For offline meetings (or unrecorded online ones), the system prompts the user to type brief notes, which AI then converts into structured Action Items.
    *   **Entity Type:** User Input
    *   **User Benefit:** captures tasks from hallway chats or in-person meetings that have no digital trail.
    *   **Primary User:** Sam (Sales)
    *   **Lifecycle Operations:**
        *   **Create:** User types text into "Quick Note" field.
        *   **Process:** AI converts text to Action Items (FR-003).
    *   **Acceptance Criteria:**
        *   - [ ] Input field available for every meeting card.
        *   - [ ] "Generate Actions" button processes the manual text.

*   **FR-005: Daily Dashboard & History**
    *   **Description:** A two-pane view: Today's active dashboard on the left, and a collapsible 7-day history on the right.
    *   **Entity Type:** View/Container
    *   **User Benefit:** clear visibility of immediate priorities vs. past backlog.
    *   **Primary User:** All Personas
    *   **Lifecycle Operations:**
        *   **View:** Toggle between "Today" and specific past dates.
        *   **List:** Show/Hide past days.
    *   **Acceptance Criteria:**
        *   - [ ] Left Panel: "Daily Dashboard, [Date]" with today's meetings.
        *   - [ ] Right Panel: List of previous 7 days (Date headers).
        *   - [ ] Visual Indicator: Red title for past days with pending items; Blue for completed days.
        *   - [ ] Expand/Collapse functionality for past days.

### 2.2 Essential Market Features

*   **FR-006: User Authentication**
    *   **Description:** Secure login via Google OAuth (required for Calendar/Gmail scope).
    *   **Entity Type:** System
    *   **User Benefit:** Security and seamless access to Google data.
    *   **Lifecycle Operations:** Login / Logout / Revoke Access.

---

## 3. USER WORKFLOWS

### 3.1 Primary Workflow: The Morning Review
*   **Trigger:** User logs in at the start of the day.
*   **Outcome:** User has a clear view of today's schedule and outstanding tasks from yesterday.
*   **Steps:**
    1.  User opens Daily Action Hub.
    2.  System syncs with Google Calendar.
    3.  User sees "Today's Dashboard" populated with upcoming meetings.
    4.  System flags any meetings from the previous day (in Right Panel) that have "Red" status (unresolved actions).
    5.  User clicks a past date to expand it.
    6.  User reviews pending actions and clicks "Execute" (e.g., sending a draft email).
    7.  User marks the past day as complete (turns Blue).

### 3.2 Primary Workflow: Post-Meeting Processing (Online)
*   **Trigger:** An online meeting finishes, and Granola/Notion notes are available.
*   **Outcome:** Follow-up email drafted and ready.
*   **Steps:**
    1.  User sees the completed meeting on the dashboard.
    2.  User clicks "Refresh/Process" (or auto-fetch happens).
    3.  System retrieves text from Granola/Notion.
    4.  AI generates 3 Action Items: "Email slide deck," "Schedule follow-up," "Update Jira."
    5.  User reviews the "Email slide deck" item.
    6.  User clicks "Draft Email."
    7.  System opens Gmail Draft with recipient and context pre-filled.
    8.  User sends email in Gmail.
    9.  User marks item as "Done" in Hub.

### 3.3 Entity Management: Action Items
*   **Create:** AI auto-generation or User clicks "Add Action Item" on a meeting card.
*   **Edit:** User clicks text of an action item -> Inline edit mode -> Save.
*   **Delete:** User hovers over action item -> Clicks Trash icon -> Item removed.
*   **Execute:** User clicks Action Button (Email/Calendar) -> External tool opens.

---

## 4. BUSINESS RULES

*   **Meeting Visibility:** Users can only see meetings from the Calendar account they authenticated with.
*   **Action Item Ownership:** Action items are local to the user's hub view.
*   **Data Retention:** Meeting metadata is cached for performance but primarily relies on the external source of truth (Google Calendar).
*   **Offline Logic:** If a meeting has no video link, it defaults to "Offline." User can manually toggle this if it was a phone call.
*   **Status Colors:**
    *   **Red:** Day has > 0 Action Items in "Pending" state.
    *   **Blue:** Day has 0 Action Items OR all items are "Done."

---

## 5. DATA REQUIREMENTS

*   **User:**
    *   `id`: UUID
    *   `email`: String (Google Auth)
    *   `provider_tokens`: JSON (Encrypted OAuth tokens)
*   **Meeting:**
    *   `id`: String (GCal Event ID)
    *   `user_id`: UUID (FK)
    *   `title`: String
    *   `start_time`: DateTime
    *   `end_time`: DateTime
    *   `is_online`: Boolean
    *   `source_notes_id`: String (Reference to Granola/Notion doc)
    *   `notes_text`: Text (Cached summary)
*   **ActionItem:**
    *   `id`: UUID
    *   `meeting_id`: String (FK)
    *   `description`: String
    *   `type`: Enum (EMAIL, EVENT, TASK, NOTE)
    *   `payload`: JSON (Draft body, recipients, etc.)
    *   `status`: Enum (PENDING, DONE, DISMISSED)
    *   `created_at`: DateTime

---

## 6. INTEGRATION REQUIREMENTS

*   **Google Calendar API:**
    *   Purpose: Read daily events; Create follow-up meetings.
    *   Scope: `calendar.events.readonly`, `calendar.events.edit` (if scheduling).
*   **Gmail API:**
    *   Purpose: Create drafts for follow-ups.
    *   Scope: `gmail.compose`.
*   **Granola / Notion API:**
    *   Purpose: Fetch meeting notes/transcripts.
    *   Data Flow: Read-only (Fetch text).

---

## 7. FUNCTIONAL VIEWS

*   **Dashboard (Main View):**
    *   **Left Column (60%):** "Today's Agenda" - Scrollable list of Meeting Cards.
    *   **Right Column (40%):** "History" - Accordion list of past 7 days.
*   **Meeting Card Component:**
    *   Header: Time | Title | Online/Offline Badge.
    *   Body: Summary Text (Collapsible).
    *   Footer: List of Action Items with "Execute" and "Done" buttons.
*   **Settings Modal:**
    *   Connect/Disconnect Integrations (Granola, Notion).
    *   Logout.

---

## 8. MVP SCOPE & DEFERRED FEATURES

### 8.1 MVP Success Definition
The MVP is successful if a user can login with Google, see their meetings, and successfully draft a Gmail email based on AI-extracted context from a meeting note (or manual input) without errors.

### 8.2 In Scope for MVP
*   FR-001 (GCal Sync & Classify)
*   FR-002 (Recording Text Fetch & AI Extraction)
*   FR-003 (Action Item Logic & Gmail/Calendar Execution)
*   FR-004 (Manual/Offline Workflow)
*   FR-005 (Dashboard UI)
*   FR-006 (Auth)

### 8.3 Deferred Features (Post-MVP Roadmap)

*   **DF-001: Obsidian Integration**
    *   *Description:* "Add notes" button saves text to a local Obsidian vault.
    *   *Reason for Deferral:* Web-to-local filesystem integration is complex for a web-based MVP. Better suited for a desktop app or V2 with local agent.
*   **DF-002: Task Management Integration (Asana/Jira)**
    *   *Description:* "Assign task" creates ticket in external system.
    *   *Reason for Deferral:* Increases authentication scope and API complexity significantly. MVP focuses on *communication* follow-ups (Email/Meetings).
*   **DF-003: Native Mobile App**
    *   *Description:* iOS/Android version.
    *   *Reason for Deferral:* MVP validates the workflow on Web first.
*   **DF-004: Team Analytics**
    *   *Description:* Dashboards showing "Velocity" or "Resolution Rate."
    *   *Reason for Deferral:* Requires historical data accumulation; value provides later.
*   **DF-005: Voice-to-Text for Offline**
    *   *Description:* Dictate notes for offline meetings.
    *   *Reason for Deferral:* Browser APIs exist, but ensuring high-quality transcription and UI is secondary to the core text-processing flow.

---

## 9. ASSUMPTIONS & DECISIONS

*   **Assumption:** Users already have notes in Granola/Notion for online meetings. If not, the "Manual" workflow is a sufficient fallback.
*   **Decision:** We are not building a video transcriber. We are leveraging existing tools (Granola/Notion) or user input.
*   **Decision:** "Offline" is determined by lack of video link. This is a heuristic that may need refinement later.
*   **Constraint:** MVP is Web-only.

---
**PRD Complete - Ready for architect and UI/UX agents**