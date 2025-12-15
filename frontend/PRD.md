---
title: Product Requirements Document
app: whispering-platypus-swim
created: 2025-12-09T20:30:44.078Z
version: 1
source: Deep Mode PRD Generation
---

Here is the finalized Product Requirements Document for Daily Action Hub, with the clarification answers incorporated.

***

### **Product Requirements Document (PRD)**

**Product Name:** Daily Action Hub
**Product Type:** Web Application

**1. Overview**
For most managers, executives, or investors, days are filled with back-to-back meetings. At the end of the day, urgent work (emails, fire-fighting, operational tasks) often takes precedence over important follow-ups. Critical insights and next steps from meetings frequently slip through the cracks.

Daily Action Hub is a productivity platform that integrates directly with Google Calendar to streamline execution. It:
*   Detects whether meetings are online or offline.
*   Retrieves recordings (via Granola and/or Notion) when available.
*   Summarizes them and extracts actionable next steps.
*   Converts those into context-specific, one-click actions (e.g., “Send follow-up email”).

For offline or unrecorded meetings, the system prompts the user to manually enter next steps, which are then structured into action items.

The ultimate goal: reduce friction between meetings and execution, ensuring nothing important is lost.

**2. Goals & Objectives**
*   Automate the capture and processing of meeting outcomes.
*   Transform passive notes into directly actionable tasks.
*   Eliminate the need to rewatch recordings or manually transcribe notes.
*   Provide a centralized daily workflow hub for all meeting follow-ups.
*   Build trust by keeping users in control (edit/confirm suggestions).
*   Reduce decision fatigue and cognitive load for busy professionals.

**3. Target Users**
*   **Primary Users:**
    *   Product Managers, Executives, Team Leads, and Project Coordinators.
    *   Professionals with high meeting loads and a mix of online and offline engagements.
*   **Secondary Users:**
    *   Consultants, sales teams, and other client-facing professionals.
    *   Distributed or hybrid teams reliant on recorded meetings for asynchronous collaboration.

**4. User Stories**
*   As a user, I want my Google Calendar scanned daily so I can see which meetings were online vs. offline.
*   As a user, I want online meetings with recordings summarized so I don’t need to rewatch them.
*   As a user, I want AI to extract next steps and propose concrete actions.
*   As a user, I want to confirm or edit next steps before execution so I stay in control.
*   As a user, I want to be prompted for to-dos from my offline meetings so I don’t forget them.
*   As a user, I want all my meeting summaries and actions visible in one dashboard.
*   As a user, I want integrations with Gmail, Google Calendar, Notion, and Granola so my tools stay in sync.
*   As a user, I want overdue or unresolved tasks clearly highlighted so I don’t lose track.

**5. Key Features**

**5.1 Google Calendar Integration**
*   Daily sync of all meetings from the user's connected Google Calendar.
*   Automatic classification of meetings:
    *   **Online:** A Zoom, Google Meet, or Microsoft Teams link is detected in the event details.
    *   **Offline:** A physical location is listed, or no online meeting link is present.

**5.2 Recording Retrieval**
*   For online meetings, the system attempts to match meeting metadata (title, time, participants) against entries in the user's connected Granola and/or Notion accounts.
*   If a match is found, it retrieves the transcript and/or recording links.
*   If no match is found, the meeting is marked as “unrecorded,” and the system triggers the fallback workflow for manual entry.

**5.3 AI Evaluation**
*   Parses the retrieved summaries and transcripts from Granola/Notion.
*   Flags key discussion items and decisions.
*   Extracts explicit next steps, identifying the core task, assigned owner (if mentioned), and due date (if mentioned).
*   Applies NER (Named Entity Recognition) to accurately identify participants, deadlines, and other key entities.

**5.4 Action Item Generation**
The system converts extracted next steps into interactive tasks through a two-step process:

1.  **Automatic Action Classification:**
    *   The system analyzes the text of each next step to predict the most likely user intent using keyword detection and NLP.
    *   Initial mapping includes:
        *   Keywords like "follow up," "email," "reach out" → **Send Email**
        *   Keywords like "schedule," "meet," "book" → **Create Calendar Invite**
        *   Keywords like "assign," "task," "do" → **Create Task**
        *   Keywords like "note," "remember," "log" → **Add to Obsidian**

2.  **User Confirmation and Control:**
    *   The system's suggested action is presented in a dropdown menu next to the action item, allowing the user to confirm the choice or select a different action if the initial classification was incorrect.
    *   The user must explicitly approve or edit any action before it is executed.

**Action-Specific Workflows:**
*   **Send Email:**
    *   Triggers a Gmail draft pre-filled with the following fields:
        *   **Recipient(s):** Automatically populated from the meeting participants.
        *   **Subject:** Derived from the meeting title or context of the action item.
        *   **Body:** A generated message providing context for the follow-up.
    *   The user can edit all fields within the Daily Action Hub UI before sending.
*   **Create Calendar Invite:** Suggests available slots via Google Calendar.
*   **Create Task:** Pushes the task into the user's connected system (e.g., Notion, Granola, with future support for Asana, Jira).
*   **Add to Obsidian:** Appends the note to a designated file in the user's Obsidian vault.

**5.5 Fallback Workflow**
*   When the AI cannot confidently infer next steps from a recording, or for unrecorded meetings, the system prompts the user: “What should the next step be?”
*   User input is converted into a structured action item with an associated action button.

**5.6 Offline Meeting Workflow**
*   For meetings classified as offline, the system prompts: “You had an offline meeting with [Participants]. Any to-dos?”
*   The user can enter tasks in a text field, which are then structured into actionable items.

**5.7 Daily Dashboard**
*   **Today’s Dashboard (Left Panel):**
    *   A view of today’s meetings (online/offline).
    *   Associated summaries (auto-generated or manual).
    *   A list of next steps with their corresponding action dropdowns.
    *   Filter/search functionality by meeting title, participant, or keyword.
    *   Pending/unconfirmed actions are clearly flagged for user attention.
*   **Past Dashboards (Right Panel):**
    *   Displays the last 7 days of dashboards, collapsed by default.
    *   Users can expand/collapse each day using an arrow icon.
    *   Dashboard titles are color-coded for quick status checks:
        *   **Red:** Contains unresolved or pending items.
        *   **Blue:** All items are resolved.
    *   An option to "View More" allows users to load older dashboards.

**5.8 Notifications & Reminders**
*   Optional email or in-app notifications for unresolved items from previous days.
*   A morning “Daily Brief” email summarizing today’s meetings and any outstanding tasks.

**5.9 Onboarding & Settings**
*   Simple sign-in via Google OAuth.
*   A clear onboarding flow that explains the required permissions (Google Calendar access, Granola/Notion integration, Gmail draft creation) and their purpose.
*   A settings page to:
    *   Manage and toggle integrations.
    *   Configure notification preferences.
    *   Set default destinations for tasks and notes (e.g., a specific Notion database or Obsidian file).

**6. Non-Goals**
*   Building a native recording or transcription service; we will only integrate with existing tools.
*   Replacing full-fledged project management systems like Asana or Jira; we aim to be a bridge to them.
*   For the MVP, we will not support non-Google calendar platforms (Outlook support may be considered post-MVP).

**7. Success Metrics**
*   **Automation Coverage:** % of online meetings successfully matched to a transcript/summary.
*   **Action Accuracy:** % of AI-suggested next steps accepted by the user without edits.
*   **User Engagement:** Average number of actions executed via the Hub per user per week.
*   **Time Saved:** Qualitative feedback and quantitative reduction in time spent on manual follow-ups.
*   **Retention:** Daily Active Users (DAU) / Weekly Active Users (WAU) over a 90-day period.
*   **Resolution Rate:** % of daily dashboards that are fully resolved (i.e., turn from red to blue).

**8. Technical Requirements**
*   **Integrations:**
    *   Google Calendar API (for reading meeting metadata and creating new invites).
    *   Gmail API (for drafting and sending emails with pre-filled context).
    *   Granola/Notion APIs (for fetching transcripts and pushing tasks).
    *   Optional: Obsidian integration for notes (e.g., via local file system access or community plugins).
*   **AI Components:**
    *   NLP summarization parser (for processing Granola/Notion outputs).
    *   Action classification model (using a simple NLP classifier or LLM prompt to map natural language next steps to specific actions like 'Send Email' or 'Create Task').
    *   NER (Named Entity Recognition) for identifying participants, deadlines, and tasks within meeting notes.
*   **Web Application:**
    *   Frontend: React/Next.js or similar modern framework.
    *   Backend: Node.js/Python.
    *   Database: PostgreSQL or MongoDB.
    *   Authentication: Secure login via Google OAuth.
    *   Notifications: System for handling email and in-app alerts.
*   **Security:**
    *   OAuth 2.0 for all third-party integrations (no raw credentials stored).
    *   Data encryption at rest and in transit.
    *   Granular user permissions and clear consent flows.
    *   GDPR compliance, including data deletion and export capabilities.
*   **Scalability:**
    *   Architecture must handle calendars with 1,000+ events per month per user.
    *   Designed to support multi-user organization accounts in future phases.

**9. Future Roadmap (Post-MVP)**
*   Integration with Microsoft Outlook Calendar & Slack.
*   Deeper task system integrations (Asana, Jira, Trello).
*   Voice-to-text capture for quickly adding notes from offline meetings.
*   Team/Organization-level analytics dashboards (e.g., follow-up velocity, resolution rates).
*   A mobile application for on-the-go review and execution of follow-ups.