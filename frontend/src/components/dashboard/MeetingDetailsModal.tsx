import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Loader2, Sparkles, BookText } from "lucide-react";
import { Meeting, ActionType } from "@/types";
import { ActionItemRow } from "./ActionItemRow";
import { AddActionItem } from "./AddActionItem";
import { showSuccess, showError } from "@/utils/toast";
import { toast } from "sonner";
import { api } from "@/lib/api";

interface MeetingDetailsModalProps {
  meeting: Meeting | null;
  isOpen: boolean;
  onClose: () => void;
  onAnalyze: (meetingId: string, notes: string) => Promise<Meeting | void>;
  onExecuteAction: (id: string, action: ActionType) => Promise<string | void | null> | void;
  onToggleActionItem: (actionId: string, isCompleted: boolean) => void;
  onAddActionItem: (description: string) => Promise<void>;
}

export function MeetingDetailsModal({
  meeting,
  isOpen,
  onClose,
  onAnalyze,
  onExecuteAction,
  onToggleActionItem,
  onAddActionItem
}: MeetingDetailsModalProps) {
  const [notes, setNotes] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isFetchingNotes, setIsFetchingNotes] = useState(false);
  
  // FIX 1: Local state to show new items immediately
  const [localActionItems, setLocalActionItems] = useState(meeting?.actionItems || []);

  useEffect(() => {
    if (meeting) {
      // Sync local state whenever the parent data updates
      setLocalActionItems(meeting.actionItems);

      const content = meeting.summary || (meeting as any).description || "";
      if (content) {
          setNotes(content);
      }
    }
  }, [meeting]);

  const handleFetchNotes = async () => {
      if (!meeting) return;
      setIsFetchingNotes(true);
      try {
          const fetchedNotes = await api.fetchMeetingNotes(meeting.id);
          // Backend now returns { notes: "..." } directly
          if (fetchedNotes && fetchedNotes.notes) {
              setNotes(fetchedNotes.notes);
              showSuccess("Notes fetched from Notion!");
          } else if (fetchedNotes && typeof fetchedNotes.notes === 'string' && fetchedNotes.notes === "") {
             toast.info("No matching notes found in Notion.");
          } else {
             // Fallback for older API structure
             setNotes(fetchedNotes); 
             showSuccess("Notes fetched!");
          }
      } catch (error) {
          console.error("Failed to fetch notes:", error);
          showError("Failed to fetch notes from Notion.");
      } finally {
          setIsFetchingNotes(false);
      }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
        // @ts-ignore
        const updatedMeeting = await onAnalyze(meeting!.id, notes);
        
        // FIX 2: Update local list immediately with the response data
        if (updatedMeeting && updatedMeeting.actionItems) {
            setLocalActionItems(updatedMeeting.actionItems);
        }
    } catch (error) {
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (!meeting) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {meeting.title}
            <Badge variant={meeting.type === 'Online' ? 'default' : 'secondary'}>{meeting.type}</Badge>
          </DialogTitle>
          <DialogDescription>
            {meeting.time} • {meeting.participants.join(", ")}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-grow flex flex-col gap-4 overflow-hidden">
            <div className="flex-1 flex flex-col min-h-[150px]">
                <div className="flex justify-between items-center mb-2">
                    <h4 className="text-sm font-semibold">Meeting Notes / Transcript</h4>
                    <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 text-xs"
                        onClick={handleFetchNotes}
                        disabled={isFetchingNotes}
                    >
                        {isFetchingNotes ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : <BookText className="h-3 w-3 mr-1" />}
                        Fetch from Notion
                    </Button>
                </div>
                <Textarea
                    placeholder="Paste your meeting notes or transcript here to analyze..."
                    className="flex-grow resize-none"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                />
                <Button
                    className="mt-2"
                    onClick={handleAnalyze}
                    disabled={!notes.trim() || isAnalyzing}
                >
                    {isAnalyzing ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Analyzing...
                        </>
                    ) : (
                        <>
                            <Sparkles className="mr-2 h-4 w-4" />
                            Generate Action Items
                        </>
                    )}
                </Button>
            </div>

            <Separator />

            <div className="flex-1 flex flex-col overflow-hidden">
                {/* FIX 3: Display count from localActionItems */}
                <h4 className="text-sm font-semibold mb-2">Action Items ({localActionItems.length})</h4>
                <ScrollArea className="flex-grow border rounded-md p-2">
                    {localActionItems.length > 0 ? (
                        <div className="space-y-2">
                            {/* FIX 4: Map over localActionItems */}
                            {localActionItems.map((item) => (
                                <ActionItemRow 
                                    key={item.id}
                                    item={item}
                                    onToggleComplete={(id, completed) => onToggleActionItem(item.id, completed)}
                                    onExecute={async (action) => {
                                        console.log(`Modal: Executing action for item ${item.id}: ${action}`);
                                        try {
                                            const result = await onExecuteAction(item.id, action);
                                            console.log("Modal: Execution result:", result);
                                            return result || null;
                                        } catch (e) {
                                            console.error("Modal: Execution failed:", e);
                                            return null;
                                        }
                                    }}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                            <p className="text-sm text-center">No action items yet.<br/>Paste notes above and click Generate.</p>
                        </div>
                    )}
                </ScrollArea>
                <div className="mt-2">
                    <AddActionItem
                        onAddItem={onAddActionItem}
                        placeholderText="Add a manual action item..."
                    />
                </div>
            </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}