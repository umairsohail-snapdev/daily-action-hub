from typing import Dict, Type
from .base import ActionExecutor
from .gmail import GmailExecutor
from .calendar import CalendarExecutor
from .notion import NotionExecutor
from ...models import ActionType

class ActionExecutorFactory:
    _executors: Dict[ActionType, Type[ActionExecutor]] = {
        ActionType.SEND_EMAIL: GmailExecutor,
        ActionType.CREATE_CALENDAR_INVITE: CalendarExecutor,
        ActionType.CREATE_TASK: NotionExecutor,
        ActionType.ADD_TO_OBSIDIAN: NotionExecutor, # Using Notion as fallback/placeholder for Obsidian
    }

    @classmethod
    def get_executor(cls, action_type: ActionType) -> ActionExecutor:
        executor_class = cls._executors.get(action_type)
        if not executor_class:
            raise ValueError(f"No executor found for action type: {action_type}")
        return executor_class()