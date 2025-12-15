from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class ActionExecutor(ABC):
    @abstractmethod
    def execute(self, action_data: Dict[str, Any], user_token: Optional[str] = None) -> Any:
        """
        Executes the specific action.
        
        Args:
            action_data: Dictionary containing details needed for the action
                         (e.g., recipient, subject, body for email).
            user_token: OAuth token if required for the action (e.g., Google API).
            
        Returns:
            Dictionary with result details if successful, False otherwise.
        """
        pass