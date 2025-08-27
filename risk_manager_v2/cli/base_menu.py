"""
Base Menu Class

Provides common functionality for all menu classes to eliminate duplication.
"""

from core.config import ConfigStore
from core.auth import AuthManager
from core.client import ProjectXClient
from core.logger import get_logger

class BaseMenu:
    """Base class for all menu components."""
    
    def __init__(self):
        """Initialize common components for all menus."""
        self.logger = get_logger(__name__)
        self.config = ConfigStore()
        self.auth = AuthManager(self.config)
        self.client = ProjectXClient(self.config, self.auth)
    
    def run(self):
        """Override this method in subclasses."""
        raise NotImplementedError("Subclasses must implement run()")
    
    def display_menu(self):
        """Override this method in subclasses."""
        raise NotImplementedError("Subclasses must implement display_menu()")
