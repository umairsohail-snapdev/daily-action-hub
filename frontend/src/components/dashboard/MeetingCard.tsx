import { Meeting, ActionType } from "@/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Users, Clock, Sparkles } from "lucide-react";
import { ActionItemRow } from "./ActionItemRow";
import { AddActionItem } from "./AddActionItem";

interface MeetingCardProps {
    meeting: Meeting;
    onToggleActionItem: (actionId: string, isCompleted: boolean) => void;
    onAddActionItem: (description: string) => Promise<void> | void;
    onExecuteAction: (id: string, action: ActionType) => void;
    onGenerateSummary?: (meetingId: string) => void;
}

export function MeetingCard({ 
    meeting, 
    onToggleActionItem, 
    onAddActionItem, 
    onExecuteAction, 
    onGenerateSummary 
}: MeetingCardProps) {
    
    const getBadgeVariant = (type: Meeting["type"]) => {
        switch (type) {
            case "Online":
                return "default";
            case "Offline":
                return "secondary";
            case "Unrecorded":
                return "outline";
            default:
                return "default";
        }
    };

    const placeholderText = meeting.type === 'Online' 
        ? "Add another action item..."
        : `Any to-dos for your ${meeting.type.toLowerCase()} meeting?`;

    return (
        <Card className="transition-all hover:shadow-md border-l-4 border-l-primary/20">
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                    <div className="space-y-1">
                        <CardTitle className="text-xl leading-tight">{meeting.title}</CardTitle>
                        <CardDescription className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm mt-1">
                            <span className="flex items-center gap-1.5 text-muted-foreground">
                                <Clock className="h-3.5 w-3.5" /> {meeting.time}
                            </span>
                            {meeting.participants.length > 0 && (
                                <span className="flex items-center gap-1.5 text-muted-foreground">
                                    <Users className="h-3.5 w-3.5" /> {meeting.participants.join(", ")}
                                </span>
                            )}
                        </CardDescription>
                    </div>
                    <Badge variant={getBadgeVariant(meeting.type)} className="ml-2 shrink-0">{meeting.type}</Badge>
                </div>
            </CardHeader>
            <CardContent>
                <div className="mb-6 p-3 bg-muted/30 rounded-lg">
                    <p className="text-sm text-muted-foreground leading-relaxed">
                        {meeting.summary || "No summary available for this meeting."}
                    </p>
                    {onGenerateSummary && (
                        <Button
                            variant="secondary"
                            size="sm"
                            className="mt-3 w-full sm:w-auto"
                            onClick={() => onGenerateSummary(meeting.id)}
                        >
                            <Sparkles className="mr-2 h-3.5 w-3.5 text-amber-500" />
                            Generate Summary & Actions
                        </Button>
                    )}
                </div>
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Action Items</h4>
                        <Badge variant="outline" className="text-xs font-normal text-muted-foreground">
                            {meeting.actionItems.length}
                        </Badge>
                    </div>
                    {meeting.actionItems.length > 0 ? (
                        meeting.actionItems.map((item) => (
                            <ActionItemRow
                                key={item.id}
                                item={item}
                                // FIX: Wrap this to pass item.id explicitly, matching onExecute pattern
                                onToggleComplete={(id, isCompleted) => onToggleActionItem(id, isCompleted)}
                                onExecute={async (action) => {
                                    try {
                                        // @ts-ignore - Ensure onExecuteAction returns the result
                                        const result = await onExecuteAction(item.id, action as ActionType);
                                        return result;
                                    } catch (e) {
                                        console.error("MeetingCard execution failed:", e);
                                        return null;
                                    }
                                }}
                            />
                        ))
                    ) : (
                        <p className="text-sm text-muted-foreground italic text-center py-2">
                            No action items yet. Add one below.
                        </p>
                    )}
                    <AddActionItem 
                        onAddItem={onAddActionItem} 
                        placeholderText={placeholderText} 
                    />
                </div>
            </CardContent>
        </Card>
    );
}