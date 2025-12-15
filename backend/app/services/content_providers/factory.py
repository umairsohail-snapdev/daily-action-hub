from typing import List
from .base import ContentProvider
from .notion import NotionProvider
from .granola import GranolaProvider
from ...config import settings

class ContentProviderFactory:
    @staticmethod
    def get_providers() -> List[ContentProvider]:
        """
        Returns a list of configured content providers.
        """
        providers = []
        
        # In a real scenario, we might check settings to see which are enabled
        # For this MVP, we enable both mock providers
        
        providers.append(NotionProvider())
        providers.append(GranolaProvider())
        
        return providers