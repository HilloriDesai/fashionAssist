import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manages conversation flow and state.
    Handles response generation and conversation context.
    """
    
    def __init__(self):
        """Initialize conversation manager with default state"""
        self.reset()
        logger.info("ConversationManager initialized with default state")
        
    def reset(self):
        """Reset conversation state to initial values"""
        self.state = {
            "followup_count": 0,
            "attributes": {},
            "stage": "initial"
        }
        self.extracted_attrs = {}
        self.inferred_attrs = {}
        self.combined_attrs = {}
        self.messages = []
        logger.info("Conversation state reset to initial values")
        
    def get_state(self) -> Dict:
        """Get current conversation state"""
        logger.debug(f"Current conversation state: {self.state}")
        return self.state
        
    def update_state(self, attributes: Dict):
        """Update conversation state with new attributes"""
        logger.info(f"Updating state with new attributes: {attributes}")
        self.state["attributes"].update(attributes)
        self.state["followup_count"] += 1
        logger.debug(f"Updated state: {self.state}")

    def update_attributes(self, extracted: Dict, inferred: Dict):
        """Update extracted and inferred attributes, maintaining combined state"""
        logger.info(f"Updating attributes - extracted: {extracted}, inferred: {inferred}")
        
        # If this is a new conversation (no existing attributes), reset first
        if not self.combined_attrs:
            self.reset()
            
        self.extracted_attrs.update(extracted)
        self.inferred_attrs.update(inferred)
        self.combined_attrs = {**self.inferred_attrs, **self.extracted_attrs}  # Extracted takes priority
        self.state["attributes"] = self.combined_attrs
        logger.debug(f"Updated combined attributes: {self.combined_attrs}")

    def get_extracted_attributes(self) -> Dict:
        """Get extracted attributes"""
        return self.extracted_attrs

    def get_inferred_attributes(self) -> Dict:
        """Get inferred attributes"""
        return self.inferred_attrs

    def get_attributes(self) -> Dict:
        """Get combined attributes"""
        return self.combined_attrs

    def determine_response_type(
        self, 
        message: str, 
        attributes: Dict, 
        current_state: Dict
    ) -> str:
        """
        Determine the type of response needed based on message and state.
        
        Args:
            message: User's input message
            attributes: Extracted attributes from message
            current_state: Current conversation state
            
        Returns:
            Response type: "followup" or "recommendation"
        """
        logger.info(f"Determining response type for message: {message}")
        logger.debug(f"Current attributes: {attributes}")
        logger.debug(f"Current state: {current_state}")
        
        # Update state with new attributes
        self.update_state(attributes)
        
        # Check if we need more information
        needs_more = self._needs_more_info(attributes, current_state)
        response_type = "followup" if needs_more else "recommendation"
        logger.info(f"Response type determined: {response_type}")
        return response_type
        
    def generate_response(
        self, 
        response_type: str, 
        attributes: Dict, 
        recommendations: List[Dict]
    ) -> str:
        """
        Generate appropriate response message.
        
        Args:
            response_type: Type of response to generate
            attributes: User preferences
            recommendations: List of product recommendations
            
        Returns:
            Generated response message
        """
        logger.info(f"Generating {response_type} response")
        logger.debug(f"Current attributes: {attributes}")
        logger.debug(f"Number of recommendations: {len(recommendations)}")
        
        if response_type == "followup":
            response = self._generate_followup_message(attributes)
        else:
            response = self._generate_recommendation_message(recommendations)
            
        logger.debug(f"Generated response: {response}")
        return response
            
    def _needs_more_info(self, attributes: Dict, current_state: Dict) -> bool:
        """Check if we need more information from the user"""
        required_attributes = ['category', 'budget']
        missing_attributes = [attr for attr in required_attributes 
                            if not attributes.get(attr)]
        logger.debug(f"Missing required attributes: {missing_attributes}")
        return len(missing_attributes) > 0
        
    def _generate_followup_message(self, attributes: Dict) -> str:
        """Generate a follow-up question based on missing attributes"""
        logger.debug("Generating follow-up message")
        
        if not attributes.get('category'):
            logger.debug("Asking for category")
            return "What type of clothing are you looking for? (e.g., dresses, tops, pants)"
        if not attributes.get('budget'):
            logger.debug("Asking for budget")
            return "What's your budget range for this item?"
        if not attributes.get('style'):
            logger.debug("Asking for style")
            return "What style are you interested in? (e.g., casual, formal, sporty)"
        if not attributes.get('color'):
            logger.debug("Asking for color")
            return "Do you have any color preferences?"
        logger.debug("Asking for additional preferences")
        return "Is there anything specific you're looking for in terms of fabric or fit?"
        
    def _generate_recommendation_message(self, recommendations: List[Dict]) -> str:
        """Generate a message for product recommendations"""
        logger.debug("Generating recommendation message")
        
        if not recommendations:
            logger.info("No recommendations found")
            return "I couldn't find any items matching your preferences. Would you like to try different criteria?"
            
        # Generate a more personalized message based on the recommendations
        categories = set(rec.get('category', '') for rec in recommendations)
        styles = set(rec.get('style', '') for rec in recommendations)
        
        logger.debug(f"Found categories: {categories}")
        logger.debug(f"Found styles: {styles}")
        
        message = "Here are some great options that match your style!"
        if categories:
            message += f" I found some {', '.join(categories)}"
        if styles:
            message += f" in {', '.join(styles)} style"
        message += ". Let me know if you'd like to see more or try different preferences!"
        
        logger.debug(f"Generated recommendation message: {message}")
        return message

    def get_messages(self) -> List[Dict]:
        """Get the conversation message history"""
        return self.messages

    def get_followup_count(self) -> int:
        """Get the current followup count"""
        return self.state["followup_count"]

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to the conversation history
        
        Args:
            role: Who sent the message ('user' or 'assistant')
            content: The message content
            metadata: Optional metadata about the message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            message.update(metadata)
        self.messages.append(message)
        logger.debug(f"Added {role} message to conversation history")

    def should_ask_followup(self) -> bool:
        """Check if we should ask a followup question"""
        return self.state["followup_count"] < 2

    def increment_followup_count(self):
        """Increment the followup count"""
        self.state["followup_count"] += 1
        logger.debug(f"Incremented followup count to {self.state['followup_count']}")

    def has_enough_info(self) -> bool:
        """Check if we have enough information to make recommendations"""
        required_attributes = ['category', 'size', 'budget', 'occasion']
        current_attrs = self.get_attributes()
        matching_attrs = [attr for attr in required_attributes if attr in current_attrs]
        has_enough = len(matching_attrs) >= 2
        logger.debug(f"Has enough info: {has_enough} (found {len(matching_attrs)} required attributes)")
        return has_enough 