import { useState, useEffect } from "react";
import { TodaysDashboard } from "@/components/dashboard/TodaysDashboard";
import { PastDashboards } from "@/components/dashboard/PastDashboards";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Meeting, ActionType, DailyDashboard } from "@/types";
import { showSuccess, showError } from "@/utils/toast";
import { useIsMobile } from "@/hooks/use-mobile";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

const Index = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [dashboards, setDashboards] = useState<DailyDashboard[]>([]);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const isMobile = useIsMobile();

  const fetchToday = async () => {
    try {
        const data = await api.getTodaysDashboard();
        console.log("Fetched meetings:", data.meetings);
        setMeetings(data.meetings);
    } catch (error) {
        console.error("Failed to fetch today's dashboard", error);
    }
  };

  const fetchHistory = async () => {
    try {
        const data = await api.getPastDashboards();
        setDashboards(data);
    } catch (error) {
        console.error("Failed to fetch history", error);
    }
  };

  useEffect(() => {
    fetchToday();
    fetchHistory();
  }, []);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
        await api.syncMeetings();
        await fetchToday();
        showSuccess("Synced with Google Calendar");
    } catch (error) {
        showError("Sync failed");
        console.error(error);
    } finally {
        setIsSyncing(false);
    }
  };

  const handleToggleTodayActionItem = async (meetingId: string, actionId: string, isCompleted: boolean) => {
    try {
        await api.updateActionItem(actionId, { isCompleted });
        setMeetings(prevMeetings =>
          prevMeetings.map(meeting =>
            meeting.id === meetingId
              ? {
                  ...meeting,
                  actionItems: meeting.actionItems.map(item =>
                    item.id === actionId ? { ...item, isCompleted } : item
                  ),
                }
              : meeting
          )
        );
    } catch (error) {
        showError("Failed to update status");
    }
  };

  const handleAddTodayActionItem = async (meetingId: string, description: string) => {
    try {
        const newActionItem = await api.createActionItem(meetingId, description);
        setMeetings(prevMeetings =>
          prevMeetings.map(meeting =>
            meeting.id === meetingId
              ? { ...meeting, actionItems: [...meeting.actionItems, newActionItem] }
              : meeting
          )
        );
        // Force refresh today's dashboard to ensure all states are synced if needed,
        // though local update should be enough. The issue might be keying or deep nesting.
        // await fetchToday();
        showSuccess("Action item created!");
    } catch (error) {
        showError("Failed to create action item");
    }
  };

  const handleTogglePastActionItem = async (dashboardDate: string, meetingId: string, actionId: string, isCompleted: boolean) => {
    try {
        await api.updateActionItem(actionId, { isCompleted });
        setDashboards(prevDashboards =>
          prevDashboards.map(dashboard =>
            dashboard.date === dashboardDate
              ? {
                  ...dashboard,
                  meetings: dashboard.meetings.map(meeting =>
                    meeting.id === meetingId
                      ? {
                          ...meeting,
                          actionItems: meeting.actionItems.map(item =>
                            item.id === actionId ? { ...item, isCompleted } : item
                          ),
                        }
                      : meeting
                  ),
                }
              : dashboard
          )
        );
    } catch (error) {
        showError("Failed to update status");
    }
  };

  const handleAddPastActionItem = async (dashboardDate: string, meetingId: string, description: string) => {
    try {
        const newActionItem = await api.createActionItem(meetingId, description);
        setDashboards(prevDashboards =>
          prevDashboards.map(dashboard =>
            dashboard.date === dashboardDate
              ? {
                  ...dashboard,
                  meetings: dashboard.meetings.map(meeting =>
                    meeting.id === meetingId
                      ? { ...meeting, actionItems: [...meeting.actionItems, newActionItem] }
                      : meeting
                  ),
                }
              : dashboard
          )
        );
        showSuccess("Action item created!");
    } catch (error) {
        showError("Failed to create action item");
        // Fallback to local optimistic update with temp ID if API fails (optional, but consistent with previous code)
         const newActionItem = {
          id: `a${Date.now()}`,
          description,
          isCompleted: false,
          suggestedAction: "Create Task" as ActionType,
        };
        setDashboards(prevDashboards =>
          prevDashboards.map(dashboard =>
            dashboard.date === dashboardDate
              ? {
                  ...dashboard,
                  meetings: dashboard.meetings.map(meeting =>
                    meeting.id === meetingId
                      ? { ...meeting, actionItems: [...meeting.actionItems, newActionItem] }
                      : meeting
                  ),
                }
              : dashboard
          )
        );
    }
  };

  const handleExecuteAction = async (actionId: string, action: ActionType) => {
    try {
      showSuccess(`Executing "${action}"...`);
      const response = await api.executeAction(actionId, { action_type: action });
      
      // Update state to mark as completed
      const updateMeetings = (currentMeetings: Meeting[]) =>
        currentMeetings.map(meeting => ({
          ...meeting,
          actionItems: meeting.actionItems.map(item =>
            item.id === actionId ? { ...item, isCompleted: true } : item
          ),
        }));

      // Optimistically update both today's meetings and history
      setMeetings(prev => updateMeetings(prev));
      setDashboards(prev => prev.map(d => ({ ...d, meetings: updateMeetings(d.meetings) })));

      // Let the component handle the link opening via returned value
      showSuccess("Action executed successfully!");
      
      // Return the link if present so the component can update its state
      if (response && response.link) {
          return response.link;
      }
      if (response && response.notionUrl) {
          return response.notionUrl;
      }

    } catch (error: any) {
      if (error.message === "Unauthorized" || error.message.includes("401") || error.message.includes("403")) {
          showError("Google session expired. Please re-login.");
          // Optional: redirect to login or force re-auth flow
          // navigate("/login");
      } else {
          showError("Failed to execute action");
      }
      console.error(error);
    }
  };

  const handleGenerateSummary = async (meetingId: string) => {
    try {
        showSuccess("Generating summary...");
        const updatedMeeting = await api.processMeeting(meetingId, ""); // Empty content triggers backend fetch
        setMeetings(prevMeetings =>
            prevMeetings.map(m => m.id === meetingId ? updatedMeeting : m)
        );
        showSuccess("Summary generated!");
    } catch (error) {
        showError("Failed to generate summary");
        console.error(error);
    }
  };

  const handleUpdateMeeting = (updatedMeeting: Meeting) => {
    setMeetings(prevMeetings =>
        prevMeetings.map(m => m.id === updatedMeeting.id ? updatedMeeting : m)
    );
  };

  const handleViewMore = () => {
    // In a real app, this would be pagination API
    setIsLoadingMore(true);
    setTimeout(() => {
      setIsLoadingMore(false);
      showSuccess("No more history in MVP.");
    }, 1000);
  };


  if (isMobile) {
    return (
      <div className="relative h-full">
        <div className="absolute top-4 right-4 z-10">
          <Button onClick={handleSync} disabled={isSyncing} variant="outline" size="sm">
              <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
              {isSyncing ? "Syncing..." : "Sync Calendar"}
          </Button>
        </div>
        <Tabs defaultValue="today" className="h-full w-full flex flex-col pt-12">
            <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="today">Today</TabsTrigger>
            <TabsTrigger value="past">Past</TabsTrigger>
            </TabsList>
            <TabsContent value="today" className="flex-grow overflow-hidden">
            <TodaysDashboard
                meetings={meetings}
                onToggleActionItem={handleToggleTodayActionItem}
                onAddActionItem={handleAddTodayActionItem}
                onExecuteAction={handleExecuteAction}
                onGenerateSummary={handleGenerateSummary}
                onUpdateMeeting={handleUpdateMeeting}
            />
            </TabsContent>
            <TabsContent value="past" className="flex-grow overflow-hidden">
            <PastDashboards
                dashboards={dashboards}
                isLoadingMore={isLoadingMore}
                onToggleActionItem={handleTogglePastActionItem}
                onAddActionItem={handleAddPastActionItem}
                onExecuteAction={handleExecuteAction}
                onViewMore={handleViewMore}
            />
            </TabsContent>
        </Tabs>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
        <div className="absolute top-4 right-4 z-10">
          <Button onClick={handleSync} disabled={isSyncing} variant="outline" size="sm">
              <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
              {isSyncing ? "Syncing..." : "Sync Calendar"}
          </Button>
        </div>
        <ResizablePanelGroup direction="horizontal" className="h-full w-full pt-12">
        <ResizablePanel defaultSize={60} minSize={40}>
            <TodaysDashboard
            meetings={meetings}
            onToggleActionItem={handleToggleTodayActionItem}
            onAddActionItem={handleAddTodayActionItem}
            onExecuteAction={handleExecuteAction}
            onGenerateSummary={handleGenerateSummary}
            onUpdateMeeting={handleUpdateMeeting}
            />
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={40} minSize={30}>
            <PastDashboards
            dashboards={dashboards}
            isLoadingMore={isLoadingMore}
            onToggleActionItem={handleTogglePastActionItem}
            onAddActionItem={handleAddPastActionItem}
            onExecuteAction={handleExecuteAction}
            onViewMore={handleViewMore}
            />
        </ResizablePanel>
        </ResizablePanelGroup>
    </div>
  );
};

export default Index;