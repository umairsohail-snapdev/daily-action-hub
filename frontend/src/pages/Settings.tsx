import { useState, useEffect } from "react";
import { IntegrationCard } from "@/components/settings/IntegrationCard";
import { NotificationsSettings } from "@/components/settings/NotificationsSettings";
import { Calendar, Mail, Book, StickyNote } from "lucide-react";
import { showSuccess, showError } from "@/utils/toast";
import { api } from "@/lib/api";

const integrationsList = [
  { name: "Google Calendar", description: "Sync your meetings.", icon: <Calendar className="h-8 w-8 text-blue-500" /> },
  { name: "Gmail", description: "Draft and send emails.", icon: <Mail className="h-8 w-8 text-red-500" /> },
  { name: "Notion / Granola", description: "Retrieve meeting summaries.", icon: <Book className="h-8 w-8 text-gray-800 dark:text-white" /> },
  { name: "Obsidian", description: "Save notes and insights.", icon: <StickyNote className="h-8 w-8 text-purple-500" /> },
];

const Settings = () => {
  const [connected, setConnected] = useState<Record<string, boolean>>({
    "Google Calendar": !!localStorage.getItem("google_access_token"), // Check if Google token exists
    "Gmail": !!localStorage.getItem("google_access_token"), // Assuming same token for now
  });

  const [notificationSettings, setNotificationSettings] = useState({
    dailyBrief: true,
    unresolvedReminders: false,
  });

  // Fetch settings on load
  useEffect(() => {
    const loadSettings = async () => {
        try {
            const data = await api.getSettings();
            if (data.integrations && Object.keys(data.integrations).length > 0) {
                setConnected(prev => ({ ...prev, ...data.integrations }));
            }
            if (data.notifications) {
                setNotificationSettings(data.notifications);
            }
        } catch (error) {
            console.error("Failed to load settings", error);
        }
    };
    loadSettings();

    // Check for Notion OAuth code
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
        const handleOAuth = async () => {
            try {
                // Assuming we have an API endpoint for this callback in frontend api lib
                // Since we don't have it explicitly in api.ts, we'll fetch directly or add it.
                // Let's add a direct fetch here for simplicity or update api.ts later.
                const response = await fetch('http://localhost:8000/auth/notion/callback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                    },
                    body: JSON.stringify({ code })
                });
                
                if (response.ok) {
                    showSuccess("Notion connected successfully!");
                    setConnected(prev => ({ ...prev, "Notion / Granola": true }));
                    // Clean URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                } else {
                    showError("Failed to connect Notion.");
                }
            } catch (error) {
                console.error("Notion OAuth error", error);
                showError("Error connecting Notion.");
            }
        };
        handleOAuth();
    }
  }, []);

  // Save settings whenever they change (debounced in a real app, direct here for simplicity)
  const saveSettings = async (newConnected: any, newNotifications: any) => {
      try {
          await api.updateSettings(newConnected, newNotifications);
      } catch (error) {
          console.error("Failed to save settings", error);
      }
  };

  const handleToggleIntegration = (name: string) => {
    // Special handling for OAuth flows
    if (name === "Notion / Granola" && !connected[name]) {
        // Redirect to Notion OAuth
        window.location.href = "http://localhost:8000/auth/notion";
        return;
    }

    setConnected(prev => {
      const isConnecting = !prev[name];
      const newState = { ...prev, [name]: isConnecting };
      
      if (isConnecting) {
        showSuccess(`Successfully connected to ${name}!`);
      } else {
        showError(`Disconnected from ${name}.`);
      }
      
      saveSettings(newState, notificationSettings);
      return newState;
    });
  };

  const handleNotificationChange = (key: 'dailyBrief' | 'unresolvedReminders', value: boolean) => {
    setNotificationSettings(prev => {
        const newState = { ...prev, [key]: value };
        saveSettings(connected, newState);
        return newState;
    });
    showSuccess("Notification settings updated.");
  };

  return (
    <div className="container mx-auto max-w-4xl py-8">
      <h1 className="text-3xl font-bold mb-2">Settings</h1>
      <p className="text-muted-foreground mb-8">Manage your integrations and preferences.</p>

      <div className="space-y-8">
        <section>
          <h2 className="text-2xl font-semibold mb-4">Integrations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {integrationsList.map(integration => (
              <IntegrationCard
                key={integration.name}
                name={integration.name}
                description={integration.description}
                icon={integration.icon}
                isConnected={!!connected[integration.name]}
                onToggle={() => handleToggleIntegration(integration.name)}
              />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Notifications</h2>
          <NotificationsSettings 
            settings={notificationSettings}
            onSettingChange={handleNotificationChange}
          />
        </section>
      </div>
    </div>
  );
};

export default Settings;