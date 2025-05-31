from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
from eCommerceAssistance import FashionAgent
import os
from typing import Dict, List, Optional
import logging
import uuid
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-commerce Assistant API",
    description="API for intelligent e-commerce product recommendations and chat assistance",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load products data
try:
    products_df = pd.read_csv("Apparels_shared.csv")
    logger.info(f"Successfully loaded {len(products_df)} products")
except Exception as e:
    logger.error(f"Failed to load products data: {str(e)}")
    raise

# Initialize FashionAgent
try:
    fashion_agent = FashionAgent(
        products_df=products_df,
        api_key=os.getenv("GOOGLE_GEMINI_API_KEY", "")
    )
    logger.info("Successfully initialized FashionAgent")
except Exception as e:
    logger.error(f"Failed to initialize FashionAgent: {str(e)}")
    raise

# Chat session storage
CHAT_SESSIONS_FILE = "chat_sessions.json"

def load_chat_sessions():
    """Load chat sessions from file"""
    if os.path.exists(CHAT_SESSIONS_FILE):
        try:
            with open(CHAT_SESSIONS_FILE, 'r') as f:
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

def save_chat_sessions():
    """Save chat sessions to file"""
    try:
        sessions_data = {
            sid: {
                'created_at': session.created_at.isoformat(),
                'messages': session.messages,
                'attributes': session.attributes,
                'followup_count': session.followup_count
            }
            for sid, session in chat_sessions.items()
        }
        with open(CHAT_SESSIONS_FILE, 'w') as f:
            json.dump(sessions_data, f)
    except Exception as e:
        logger.error(f"Error saving chat sessions: {str(e)}")

# Initialize chat sessions from file
chat_sessions = load_chat_sessions()

class ChatSession:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.messages = []
        self.attributes = {}
        self.followup_count = 0

    def add_message(self, role: str, content: str, response_data: Optional[dict] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.messages.append(message)
        return message

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message to process")
    current_attributes: Optional[Dict] = Field(None, description="Current conversation attributes")
    session_id: Optional[str] = Field(None, description="Session ID")

class ProductRequest(BaseModel):
    category: Optional[str] = Field(None, description="Product category")
    size: Optional[str] = Field(None, description="Product size")
    budget: Optional[float] = Field(None, description="Maximum budget")
    style: Optional[str] = Field(None, description="Style preference")
    occasion: Optional[str] = Field(None, description="Occasion")
    color: Optional[str] = Field(None, description="Color preference")
    fabric: Optional[str] = Field(None, description="Fabric preference")
    fit: Optional[str] = Field(None, description="Fit preference")

class ProductResponse(BaseModel):
    products: List[Dict]
    total_count: int
    filters_applied: Dict
    removed_filters: Optional[List[str]] = None

@app.post("/api/chat")
async def process_message(request: ChatRequest):
    """
    Process a chat message and return AI-generated response with product recommendations.
    """
    try:
        logger.info(f"Processing chat message: {request.message}")
        
        # Get or create chat session
        session_id = request.session_id
        if not session_id or session_id not in chat_sessions:
            session = ChatSession()
            chat_sessions[session.session_id] = session
            session_id = session.session_id
        else:
            session = chat_sessions[session_id]
        
        # Add user message to session
        session.add_message("user", request.message)
        
        # If we have current attributes, update the agent's state
        if request.current_attributes:
            session.attributes.update(request.current_attributes)
            logger.info(f"Updated conversation state with attributes: {request.current_attributes}")
        
        # Process message with the agent
        response = await fashion_agent.process_message(request.message)
        logger.info("response from fashion agent", response)
        # Add bot response to session
        session.add_message("bot", response["message"], response)
        
        # Update session state
        session.followup_count = response.get("followup_count", 0)
        
        # Save chat sessions after each update
        save_chat_sessions()
        
        # Return response with session info
        return {
            "session_id": session_id,
            "message": response["message"],
            "type": response["type"],
            "recommendations": response.get("recommendations", []),
            "current_state": {
                "attributes": session.attributes,
                "followup_count": session.followup_count
            }
        }
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{session_id}")
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a specific session.
    """
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    session = chat_sessions[session_id]
    return {
        "session_id": session.session_id,
        "created_at": session.created_at.isoformat(),
        "messages": session.messages,
        "current_state": {
            "attributes": session.attributes,
            "followup_count": session.followup_count
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 