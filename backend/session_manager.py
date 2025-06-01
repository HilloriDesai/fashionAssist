import json
import os
import logging
from datetime import datetime
from typing import Dict
from models import ChatSession

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages chat sessions and their persistence"""
    
    def __init__(self, sessions_file: str = "chat_sessions.json"):
        self.sessions_file = sessions_file
        self.sessions: Dict[str, ChatSession] = self._load_sessions()

    def _load_sessions(self) -> Dict[str, ChatSession]:
        """Load chat sessions from file"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                    sessions = {}
                    for sid, data in sessions_data.items():
                        session = ChatSession()
                        session.session_id = sid
                        session.created_at = datetime.fromisoformat(data['created_at'])
                        session.messages = data['messages']
                        session.attributes = data['attributes']
                        session.followup_count = data['followup_count']
                        sessions[sid] = session
                    return sessions
            except Exception as e:
                logger.error(f"Error loading chat sessions: {str(e)}")
        return {}

    def save_sessions(self):
        """Save chat sessions to file"""
        try:
            sessions_data = {
                sid: {
                    'created_at': session.created_at.isoformat(),
                    'messages': session.messages,
                    'attributes': session.attributes,
                    'followup_count': session.followup_count
                }
                for sid, session in self.sessions.items()
            }
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions_data, f)
        except Exception as e:
            logger.error(f"Error saving chat sessions: {str(e)}")

    def get_session(self, session_id: str) -> ChatSession:
        """Get a chat session by ID"""
        return self.sessions.get(session_id)

    def create_session(self) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession()
        self.sessions[session.session_id] = session
        self.save_sessions()
        return session

    def update_session(self, session_id: str, session: ChatSession):
        """Update an existing chat session"""
        self.sessions[session_id] = session
        self.save_sessions() 