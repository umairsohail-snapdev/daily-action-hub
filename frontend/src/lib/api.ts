import { DailyDashboard, Meeting, ActionItem, ActionType } from "@/types";

const API_BASE_URL = "http://localhost:8000";

// Helper to get the token (mock implementation for now, replace with actual auth logic)
const getAppToken = () => {
  return localStorage.getItem("jwt_token") || "";
};

const getGoogleToken = () => {
  return localStorage.getItem("google_access_token") || "";
};

const headers = () => ({
  "Content-Type": "application/json",
  "Authorization": `Bearer ${getAppToken()}`, // For backend auth dependency (App JWT)
  "X-Google-Access-Token": getGoogleToken(), // For syncing with Google Calendar (Google Access Token)
});

// Transform Backend Meeting to Frontend Meeting
const transformMeeting = (backendMeeting: any): Meeting => {
  const startTime = new Date(backendMeeting.start_time);
  const endTime = new Date(backendMeeting.end_time);
  
  const timeString = `${startTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${endTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

  return {
    id: backendMeeting.id.toString(),
    title: backendMeeting.title,
    time: timeString,
    participants: backendMeeting.participants,
    type: backendMeeting.type,
    summary: backendMeeting.summary || "",
    actionItems: (backendMeeting.action_items || []).map((ai: any) => ({
      id: ai.id.toString(),
      description: ai.description,
      isCompleted: ai.is_completed,
      suggestedAction: ai.suggested_action as ActionType,
    })),
  };
};

export const api = {
  syncMeetings: async (): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/meetings/sync`, {
      method: "POST",
      headers: headers(),
    });
    if (!response.ok) throw new Error("Failed to sync meetings");
  },

  getTodaysDashboard: async (): Promise<DailyDashboard> => {
    const response = await fetch(`${API_BASE_URL}/dashboard/today`, {
      headers: headers(),
    });
    if (!response.ok) throw new Error("Failed to fetch dashboard");
    
    const data = await response.json();
    return {
      date: data.date,
      isResolved: data.is_resolved,
      meetings: data.meetings.map(transformMeeting),
    };
  },

  getPastDashboards: async (): Promise<DailyDashboard[]> => {
    const response = await fetch(`${API_BASE_URL}/dashboard/history`, {
      headers: headers(),
    });
    if (!response.ok) throw new Error("Failed to fetch history");
    
    const data = await response.json();
    return data.map((d: any) => ({
      date: d.date,
      isResolved: d.is_resolved,
      meetings: d.meetings.map(transformMeeting),
    }));
  },

  processMeeting: async (meetingId: string, content: string): Promise<Meeting> => {
    const response = await fetch(`${API_BASE_URL}/meetings/${meetingId}/process`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error("Failed to process meeting");
    
    const data = await response.json();
    return transformMeeting(data);
  },

  analyzeMeeting: async (meetingId: string, notesText: string): Promise<Meeting> => {
    const response = await fetch(`${API_BASE_URL}/meetings/${meetingId}/analyze`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ notes_text: notesText }),
    });
    if (!response.ok) throw new Error("Failed to analyze meeting");
    
    const data = await response.json();
    return transformMeeting(data);
  },

  fetchMeetingNotes: async (meetingId: string): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/meetings/${meetingId}/fetch-notes`, {
      headers: headers(),
    });
    if (!response.ok) throw new Error("Failed to fetch notes");
    
    const data = await response.json();
    return data.notes || "";
  },

  updateActionItem: async (actionId: string, updates: Partial<ActionItem>): Promise<ActionItem> => {
    // Map frontend keys to backend keys
    const backendUpdates: any = {};
    if (updates.description !== undefined) backendUpdates.description = updates.description;
    if (updates.isCompleted !== undefined) backendUpdates.is_completed = updates.isCompleted;
    if (updates.suggestedAction !== undefined) backendUpdates.suggested_action = updates.suggestedAction;

    const response = await fetch(`${API_BASE_URL}/actions/${actionId}`, {
      method: "PATCH",
      headers: headers(),
      body: JSON.stringify(backendUpdates),
    });
    if (!response.ok) throw new Error("Failed to update action item");
    
    const data = await response.json();
    return {
      id: data.id.toString(),
      description: data.description,
      isCompleted: data.is_completed,
      suggestedAction: data.suggested_action as ActionType,
    };
  },

  createActionItem: async (meetingId: string, description: string): Promise<ActionItem> => {
    const response = await fetch(`${API_BASE_URL}/actions/`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        meeting_id: parseInt(meetingId),
        description: description,
        suggested_action: "Create Task"
      }),
    });
    if (!response.ok) throw new Error("Failed to create action item");
    
    const data = await response.json();
    return {
      id: data.id.toString(),
      description: data.description,
      isCompleted: data.is_completed,
      suggestedAction: data.suggested_action as ActionType,
    };
  },

  executeAction: async (actionId: string, params: any = {}): Promise<any> => {
    // For MVP, we use the same access token for both backend auth and google auth
    // In a real app, you might send them separately
    const response = await fetch(`${API_BASE_URL}/actions/${actionId}/execute`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        user_token: getGoogleToken(), // Action executors might need Google permissions
        params: params
      }),
    });
    if (response.status === 401) {
      throw new Error("Unauthorized");
    }
    if (!response.ok) throw new Error("Failed to execute action");
    return await response.json();
  },

  getSettings: async (): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/auth/settings`, {
      headers: headers(),
    });
    if (!response.ok) throw new Error("Failed to fetch settings");
    return await response.json();
  },

  updateSettings: async (integrations: any, notifications: any): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/auth/settings`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ integrations, notifications }),
    });
    if (!response.ok) throw new Error("Failed to update settings");
  },

  signup: async (email: string, password: string, name?: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password, name }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Signup failed");
    }
    return await response.json();
  },

  login: async (email: string, password: string): Promise<any> => {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }
    return await response.json();
  },

  googleLogin: async (token: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/auth/google`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Google login failed");
    }
    return await response.json();
  }
};