import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

interface NotificationSettingsProps {
    settings: {
        dailyBrief: boolean;
        unresolvedReminders: boolean;
    };
    onSettingChange: (key: 'dailyBrief' | 'unresolvedReminders', value: boolean) => void;
}

export function NotificationsSettings({ settings, onSettingChange }: NotificationSettingsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Notifications</CardTitle>
        <CardDescription>Manage your email and in-app notifications.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <Label htmlFor="daily-brief">Morning Daily Brief</Label>
            <p className="text-sm text-muted-foreground">Get a summary of today's meetings every morning.</p>
          </div>
          <Switch 
            id="daily-brief" 
            checked={settings.dailyBrief}
            onCheckedChange={(value) => onSettingChange('dailyBrief', value)}
          />
        </div>
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <Label htmlFor="unresolved-reminders">Unresolved Item Reminders</Label>
            <p className="text-sm text-muted-foreground">Get notified about action items you haven't completed.</p>
          </div>
          <Switch 
            id="unresolved-reminders" 
            checked={settings.unresolvedReminders}
            onCheckedChange={(value) => onSettingChange('unresolvedReminders', value)}
          />
        </div>
      </CardContent>
    </Card>
  );
}