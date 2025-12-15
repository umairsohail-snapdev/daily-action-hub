import { DailyDashboard, Meeting } from "@/types";

export const today_meetings: Meeting[] = [
  {
    id: "m1",
    title: "Project Phoenix Sync",
    time: "9:00 AM - 10:00 AM",
    participants: ["Alice", "Bob", "Charlie"],
    type: "Online",
    summary: "Discussed Q3 roadmap and resource allocation. Key decisions were made on the new feature set.",
    actionItems: [
      { id: "a1", description: "Draft Q3 roadmap announcement email.", isCompleted: false, suggestedAction: "Send Email" },
      { id: "a2", description: "Schedule follow-up with design team.", isCompleted: false, suggestedAction: "Create Calendar Invite" },
    ],
  },
  {
    id: "m2",
    title: "Client Check-in: Acme Corp",
    time: "11:30 AM - 12:00 PM",
    participants: ["David", "Eve"],
    type: "Offline",
    summary: "Met at their office. They are happy with the progress but requested a new report.",
    actionItems: [
      { id: "a3", description: "Create task for generating the new quarterly report.", isCompleted: false, suggestedAction: "Create Task" },
    ],
  },
  {
    id: "m3",
    title: "Internal Brainstorming",
    time: "2:00 PM - 3:30 PM",
    participants: ["Frank", "Grace", "Heidi"],
    type: "Unrecorded",
    summary: "No recording available. Manually entered notes.",
    actionItems: [
      { id: "a4", description: "Log brainstorming notes and ideas into Obsidian.", isCompleted: false, suggestedAction: "Add to Obsidian" },
      { id: "a5", description: "Follow up with Heidi on the marketing plan.", isCompleted: true, suggestedAction: "Send Email" },
    ],
  },
];

export const past_dashboards: DailyDashboard[] = [
  {
    date: "2023-10-25",
    isResolved: true,
    meetings: [
      {
        id: "pd1-m1",
        title: "Weekly Standup",
        time: "10:00 AM",
        participants: ["Team"],
        type: "Online",
        summary: "All tasks completed.",
        actionItems: [
          { id: "pd1-a1", description: "Prepare next week's sprint board.", isCompleted: true, suggestedAction: "Create Task" },
        ],
      },
    ],
  },
  {
    date: "2023-10-24",
    isResolved: false,
    meetings: [
      {
        id: "pd2-m1",
        title: "Design Review",
        time: "1:00 PM",
        participants: ["Alice", "Design Team"],
        type: "Online",
        summary: "Feedback collected, revisions needed.",
        actionItems: [
          { id: "pd2-a1", description: "Send feedback summary to the design lead.", isCompleted: true, suggestedAction: "Send Email" },
          { id: "pd2-a2", description: "Schedule a final review for Friday.", isCompleted: false, suggestedAction: "Create Calendar Invite" },
        ],
      },
    ],
  },
  {
    date: "2023-10-23",
    isResolved: true,
    meetings: [
       {
        id: "pd3-m1",
        title: "Budget Planning",
        time: "11:00 AM",
        participants: ["Charlie", "Finance"],
        type: "Offline",
        summary: "Q4 budget approved.",
        actionItems: [],
      },
    ],
  },
];

export const more_past_dashboards: DailyDashboard[] = [
    {
        date: "2023-10-22",
        isResolved: false,
        meetings: [
            {
                id: "pd4-m1",
                title: "Marketing Strategy",
                time: "3:00 PM",
                participants: ["Grace", "Marketing Team"],
                type: "Online",
                summary: "Discussed Q1 campaigns.",
                actionItems: [
                    { id: "pd4-a1", description: "Finalize campaign brief.", isCompleted: false, suggestedAction: "Create Task" },
                ],
            },
        ],
    },
    {
        date: "2023-10-21",
        isResolved: true,
        meetings: [
            {
                id: "pd5-m1",
                title: "1-on-1 with Bob",
                time: "11:00 AM",
                participants: ["Alice", "Bob"],
                type: "Offline",
                summary: "Performance review.",
                actionItems: [
                    { id: "pd5-a1", description: "Update Bob's development plan.", isCompleted: true, suggestedAction: "Add to Obsidian" },
                ],
            },
        ],
    }
]