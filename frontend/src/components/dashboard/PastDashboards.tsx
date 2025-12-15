import { DailyDashboard, ActionType } from "@/types";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { MeetingCard } from "./MeetingCard";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "../ui/button";
import { Archive, Loader2 } from "lucide-react";

interface PastDashboardsProps {
  dashboards: DailyDashboard[];
  isLoadingMore: boolean;
  onToggleActionItem: (dashboardDate: string, meetingId: string, actionId: string, isCompleted: boolean) => void;
  onAddActionItem: (dashboardDate: string, meetingId: string, description: string) => void;
  onExecuteAction: (id: string, action: ActionType) => void;
  onGenerateSummary?: (meetingId: string) => void;
  onViewMore: () => void;
}

import { useState, useEffect } from "react";

export function PastDashboards({ dashboards: initialDashboards, isLoadingMore, onToggleActionItem, onAddActionItem, onExecuteAction, onGenerateSummary, onViewMore }: PastDashboardsProps) {
  const [dashboards, setDashboards] = useState(initialDashboards);

  useEffect(() => {
      setDashboards(initialDashboards);
  }, [initialDashboards]);

  return (
    <div className="flex flex-col h-full bg-muted/40">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Past Dashboards</h2>
        <p className="text-sm text-muted-foreground">Last 7 days</p>
      </div>
      {dashboards.length > 0 ? (
        <ScrollArea className="flex-grow p-4">
          <Accordion type="multiple" className="w-full space-y-2">
            {dashboards.map((dashboard) => (
              <AccordionItem value={dashboard.date} key={`${dashboard.date}-${dashboard.isResolved ? 'resolved' : 'unresolved'}`}>
                <AccordionTrigger className={`text-sm font-medium ${dashboard.isResolved ? 'text-blue-600' : 'text-red-600'}`}>
                  {new Date(dashboard.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 p-2">
                    {dashboard.meetings.map((meeting) => (
                      <MeetingCard
                        key={`${meeting.id}-${meeting.actionItems.length}`}
                        meeting={meeting}
                        onToggleActionItem={(actionId, isCompleted) => onToggleActionItem(dashboard.date, meeting.id, actionId, isCompleted)}
                        onAddActionItem={(description) => onAddActionItem(dashboard.date, meeting.id, description)}
                        onExecuteAction={async (id, action) => {
                            // Ensure async execution and return result
                            // @ts-ignore
                            const result = await onExecuteAction(id, action);
                            return result;
                        }}
                        onGenerateSummary={onGenerateSummary}
                      />
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
          <div className="mt-4 text-center">
              <Button variant="link" onClick={onViewMore} disabled={isLoadingMore}>
                {isLoadingMore ? (
                    <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Loading...
                    </>
                ) : (
                    "View More"
                )}
              </Button>
          </div>
        </ScrollArea>
      ) : (
        <div className="flex flex-col items-center justify-center h-full text-center p-8 bg-gray-50/50 rounded-xl m-4 border-2 border-dashed border-gray-200">
            <div className="bg-purple-50 p-4 rounded-full mb-4">
                <Archive className="h-8 w-8 text-purple-500" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-1">No history yet</h3>
            <p className="text-gray-500 max-w-sm mx-auto">
                Once you start managing your daily meetings, your past dashboards will be archived here for easy access.
            </p>
        </div>
      )}
    </div>
  );
}