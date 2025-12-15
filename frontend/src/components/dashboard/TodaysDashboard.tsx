import { useState, useEffect } from "react";
import { Meeting, ActionType } from "@/types";
import { MeetingCard } from "./MeetingCard";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Coffee, Search, Filter, Plus } from "lucide-react";
import { AddActionItem } from "./AddActionItem";
import { MeetingDetailsModal } from "./MeetingDetailsModal";
import { api } from "@/lib/api";
import { showSuccess, showError } from "@/utils/toast";

interface TodaysDashboardProps {
  meetings: Meeting[];
  onToggleActionItem: (meetingId: string, actionId: string, isCompleted: boolean) => void;
  onAddActionItem: (meetingId: string, description: string) => Promise<void> | void;
  onExecuteAction: (id: string, action: ActionType) => Promise<string | void | null> | void;
  onGenerateSummary?: (meetingId: string) => void; // Kept for compatibility if used elsewhere, but logic moved here
  onUpdateMeeting?: (updatedMeeting: Meeting) => void;
}

export function TodaysDashboard({ meetings: initialMeetings, onToggleActionItem, onAddActionItem, onExecuteAction, onUpdateMeeting }: TodaysDashboardProps) {
  // Use local state to manage updates immediately after analysis
  const [meetings, setMeetings] = useState(initialMeetings);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [showOfflinePrompt, setShowOfflinePrompt] = useState(false);

  const today = new Date().toLocaleString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);

  // Update selectedMeeting when the source meetings data changes to ensure modal stays in sync
  useEffect(() => {
    if (selectedMeeting) {
        const updated = meetings.find(m => m.id === selectedMeeting.id);
        if (updated) {
            setSelectedMeeting(updated);
        } else {
            // Meeting was removed (e.g. after sync), so close the modal
            setSelectedMeeting(null);
        }
    }
  }, [meetings]);

  // Sync prop changes to local state
  useEffect(() => {
    setMeetings(initialMeetings);
  }, [initialMeetings]);

  const offlineMeetings = meetings.filter(m => m.type === "Offline" && m.actionItems.length === 0);

  const filteredMeetings = meetings.filter(meeting => {
    const matchesSearch =
      meeting.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      meeting.participants.some(p => p.toLowerCase().includes(searchQuery.toLowerCase())) ||
      meeting.summary.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesType = filterType === "all" || meeting.type.toLowerCase() === filterType.toLowerCase();

    return matchesSearch && matchesType;
  });

  const onlineMeetings = filteredMeetings.filter(m => m.type === 'Online');
  const offlineMeetingsList = filteredMeetings.filter(m => m.type !== 'Online');

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b space-y-4">
        <div>
          <h2 className="text-lg font-semibold">Daily Dashboard</h2>
          <p className="text-sm text-muted-foreground">{today}</p>
        </div>
        
        {meetings.length > 0 && (
          <div className="flex gap-2">
            <div className="relative flex-grow">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search meetings..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[130px]">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Filter" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="online">Online</SelectItem>
                <SelectItem value="offline">Offline</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {showOfflinePrompt && offlineMeetings.length > 0 && (
        <div className="mx-4 mt-2 p-4 bg-secondary/20 rounded-lg border border-secondary">
          <h3 className="font-semibold mb-2">Catch up on offline meetings?</h3>
          <p className="text-sm text-muted-foreground mb-3">You have {offlineMeetings.length} offline meeting(s) with no to-dos yet.</p>
          <div className="space-y-4">
            {offlineMeetings.map(meeting => (
              <div key={meeting.id} className="bg-background p-3 rounded border">
                <p className="font-medium text-sm mb-2">{meeting.title}</p>
                <AddActionItem
                  onAddItem={(desc) => onAddActionItem(meeting.id, desc)}
                  placeholderText={`Add to-do for ${meeting.title}...`}
                />
              </div>
            ))}
          </div>
          <Button variant="ghost" size="sm" className="mt-3 w-full" onClick={() => setShowOfflinePrompt(false)}>Dismiss</Button>
        </div>
      )}

      {filteredMeetings.length > 0 ? (
        <ScrollArea className="flex-grow p-4">
          <div className="space-y-6">
            {/* Show prompt trigger if hidden and applicable */}
            {!showOfflinePrompt && offlineMeetings.length > 0 && (
               <Button variant="outline" className="w-full" onClick={() => setShowOfflinePrompt(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add tasks for {offlineMeetings.length} offline meetings
               </Button>
            )}

            {onlineMeetings.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Online Meetings</h3>
                {onlineMeetings.map((meeting) => (
                  <MeetingCard
                      key={meeting.id}
                      meeting={meeting}
                      onToggleActionItem={(actionId, isCompleted) => onToggleActionItem(meeting.id, actionId, isCompleted)}
                      onAddActionItem={(description) => onAddActionItem(meeting.id, description)}
                      onExecuteAction={async (id, action) => {
                          // @ts-ignore - Ensure we return the result from the parent handler
                          const result = await onExecuteAction(id, action);
                          return result;
                      }}
                      onGenerateSummary={() => setSelectedMeeting(meeting)}
                  />
                ))}
              </div>
            )}

            {offlineMeetingsList.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Offline Meetings</h3>
                {offlineMeetingsList.map((meeting) => (
                      <MeetingCard
                          key={meeting.id}
                          meeting={meeting}
                          onToggleActionItem={(actionId, isCompleted) => onToggleActionItem(meeting.id, actionId, isCompleted)}
                          onAddActionItem={(description) => onAddActionItem(meeting.id, description)}
                          onExecuteAction={async (id, action) => {
                              // @ts-ignore - Ensure we return the result from the parent handler
                              const result = await onExecuteAction(id, action);
                              return result;
                          }}
                          onGenerateSummary={() => setSelectedMeeting(meeting)}
                      />
                    ))}
              </div>
            )}
          </div>
        </ScrollArea>
      ) : (
        <div className="flex flex-col items-center justify-center h-full text-center p-8 bg-gray-50/50 rounded-xl m-4 border-2 border-dashed border-gray-200">
          {meetings.length > 0 ? (
             <>
                <div className="bg-gray-100 p-4 rounded-full mb-4">
                    <Search className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">No matches found</h3>
                <p className="text-gray-500 max-w-sm mx-auto">
                    We couldn't find any meetings matching your current filters. Try adjusting your search terms or filters.
                </p>
                <Button
                    variant="outline"
                    className="mt-6"
                    onClick={() => {
                        setSearchQuery("");
                        setFilterType("all");
                    }}
                >
                    Clear Filters
                </Button>
             </>
          ) : (
            <>
              <div className="bg-orange-50 p-4 rounded-full mb-4">
                  <Coffee className="h-8 w-8 text-orange-500" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-1">Your schedule is clear!</h3>
              <p className="text-gray-500 max-w-sm mx-auto">
                  You have no meetings scheduled for today. This is a great opportunity to focus on deep work or catch up on backlog.
              </p>
            </>
          )}
        </div>
      )}
      <MeetingDetailsModal
        meeting={selectedMeeting}
        isOpen={!!selectedMeeting}
        onClose={() => setSelectedMeeting(null)}
        onAnalyze={async (meetingId, notes) => {
            try {
                const updatedMeeting = await api.analyzeMeeting(meetingId, notes);
                
                // Update local meetings state
                setMeetings(prev => prev.map(m => m.id === meetingId ? updatedMeeting : m));
                
                // CRITICAL: Update the selectedMeeting state immediately to reflect changes in the open modal
                setSelectedMeeting(prev => prev && prev.id === meetingId ? updatedMeeting : prev);
                
                if (onUpdateMeeting) {
                    onUpdateMeeting(updatedMeeting);
                }
                showSuccess("Action items generated!");
                return updatedMeeting;
            } catch (err) {
                showError("Analysis failed");
                throw err;
            }
        }}
        onExecuteAction={onExecuteAction}
        onToggleActionItem={(actionId, completed) => {
            if (selectedMeeting) {
                 onToggleActionItem(selectedMeeting.id, actionId, completed);
                 // Update local modal state immediately
                 setSelectedMeeting({
                     ...selectedMeeting,
                     actionItems: selectedMeeting.actionItems.map(item =>
                        item.id === actionId ? { ...item, isCompleted: completed } : item
                     )
                 });
            }
        }}
        onAddActionItem={async (description) => {
            if (selectedMeeting) {
                await onAddActionItem(selectedMeeting.id, description);
                // The parent's onAddActionItem updates the parent state, which propagates down via props.
                // However, we need to update the modal's local state immediately for the user to see it.
                // Since onAddActionItem is async and might not return the new item immediately in this flow structure without refactor,
                // we will rely on the useEffect above to sync 'meetings' -> 'selectedMeeting' or we can fetch/guess.
                // Better approach: Let's assume onAddActionItem in Index.tsx updates the list, which updates initialMeetings here,
                // which updates local meetings here. But selectedMeeting is separate state.
                // We need to update selectedMeeting too.
                
                // Let's optimistic update here for immediate feedback, assuming success (real ID comes later usually but we need to show something)
                // Actually, the best way is to find the updated meeting from the new 'meetings' state, but React state updates are async.
                
                // A simpler temporary fix for the modal view:
                // We'll trust the parent update will flow down to 'meetings', and we should update 'selectedMeeting' when 'meetings' changes?
                // No, that might close the modal or reset it if we aren't careful.
                
                // Let's look at how Index.tsx handles it. It updates the state.
                // So when 'meetings' updates here via the new useEffect, we should also update 'selectedMeeting' if it's open.
            }
        }}
      />
    </div>
  );
}