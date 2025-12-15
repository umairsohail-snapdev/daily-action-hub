import { ActionItem, ActionType } from "@/types";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Send, CalendarPlus, ListTodo, BookText } from "lucide-react";
import { useState, useEffect } from "react";

const actionIcons: Record<ActionType, React.ReactNode> = {
  "Send Email": <Send className="h-4 w-4 mr-2" />,
  "Create Calendar Invite": <CalendarPlus className="h-4 w-4 mr-2" />,
  "Create Task": <ListTodo className="h-4 w-4 mr-2" />,
  "Add to Obsidian": <BookText className="h-4 w-4 mr-2" />,
};

interface ActionItemRowProps {
    item: ActionItem;
    onToggleComplete: (id: string, isCompleted: boolean) => void;
    onExecute: (action: ActionType) => Promise<string | void | null>;
}

export function ActionItemRow({ item, onToggleComplete, onExecute }: ActionItemRowProps) {
  const [action, setAction] = useState<ActionType>(item.suggestedAction);
  const [isCompleted, setIsCompleted] = useState(item.isCompleted);
  const [isExecuting, setIsExecuting] = useState(false);
  const [draftLink, setDraftLink] = useState<string | null>(null);

  useEffect(() => {
    setIsCompleted(item.isCompleted);
  }, [item.isCompleted]);

  const handleToggle = (checked: boolean) => {
      setIsCompleted(checked);
      onToggleComplete(item.id, checked);
  };

  const handleExecute = async () => {
      console.log('Execute clicked for action:', action);
      setIsExecuting(true);
      try {
        const link = await onExecute(action);
        console.log("Execution result link:", link);
        
        // Immediately mark as completed locally for visual feedback
        setIsCompleted(true);
        onToggleComplete(item.id, true);

        // FIX: Handle both string URLs and object responses with a 'link' or 'notionUrl' property
        if (typeof link === 'string') {
            console.log("Received draft link (string):", link);
            setDraftLink(link);
        } else if (link && typeof link === 'object') {
             // @ts-ignore - Check for link property in object
             const url = link.link || link.notionUrl || link.calendarUrl;
             if (url) {
                 console.log("Received draft link (object):", url);
                 setDraftLink(url);
             } else {
                 console.log("Link object missing URL property:", link);
             }
        } else if (action === "Add to Obsidian") {
            // Obsidian might not return a link if local
            console.log("Obsidian action completed.");
        } else {
            console.log("Link is not a valid format:", link);
        }
      } catch (error) {
          console.error("Error executing action:", error);
      } finally {
          setIsExecuting(false);
      }
  };

  return (
    <div className="relative flex items-center gap-4 py-2 border-b last:border-b-0 group">
      <Checkbox
        id={`action-${item.id}`}
        checked={isCompleted}
        onCheckedChange={(checked) => handleToggle(!!checked)}
        className="z-10"
        disabled={isExecuting}
      />
      <label htmlFor={`action-${item.id}`} className={`flex-grow text-sm ${isCompleted ? 'line-through text-muted-foreground' : ''} cursor-pointer`}>
        {item.description}
      </label>
      <div className="flex items-center gap-2 z-10 relative">
        {draftLink ? (
            <Button size="sm" variant="outline" className={`
                ${draftLink.includes('calendar')
                    ? 'border-purple-500 text-purple-600 hover:bg-purple-50'
                    : draftLink.includes('notion')
                    ? 'border-gray-500 text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    : 'border-blue-500 text-blue-600 hover:bg-blue-50'}
            `} asChild>
                <a href={draftLink} target="_blank" rel="noopener noreferrer">
                    {draftLink.includes('calendar')
                        ? 'Schedule Event 📅'
                        : draftLink.includes('notion')
                        ? 'View in Notion ↗'
                        : 'Open Draft ↗'}
                </a>
            </Button>
        ) : (
            <>
                <Select value={action} onValueChange={(value) => setAction(value as ActionType)} disabled={isCompleted || isExecuting}>
                <SelectTrigger className="w-[220px] text-sm">
                    <div className="flex items-center">
                    {actionIcons[action]}
                    <SelectValue placeholder="Select action" />
                    </div>
                </SelectTrigger>
                <SelectContent>
                    {Object.keys(actionIcons).map((actionKey) => (
                    <SelectItem key={actionKey} value={actionKey}>
                        <div className="flex items-center">
                        {actionIcons[actionKey as ActionType]}
                        {actionKey}
                        </div>
                    </SelectItem>
                    ))}
                </SelectContent>
                </Select>
                <Button size="sm" variant="outline" disabled={isCompleted || isExecuting} onClick={handleExecute}>
                    {isExecuting ? "..." : "Execute"}
                </Button>
            </>
        )}
      </div>
    </div>
  );
}