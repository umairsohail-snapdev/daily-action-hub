import { useState, useEffect } from "react";
import { IntegrationCard } from "@/components/settings/IntegrationCard";
import { NotificationsSettings } from "@/components/settings/NotificationsSettings";
import { Calendar, Mail, Book } from "lucide-react";
import { showSuccess, showError } from "@/utils/toast";
import { api } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
 
const integrationsList = [
  { name: "Google Calendar", description: "Sync your meetings.", icon: <Calendar className="h-8 w-8 text-blue-500" /> },
  { name: "Gmail", description: "Draft and send emails.", icon: <Mail className="h-8 w-8 text-red-500" /> },
];
 
const Settings = () => {
  const [connected, setConnected] = useState<Record<string, boolean>>({
    "Google Calendar": true,
    "Gmail": true,
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
    // Removed Notion OAuth handling logic
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
            {integrationsList.map(integration => {
                const isGoogleService = integration.name === "Google Calendar" || integration.name === "Gmail";
                return (
                  <IntegrationCard
                    key={integration.name}
                    name={integration.name}
                    description={integration.description}
                    icon={integration.icon}
                    isConnected={isGoogleService ? true : !!connected[integration.name]}
                    isReadOnly={isGoogleService}
                    onToggle={() => handleToggleIntegration(integration.name)}
                  />
                );
            })}
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