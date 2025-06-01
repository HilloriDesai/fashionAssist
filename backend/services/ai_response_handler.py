import logging
from typing import Dict
import google.generativeai as genai
from .conversation_manager import ConversationManager
from .attribute_values import AttributeValues
import json
import re

logger = logging.getLogger(__name__)

class AIResponseHandler:
    """
    Handles AI response generation using Google's Gemini model.
    Manages the interaction with the AI model and processes its responses.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AI response handler.
        
        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Initialized AI Response Handler")
        
    async def get_ai_response(self, message: str, conversation_manager: ConversationManager) -> Dict:
        """
        Get structured response from AI.
        
        Args:
            message: User's input message
            conversation_manager: Current conversation state manager
            
        Returns:
            Dict containing AI response with type, message, and attributes
        """
        # Check for greetings/small talk first
        if self._is_greeting_or_small_talk(message):
            return {
                "type": "direct_conversation",
                "message": "Hello! I'm your fashion shopping assistant. How can I help you find the perfect outfit today?",
                "extracted_attributes": {},
                "inferred_attributes": {},
                "recommendations": []
            }
            
        # Check for attribute removal requests
        if any(phrase in message.lower() for phrase in ["remove all attributes", "clear attributes", "reset attributes"]):
            return {
                "type": "direct_conversation",
                "message": "I've cleared all the previous attributes. What would you like to look for?",
                "extracted_attributes": {},
                "inferred_attributes": {},
                "recommendations": []
            }
            
        prompt = self._build_prompt(message, conversation_manager)
        
        try:
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            # Clean up the response text to ensure it's valid JSON
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                ai_response = json.loads(response_text)
                
                # Ensure all required keys are present
                if 'recommendations' not in ai_response:
                    ai_response['recommendations'] = []
                
                return ai_response
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Raw response: {response_text}")
                return self._fallback_response(message)
                
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return self._fallback_response(message)
            
    def _is_greeting_or_small_talk(self, message: str) -> bool:
        """Check if the message is a greeting or small talk"""
        greetings = ['hi', 'hello', 'hey', 'howdy', 'greetings', 'good morning', 'good afternoon', 'good evening']
        small_talk = ['how are you', 'how\'s it going', 'what\'s up', 'how do you do', 'nice to meet you']
        
        message_lower = message.lower().strip()
        
        # Check for exact greetings
        if message_lower in greetings:
            return True
            
        # Check for small talk phrases
        for phrase in small_talk:
            if phrase in message_lower:
                return True
                
        return False
        
    def _fallback_response(self, message: str) -> Dict:
        """Fallback response if AI fails"""
        # Simple keyword extraction for non-greetings
        extracted = {}
        inferred = {}  # TODO: Implement vibe to attribute mapping
        
        # Basic size extraction
        sizes = re.findall(r'\b(XS|S|M|L|XL|XXL)\b', message.upper())
        if sizes:
            extracted['size'] = sizes[0]
            
        # Basic budget extraction  
        budget_match = re.search(r'\$(\d+)|under (\d+)|budget.*?(\d+)', message.lower())
        if budget_match:
            budget = int(budget_match.group(1) or budget_match.group(2) or budget_match.group(3))
            extracted['price_max'] = budget
        
        # Otherwise return a recommendation response
        return {
            "type": "recommendation",
            "message": "I'd be happy to help you find something perfect!",
            "extracted_attributes": extracted,
            "inferred_attributes": inferred,
            "recommendations": []
        } 

    def _build_prompt(self, message: str, conversation_manager: ConversationManager) -> str:
        """Build the prompt for AI"""
        logger.info(f"Conversation history: {conversation_manager.get_messages()[-3:] if len(conversation_manager.get_messages()) > 3 else conversation_manager.get_messages()}")
        logger.info(f"Current attributes: {conversation_manager.get_attributes()}")
        
        # Get valid attribute values
        valid_values = {
            'category': AttributeValues.CATEGORIES,
            'size': AttributeValues.SIZES,
            'fit': AttributeValues.FITS,
            'fabric': AttributeValues.FABRICS,
            'sleeve_length': AttributeValues.SLEEVE_LENGTHS,
            'color_or_print': AttributeValues.COLORS_AND_PRINTS,
            'occasion': AttributeValues.OCCASIONS,
            'neckline': AttributeValues.NECKLINES,
            'length': AttributeValues.LENGTHS,
            'pant_type': AttributeValues.PANT_TYPES
        }
        
        return f"""
You are a friendly and knowledgeable fashion shopping assistant. You have great fashion sense and you are able to understand the user's request and provide them with the best recommendations. 
You can also engage in natural conversations with users about fashion, style, and shopping in general.

Your primary capabilities:
1. Provide fashion recommendations based on user preferences
2. Engage in natural conversations about fashion and style
3. Ask followup questions to better understand user needs
4. Infer missing information from user's vibe and context
5. Have casual conversations about fashion trends, style advice, and shopping tips

CURRENT SITUATION:
- User message: "{message}"
- Conversation history: {conversation_manager.get_messages()[-3:] if len(conversation_manager.get_messages()) > 3 else conversation_manager.get_messages()}
- Followup count: {conversation_manager.get_followup_count()}/2
- Current attributes: {conversation_manager.get_attributes()}

AVAILABLE PRODUCT ATTRIBUTES AND VALID VALUES:
{json.dumps(valid_values, indent=2)}

VIBE TO ATTRIBUTE MAPPING:
- casual/relaxed → fit: "Relaxed"
- summer → fabric: ["Cotton", "Linen"], sleeve_length: "Sleeveless"  
- brunch → occasion: "Everyday"
- cute → style: "feminine"
- elevated → fit: "Tailored"
- budget mentions → extract number as price_max

CONVERSATION TYPES:
1. Direct Conversation (type: "direct_conversation")
   - Greetings and small talk (hi, hello, how are you, etc.)
   - General fashion questions
   - Style advice requests
   - Shopping tips
   - Fashion trend discussions
   - Personal style questions
   - Outfit planning help
   - Fashion terminology explanations

2. Followup Questions (type: "followup")
   - When missing key info (category, size, budget)
   - When need clarification on preferences
   - When need more details about style
   - When need to narrow down options

3. Product Recommendations (type: "recommendation")
   - When user asks for specific items
   - When user describes what they're looking for
   - When user needs outfit suggestions

RULES:
1. If the message is a greeting, small talk, or general fashion discussion → type: "direct_conversation"
2. If followup_count < 2 AND missing key info (category, size, budget) → type: "followup"
3. If user is asking for specific product recommendations → type: "recommendation"
4. Extract explicit attributes mentioned by user
5. Infer attributes from vibe words
6. Ask focused questions about missing essentials
7. Keep direct conversations natural and engaging
8. Provide helpful fashion advice even in casual conversations
9. Only use attribute values from the provided valid values list
10. Match attribute values exactly as they appear in the valid values list

IMPORTANT: Before making recommendations, you MUST:
1. Have at least 2 of these key attributes: category, size, budget, occasion
2. Ask followup questions if missing key information
3. Only proceed with recommendations when you have enough information
4. Use only valid attribute values from the provided list

RESPONSE FORMAT:
{{
  "type": "followup" | "recommendation" | "direct_conversation",
  "message": "conversational response to user",
  "extracted_attributes": {{"category": "dress", "size": "M"}},
  "inferred_attributes": {{"fit": "Relaxed", "fabric": "Cotton"}},
  "followup_question": "specific question if type=followup"
}}

JSON Response:
""" 