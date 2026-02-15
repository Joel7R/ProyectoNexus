from typing import Dict
from server.utils.logger import logger

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.conversation_states = {}
            cls._instance._initialized = True
        return cls._instance

    def get_session(self, session_id: str) -> Dict:
        """Retrieves or creates a session state."""
        if session_id not in self.conversation_states:
            logger.info(f"Creating new session state for: {session_id}")
            self.conversation_states[session_id] = {"messages": []}
        return self.conversation_states[session_id]

    def clear_session(self, session_id: str):
        """Clears a session state."""
        if session_id in self.conversation_states:
            del self.conversation_states[session_id]
            logger.info(f"Cleared session: {session_id}")
            
# Global instance
db_manager = DatabaseManager()
