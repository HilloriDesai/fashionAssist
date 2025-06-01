from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class ChatSession:
    """Represents a chat session with a user"""
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.messages = []
        self.attributes = {}
        self.followup_count = 0

    def add_message(self, role: str, content: str, response_data: Optional[dict] = None):
        """Add a new message to the chat session"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.messages.append(message)
        return message

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="The user's message to process")
    current_attributes: Optional[Dict] = Field(None, description="Current conversation attributes")
    session_id: Optional[str] = Field(None, description="Session ID")

class ProductRequest(BaseModel):
    """Request model for product queries"""
    category: Optional[str] = Field(None, description="Product category")
    size: Optional[str] = Field(None, description="Product size")
    budget: Optional[float] = Field(None, description="Maximum budget")
    style: Optional[str] = Field(None, description="Style preference")
    occasion: Optional[str] = Field(None, description="Occasion")
    color: Optional[str] = Field(None, description="Color preference")
    fabric: Optional[str] = Field(None, description="Fabric preference")
    fit: Optional[str] = Field(None, description="Fit preference")

class ProductResponse(BaseModel):
    """Response model for product recommendations"""
    products: List[Dict]
    total_count: int
    filters_applied: Dict
    removed_filters: Optional[List[str]] = None 