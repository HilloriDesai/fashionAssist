from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from services.fashion_agent import FashionAgent
import os
import logging
from dotenv import load_dotenv
from models import ChatRequest
from session_manager import SessionManager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Assistant API",
    description="API for intelligent e-commerce product recommendations and chat assistance",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://fashionassist.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    products_df = pd.read_csv("Apparels_shared.csv")
    logger.info(f"Successfully loaded {len(products_df)} products")
    
    fashion_agent = FashionAgent(
        products_df=products_df,
        api_key=os.getenv("GOOGLE_GEMINI_API_KEY", "")
    )
    logger.info("Successfully initialized FashionAgent")
    
    session_manager = SessionManager()
    logger.info("Successfully initialized SessionManager")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/api/chat")
async def process_message(request: ChatRequest):
    """Process a chat message and return AI-generated response with product recommendations."""
    try:
        logger.info(f"Processing chat message: {request.message}")
        
        # Get or create chat session
        session = session_manager.get_session(request.session_id)
        if not session:
            session = session_manager.create_session()
        
        # Add user message to session
        session.add_message("user", request.message)
        
        # Update session attributes if provided
        if request.current_attributes:
            session.attributes.update(request.current_attributes)
            logger.info(f"Updated conversation state with attributes: {request.current_attributes}")
        
        # Process message with the agent
        response = await fashion_agent.process_message(request.message)
        logger.info("Response from fashion agent:", response)
        
        # Add bot response to session
        session.add_message("bot", response["message"], response)
        
        # Update session state
        session.followup_count = response.get("followup_count", 0)
        session_manager.update_session(session.session_id, session)
        
        # Return response with session info
        return {
            "session_id": session.session_id,
            "message": response["message"],
            "type": response["type"],
            "recommendations": response.get("recommendations", []),
            "messages": session.messages,
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
    """Retrieve chat history for a specific session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
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