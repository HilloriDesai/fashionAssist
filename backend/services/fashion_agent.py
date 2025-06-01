import logging
from typing import Dict
import pandas as pd
from .conversation_manager import ConversationManager
from .product_recommender import ProductRecommender
from .response_formatter import ResponseFormatter
import json
from .attribute_values import AttributeValues
from .ai_response_handler import AIResponseHandler

logger = logging.getLogger(__name__)

class FashionAgent:
    """
    Main agent class that coordinates fashion recommendations and conversation management.
    Handles the interaction between product recommendations and conversation flow.
    """
    
    def __init__(self, products_df: pd.DataFrame, api_key: str):
        """
        Initialize the FashionAgent with required components.
        
        Args:
            products_df: DataFrame containing product information
            api_key: API key for external services (e.g., Gemini)
        """
        self.products_df = products_df  # Store products_df as instance variable
        self.product_recommender = ProductRecommender(products_df)
        self.conversation_manager = ConversationManager()
        self.response_formatter = ResponseFormatter(self.conversation_manager, self.product_recommender)
        self.ai_response_handler = AIResponseHandler(api_key)  # Initialize AI response handler
        logger.info(f"Initialized FashionAgent with {len(products_df)} products")

    def _build_prompt(self, message: str, conversation_manager: ConversationManager) -> str:
        """Build the prompt for AI"""
        logger.info(f"Conversation history: {conversation_manager.get_messages()[-3:] if len(conversation_manager.get_messages()) > 3 else conversation_manager.get_messages()}")
        logger.info(f"Current attributes: {conversation_manager.get_attributes()}")
        
        sample_products = self.products_df.head(5).to_dict('records')
        
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

SAMPLE PRODUCTS: {sample_products}

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

CONTEXT AND ATTRIBUTE MANAGEMENT:
1. Understand the natural flow of conversation and when a user is:
   - Continuing their current shopping context
   - Starting a new shopping context
   - Referencing previous preferences
   - Changing their mind about preferences

2. When carrying forward attributes, consider:
   - Is this a continuation of the same shopping context?
   - Are the previous attributes still relevant?
   - Would carrying forward certain attributes make sense?
   - Should I ask for confirmation about previous preferences?

3. Be natural in how you handle context:
   - If user mentions "I also need pants to go with that dress", carry forward relevant attributes
   - If user says "Now I'm looking for something for work", understand it's a new context
   - If user asks "What about in blue?", understand they're refining the current context
   - If user says "Actually, I want something more casual", understand they're changing preferences

SIZE MAPPING RULES:
1. Always map numeric sizes to the closest standard size category
2. If unsure, ask for clarification about size preference
3. Never use numeric sizes directly in attributes - always map to standard categories

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
11. Always map numeric sizes to standard size categories before using them

IMPORTANT: Before making recommendations, you MUST:
1. Have at least 2 of these key attributes: category, size, budget, occasion
2. Ask followup questions if missing key information
3. Only proceed with recommendations when you have enough information
4. Use only valid attribute values from the provided list
5. Map any numeric sizes to standard size categories

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
        
    async def process_message(self, message: str) -> Dict:
        """
        Process a user message and generate appropriate response with recommendations.
        
        Args:
            message: User's input message
            
        Returns:
            Dict containing response message, type, and recommendations
        """
        try:
            # Get AI response
            ai_response = await self.ai_response_handler.get_ai_response(message, self.conversation_manager)
            logger.debug(f"AI Response: {ai_response}")
            
            # Update conversation state with extracted and inferred attributes
            if isinstance(ai_response, dict):
                # Get current attributes before updating
                current_attrs = self.conversation_manager.get_attributes()
                
                # Extract new attributes
                new_extracted = ai_response.get('extracted_attributes', {})
                new_inferred = ai_response.get('inferred_attributes', {})
                
                # Update attributes
                self.conversation_manager.update_attributes(new_extracted, new_inferred)
                logger.debug(f"Updated attributes: {self.conversation_manager.get_attributes()}")
                
                # Handle different response types
                response_type = ai_response.get('type')
                
                if response_type == 'followup' and self.conversation_manager.should_ask_followup():
                    logger.info(f"Creating followup response for followup count {self.conversation_manager.get_followup_count()}")
                    self.conversation_manager.increment_followup_count()
                    return self.response_formatter.create_followup_response(ai_response)
                elif response_type == 'direct_conversation':
                    return {
                        "type": "direct_conversation",
                        "message": ai_response['message'],
                        "followup_question": ai_response.get('followup_question', ''),
                        "attributes_so_far": self.conversation_manager.get_attributes(),
                        "recommendations": []
                    }
                elif response_type == 'recommendation':
                    # Get recommendations - our new filtering logic will handle fallbacks
                    response = self.response_formatter.create_recommendation_response()
                    return response
            
            # If we get here, something went wrong with the AI response
            return self.ai_response_handler._fallback_response(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise