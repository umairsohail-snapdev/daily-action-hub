from ...models import ActionType
from .base import ActionExecutor
from .gmail import GmailExecutor
from .calendar import CalendarExecutor
from .notion import NotionExecutor

class ActionExecutorFactory:
    _executors = {
        ActionType.SEND_EMAIL: GmailExecutor(),
        ActionType.CREATE_CALENDAR_INVITE: CalendarExecutor(),
        ActionType.CREATE_TASK: NotionExecutor(),
        # ActionType.ADD_TO_OBSIDIAN: ObsidianExecutor(),
    }

    @staticmethod
    def get_executor(action_type: ActionType) -> ActionExecutor:
        executor = ActionExecutorFactory._executors.get(action_type)
        if not executor:
            raise ValueError(f"No executor found for action type: {action_type}")
        return executor