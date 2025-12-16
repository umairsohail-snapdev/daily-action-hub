import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface IntegrationCardProps {
  name: string;
  description: string;
  icon: React.ReactNode;
  isConnected: boolean;
  onToggle?: () => void;
  isReadOnly?: boolean;
}

export function IntegrationCard({ name, description, icon, isConnected, onToggle, isReadOnly }: IntegrationCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-4">
          {icon}
          <div>
            <CardTitle>{name}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isReadOnly ? (
            <Button variant="secondary" className="w-full" disabled>
                {isConnected ? "Integrated by Default" : "Unavailable"}
            </Button>
        ) : (
            <Button onClick={onToggle} variant={isConnected ? "destructive" : "default"} className="w-full">
            {isConnected ? "Disconnect" : "Connect"}
            </Button>
        )}
      </CardContent>
    </Card>
  );
}