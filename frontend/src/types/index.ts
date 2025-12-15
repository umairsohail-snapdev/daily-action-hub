export type ActionType = "Send Email" | "Create Calendar Invite" | "Create Task" | "Add to Obsidian";

export interface ActionItem {
  id: string;
  description: string;
  isCompleted: boolean;
  suggestedAction: ActionType;
}

export interface Meeting {
  id: string;
  title: string;
  time: string;
  participants: string[];
  type: "Online" | "Offline" | "Unrecorded";
  summary: string;
  actionItems: ActionItem[];
}

export interface DailyDashboard {
  date: string;
  isResolved: boolean;
  meetings: Meeting[];
}