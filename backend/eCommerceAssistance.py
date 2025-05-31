import pandas as pd
import json
import asyncio
import google.generativeai as genai
from typing import Dict, List, Optional, Union
import re
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fashion_agent.log')
    ]
)
logger = logging.getLogger(__name__)

class AttributeValues:
    """Stores all valid attribute values for the fashion system"""
    
    CATEGORIES = ['top', 'dress', 'skirt', 'pants']
    
    SIZES = ['XS', 'S', 'M', 'L', 'XL']
    
    FITS = [
        'Relaxed', 'Stretch to fit', 'Body hugging', 'Tailored', 'Flowy',
        'Bodycon', 'Oversized', 'Slim', 'Sleek and straight'
    ]
    
    FABRICS = [
        'Linen', 'Silk', 'Cotton', 'Rayon', 'Satin', 'Modal jersey', 'Crepe',
        'Tencel', 'Sequined mesh', 'Viscose', 'Organic cotton', 'Chiffon',
        'Cotton poplin', 'Linen blend', 'Cotton gauze', 'Ribbed jersey',
        'Lace overlay', 'Tencel twill', 'Chambray', 'Velvet', 'Silk chiffon',
        'Bamboo jersey', 'Ribbed knit', 'Tweed', 'Organza overlay',
        'Sequined velvet', 'Cotton-blend', 'Crushed velvet', 'Tulle', 'Denim',
        'Wool-blend', 'Scuba knit', 'Linen-blend', 'Polyester georgette',
        'Cotton twill', 'Poly-crepe', 'Viscose voile', 'Vegan leather',
        'Lamé', 'Polyester twill', 'Stretch denim', 'Tencel-blend'
    ]
    
    SLEEVE_LENGTHS = [
        'Short Flutter Sleeves', 'Cropped', 'Long sleeves with button cuffs',
        'Sleeveless', 'Full sleeves', 'Short sleeves', 'Quarter sleeves',
        'Straps', 'Spaghetti straps', 'Short flutter sleeves', 'Tube',
        'Balloon sleeves', 'Halter', 'Bishop sleeves', 'Cap sleeves',
        'Cropped long sleeves', 'Bell sleeves', 'Short puff sleeves'
    ]
    
    COLORS_AND_PRINTS = [
        'Pastel yellow', 'Deep blue', 'Floral print', 'Red', 'Off-white',
        'Pastel pink', 'Aqua blue', 'Green floral', 'Charcoal', 'Pastel coral',
        'Dusty rose', 'Seafoam green', 'Multicolor mosaic print', 'Pastel floral',
        'Storm grey', 'Cobalt blue', 'Blush pink', 'Sunflower yellow',
        'Aqua wave print', 'Black iridescent', 'Orchid purple', 'Amber gold',
        'Watercolor petals', 'Stone/black stripe', 'Sage green', 'Soft teal',
        'Charcoal marled', 'Lavender', 'Ombre sunset', 'Coral stripe',
        'Jet black', 'Olive green', 'Mustard yellow', 'Silver metallic',
        'Teal abstract print', 'Lavender haze', 'Warm taupe', 'Black polka dot',
        'Midnight navy sequin', 'Sunshine yellow', 'Charcoal pinstripe',
        'Plum purple', 'Emerald green', 'Mustard windowpane check',
        'Sapphire blue', 'Peony watercolor print', 'Slate grey',
        'Emerald green grid check', 'Bronze metallic', 'Seafoam green',
        'Midnight navy', 'Classic indigo', 'Stone beige', 'Sand taupe',
        'Graphite grey', 'Deep indigo', 'Platinum grey'
    ]
    
    OCCASIONS = ['Party', 'Vacation', 'Everyday', 'Evening', 'Work']
    
    NECKLINES = [
        'Sweetheart', 'Square neck', 'V neck', 'Boat neck', 'Tubetop',
        'Halter', 'Collar', 'One-shoulder', 'Polo collar', 'Illusion bateau',
        'Round neck', 'Cowl neck'
    ]
    
    LENGTHS = ['Mini', 'Short', 'Midi', 'Maxi']
    
    PANT_TYPES = [
        'Wide-legged', 'Ankle length', 'Flared', 'Wide hem',
        'Straight ankle', 'Mid-rise', 'Low-rise'
    ]
    
    @classmethod
    def get_valid_values(cls, attribute: str) -> List[str]:
        """Get valid values for a given attribute"""
        attribute_map = {
            'category': cls.CATEGORIES,
            'size': cls.SIZES,
            'fit': cls.FITS,
            'fabric': cls.FABRICS,
            'sleeve_length': cls.SLEEVE_LENGTHS,
            'color_or_print': cls.COLORS_AND_PRINTS,
            'occasion': cls.OCCASIONS,
            'neckline': cls.NECKLINES,
            'length': cls.LENGTHS,
            'pant_type': cls.PANT_TYPES
        }
        return attribute_map.get(attribute, [])

class VibeToAttributeMapper:
    """Maps vibe terms to structured attributes"""
    
    VIBE_MAPPINGS = {
        # Occasion vibes
        'casual': {'fit': 'Relaxed', 'style': 'casual'},
        'elevated': {'fit': 'Tailored', 'style': 'sophisticated'},
        'brunch': {'occasion': 'Everyday', 'style': 'cute'},
        'date': {'fit': 'Body hugging', 'style': 'romantic'},
        'work': {'fit': 'Tailored', 'style': 'professional'},
        
        # Season vibes
        'summer': {'fabric': ['Cotton', 'Linen'], 'sleeve_length': 'Sleeveless'},
        'winter': {'fabric': ['Wool-blend', 'Ribbed knit'], 'sleeve_length': 'Full sleeves'},
        'spring': {'fabric': ['Cotton', 'Chiffon']},
        
        # Style vibes
        'cute': {'style': 'feminine', 'fit': 'Relaxed'},
        'edgy': {'style': 'modern', 'color_or_print': 'Jet black'},
        'romantic': {'style': 'feminine', 'fabric': ['Chiffon', 'Silk']},
        'minimalist': {'color_or_print': ['Off-white', 'Jet black', 'Stone beige']},
        
        # Fit vibes
        'relaxed': {'fit': 'Relaxed'},
        'fitted': {'fit': 'Body hugging'},
        'flowy': {'fit': 'Flowy'},
        'bodycon': {'fit': 'Bodycon'}
    }
    
    @classmethod
    def infer_attributes(cls, text: str) -> Dict:
        """Extract inferred attributes from vibe text"""
        text_lower = text.lower()
        inferred = {}
        
        for vibe, attributes in cls.VIBE_MAPPINGS.items():
            if vibe in text_lower:
                for attr, value in attributes.items():
                    if attr not in inferred:
                        inferred[attr] = value
                    elif isinstance(inferred[attr], list) and isinstance(value, list):
                        inferred[attr].extend(value)
        
        logger.debug(f"Inferred attributes from text: {inferred}")
        return inferred

class ConversationState:
    """Manages conversation flow and state"""
    
    def __init__(self):
        self.messages = []
        self.followup_count = 0
        self.extracted_attrs = {}
        self.inferred_attrs = {}
        self.combined_attrs = {}
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    def should_ask_followup(self) -> bool:
        logger.info(f"Checking if should ask followup. Current count: {self.followup_count}")
        return self.followup_count < 2
    
    def has_enough_info(self) -> bool:
        """Check if we have minimum info to make good recommendations"""
        essential_attrs = ['category', 'size', 'budget', 'occasion']
        provided_count = sum(1 for attr in essential_attrs if attr in self.combined_attrs)
        logger.info(f"Checking if has enough info. Current combined attrs: {provided_count}")

        return provided_count >= 2
    
    def update_attributes(self, extracted: Dict, inferred: Dict):
        self.extracted_attrs.update(extracted)
        self.inferred_attrs.update(inferred)
        self.combined_attrs = {**self.inferred_attrs, **self.extracted_attrs}  # Extracted takes priority

class ProductFilter:
    """Handles product filtering and scoring"""
    
    # Define attribute priorities (higher number = higher priority)
    ATTRIBUTE_PRIORITIES = {
        'category': 5,      # Highest priority - essential for product type
        'size': 4,          # High priority - important for fit
        'budget': 4,        # High priority - important for purchase
        'price_max': 4,     # Same as budget
        'fabric': 3,        # Medium priority - important for feel/quality
        'fit': 3,          # Medium priority - important for style
        'style': 2,        # Lower priority - style preference
        'color_or_print': 2, # Lower priority - aesthetic preference
        'sleeve_length': 2,  # Lower priority - style detail
        'occasion': 1       # Lowest priority - optional context
    }
    
    @staticmethod
    def filter_products(products_df: pd.DataFrame, attributes: Dict, top_k: int = 5) -> pd.DataFrame:
        """Filter products based on attributes with smart fallback logic"""
        logger.info(f"Starting product filtering with attributes: {attributes}")
        logger.debug(f"Initial product count: {len(products_df)}")
        logger.debug(f"Available columns: {products_df.columns.tolist()}")
        
        # Verify required columns exist
        required_columns = ['id', 'name', 'category', 'price', 'available_sizes']
        missing_columns = [col for col in required_columns if col not in products_df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(f"DataFrame missing required columns: {missing_columns}")
        
        filtered = products_df.copy()
        original_len = len(filtered)
        removed_filters = []  # Initialize removed_filters at the start
        
        # Sort attributes by priority
        sorted_attrs = sorted(
            attributes.items(),
            key=lambda x: ProductFilter.ATTRIBUTE_PRIORITIES.get(x[0], 0),
            reverse=True
        )
        
        # Try filtering with all attributes first
        filtered = ProductFilter._apply_filters(filtered, dict(sorted_attrs))
        
        # If not enough results, progressively remove less important filters
        if len(filtered) < top_k:
            logger.info(f"Not enough results ({len(filtered)}), applying fallback logic")
            
            # Try removing filters one by one, starting with lowest priority
            for attr, value in reversed(sorted_attrs):
                if len(filtered) >= top_k:
                    break
                    
                # Skip essential filters
                if ProductFilter.ATTRIBUTE_PRIORITIES.get(attr, 0) >= 4:
                    continue
                
                # Create new filter set without this attribute
                current_filters = dict(sorted_attrs)
                del current_filters[attr]
                
                # Try filtering with reduced set
                new_filtered = ProductFilter._apply_filters(products_df.copy(), current_filters)
                
                if len(new_filtered) > len(filtered):
                    filtered = new_filtered
                    removed_filters.append(attr)
                    logger.info(f"Removed filter '{attr}' to get more results. New count: {len(filtered)}")
        
        # Score remaining products
        filtered = ProductFilter._score_products(filtered, attributes)
        
        # Add metadata about filtering process
        filtered['is_fallback'] = len(removed_filters) > 0
        filtered['removed_filters'] = str(removed_filters) if len(removed_filters) > 0 else ''
        
        # Ensure we have the right columns and data types
        filtered = filtered.reset_index(drop=True)
        logger.info(f"Final filtered product count: {len(filtered)}")
        logger.debug(f"Filtered columns: {filtered.columns.tolist()}")
        logger.debug(f"First few filtered products:\n{filtered.head()}")
        
        return filtered.head(top_k)
    
    @staticmethod
    def _apply_filters(products_df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Apply a set of filters to the products dataframe"""
        filtered = products_df.copy()
        
        for attr, value in filters.items():
            if attr not in filtered.columns:
                logger.warning(f"Column '{attr}' not found in DataFrame. Available columns: {filtered.columns.tolist()}")
                continue
                
            if attr == 'category':
                if isinstance(value, list):
                    filtered = filtered[filtered[attr].isin(value)]
                else:
                    filtered = filtered[filtered[attr].str.lower() == value.lower()]
                    
            elif attr in ['size', 'available_sizes']:
                size = value
                filtered = filtered[filtered['available_sizes'].str.contains(size, case=False, na=False)]
                
            elif attr in ['budget', 'price_max']:
                max_price = float(value)
                if 'price' in filtered.columns:
                    filtered = filtered[filtered['price'] <= max_price]
                    
            else:  # Soft attributes (fabric, style, etc.)
                if isinstance(value, list):
                    for v in value:
                        filtered = filtered[filtered[attr].str.contains(v, case=False, na=False)]
                else:
                    filtered = filtered[filtered[attr].str.contains(value, case=False, na=False)]
            
            logger.debug(f"After {attr} filter: {len(filtered)} products remaining")
            
        return filtered
    
    @staticmethod
    def _score_products(products_df: pd.DataFrame, attributes: Dict) -> pd.DataFrame:
        """Score products based on soft attribute matches"""
        logger.debug("Starting product scoring")
        products_df = products_df.copy()
        
        # Add score column if it doesn't exist
        if 'score' not in products_df.columns:
            products_df['score'] = 0
        
        # Scoring logic for soft attributes
        soft_attrs = ['fabric', 'fit', 'style', 'color_or_print', 'sleeve_length', 'occasion']
        for attr in soft_attrs:
            if attr in attributes and attr in products_df.columns:
                target_value = attributes[attr]
                if isinstance(target_value, list):
                    for value in target_value:
                        products_df.loc[products_df[attr].str.contains(value, case=False, na=False), 'score'] += 1
                else:
                    products_df.loc[products_df[attr].str.contains(target_value, case=False, na=False), 'score'] += 1
                logger.debug(f"After scoring {attr}: max score = {products_df['score'].max()}")
        
        return products_df.sort_values('score', ascending=False)

class FashionAgent:
    """Main conversational fashion agent"""
    
    def __init__(self, products_df: pd.DataFrame, api_key: str):
        self.products_df = products_df
        self.state = ConversationState()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info(f"Initialized FashionAgent with {len(products_df)} products")
        
    async def process_message(self, user_message: str) -> Dict:
        """Process user message and return response"""
        logger.info(f"Processing message: {user_message}")
        self.state.add_message("user", user_message)
        
        # Get AI response
        ai_response = await self._get_ai_response(user_message)
        logger.debug(f"AI Response: {ai_response}")
        
        # Update conversation state with extracted and inferred attributes
        if isinstance(ai_response, dict):
            self.state.extracted_attrs.update(ai_response.get('extracted_attributes', {}))
            self.state.inferred_attrs.update(ai_response.get('inferred_attributes', {}))
            self.state.combined_attrs = {**self.state.inferred_attrs, **self.state.extracted_attrs}
            logger.debug(f"Updated attributes: {self.state.combined_attrs}")
            
            # Handle different response types
            response_type = ai_response.get('type')
            
            if response_type == 'followup' and self.state.should_ask_followup():
                logger.info("Creating followup response for followup count",self.state.followup_count )
                self.state.followup_count += 1
                return self._create_followup_response(ai_response)
            elif response_type == 'direct_conversation':
                return {
                    "type": "direct_conversation",
                    "message": ai_response['message'],
                    "followup_question": ai_response.get('followup_question', ''),
                    "attributes_so_far": self.state.combined_attrs,
                    "recommendations": []
                }
            elif response_type == 'recommendation':
                # If we don't have enough info, force a followup instead of recommendation
                if not self.state.has_enough_info():
                    self.state.followup_count += 1
                    return self._create_followup_response({
                        "type": "followup",
                        "message": "I'd love to help you find the perfect outfit! To give you the best recommendations, I need a bit more information.",
                        "followup_question": "Could you tell me what type of outfit you're looking for (dress, top, pants, etc.) and your preferred size?",
                        "extracted_attributes": ai_response.get('extracted_attributes', {}),
                        "inferred_attributes": ai_response.get('inferred_attributes', {})
                    })
                return self._create_recommendation_response()
        
        # If we get here, something went wrong with the AI response
        return self._fallback_response(user_message)
    
    
    def _build_prompt(self, message: str) -> str:
        """Build the prompt for AI"""
        logger.info(f"Conversation history: {self.state.messages[-3:] if len(self.state.messages) > 3 else self.state.messages}")
        logger.info(f"Current attributes: {self.state.combined_attrs}")
        
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
- Conversation history: {self.state.messages[-3:] if len(self.state.messages) > 3 else self.state.messages}
- Followup count: {self.state.followup_count}/2
- Current attributes: {self.state.combined_attrs}

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

    async def _get_ai_response(self, message: str) -> Dict:
        """Get structured response from AI"""
        # Check for greetings/small talk first
        if self._is_greeting_or_small_talk(message):
            return {
                "type": "direct_conversation",
                "message": "Hello! I'm your fashion shopping assistant. How can I help you find the perfect outfit today?",
                "extracted_attributes": {},
                "inferred_attributes": {},
                "recommendations": []  # Add empty recommendations list
            }
            
        prompt = self._build_prompt(message)
        
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
                
                # Force followup if we don't have enough information
                if ai_response.get('type') == 'recommendation' and not self.state.has_enough_info():
                    ai_response['type'] = 'followup'
                    ai_response['message'] = "I'd love to help you find the perfect outfit! To give you the best recommendations, I need a bit more information."
                    ai_response['followup_question'] = "Could you tell me what type of outfit you're looking for (dress, top, pants, etc.) and your preferred size?"
                    ai_response['recommendations'] = []  # Ensure recommendations is empty for followup
                
                return ai_response
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Raw response: {response_text}")
                return self._fallback_response(message)
                
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> Dict:
        """Fallback response if AI fails"""
        # Simple keyword extraction for non-greetings
        extracted = {}
        inferred = VibeToAttributeMapper.infer_attributes(message)
        
        # Basic size extraction
        sizes = re.findall(r'\b(XS|S|M|L|XL|XXL)\b', message.upper())
        if sizes:
            extracted['size'] = sizes
            
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
    
    def _create_followup_response(self, ai_response: Dict) -> Dict:
        """Create followup question response"""
        # Add the assistant's message to the conversation state
        self.state.add_message("assistant", ai_response['message'])
        
        # Create the response with both the message and followup question
        response = {
            "type": "followup",
            "message": ai_response['message'],
            "followup_question": ai_response.get('followup_question', ''),
            "attributes_so_far": self.state.combined_attrs,
            "recommendations": [],  # Explicitly set empty recommendations for followup
            "messages": self.state.messages,  # Include the full conversation history
        }
        
        return response
    
    def _create_recommendation_response(self) -> Dict:
        """Create product recommendations"""
        logger.info("Creating recommendation response")
        # Get product recommendations
        recommendations = ProductFilter.filter_products(
            self.products_df, 
            self.state.combined_attrs,
            top_k=3
        )
        
        logger.debug(f"Found {len(recommendations)} recommendations")
        logger.debug(f"Recommendations DataFrame:\n{recommendations}")
        
        # Check if these are fallback recommendations
        is_fallback = bool(recommendations['is_fallback'].iloc[0]) if len(recommendations) > 0 else False
        
        # Format recommendations
        rec_list = []
        for _, product in recommendations.iterrows():
            try:
                rec = {
                    "id": str(product['id']),
                    "name": str(product['name']),
                    "price": float(product['price']),
                    "category": str(product['category']),
                    "available_sizes": str(product['available_sizes']),
                    "match_reason": self._generate_match_reason(product.to_dict())
                }
                logger.debug(f"Formatted recommendation: {rec}")
                rec_list.append(rec)
            except KeyError as e:
                logger.error(f"Missing required field in product data: {e}")
                continue
        
        # Create justification
        justification = self._generate_justification()
        
        if is_fallback:
            response_message = f"I couldn't find an exact match for your request, but here are some similar items you might like:\n\n"
        else:
            response_message = f"{justification}\n\nHere are my top recommendations:\n\n"
        
        self.state.add_message("assistant", response_message)
        
        # Reset followup count after making a recommendation
        self.state.followup_count = 0
        
        return {
            "type": "recommendation", 
            "message": response_message,
            "recommendations": rec_list,
            "final_attributes": self.state.combined_attrs,
            "justification": justification,
            "is_fallback": is_fallback
        }
    
    def _generate_match_reason(self, product: Dict) -> str:
        """Generate reason why product matches"""
        reasons = []
        
        for attr, value in self.state.combined_attrs.items():
            if attr in product and product[attr] == value:
                reasons.append(f"matches {attr}: {value}")
        
        return f"Perfect for your request: {', '.join(reasons[:2])}" if reasons else "Great match for your style"
    
    def _generate_justification(self) -> str:
        """Generate justification for recommendations"""
        extracted_parts = []
        inferred_parts = []
        
        for attr, value in self.state.extracted_attrs.items():
            if isinstance(value, list):
                extracted_parts.append(f"{attr}: {', '.join(map(str, value))}")
            else:
                extracted_parts.append(f"{attr}: {value}")
        
        for attr, value in self.state.inferred_attrs.items():
            if isinstance(value, list):
                inferred_parts.append(f"{attr}: {', '.join(map(str, value))}")
            else:
                inferred_parts.append(f"{attr}: {value}")
        
        justification = "Based on your request"
        if extracted_parts:
            justification += f", I focused on your specific needs: {', '.join(extracted_parts)}"
        if inferred_parts:
            justification += f" and inferred from your vibe: {', '.join(inferred_parts)}"
        
        return justification + "."

# Example usage and testing
async def main():
    # Load data from CSV
    try:
        # First, read the raw CSV content
        with open('Apparels_shared.csv', 'r') as f:
            content = f.read()
        
        # Clean up the content
        # Remove extra spaces and normalize newlines
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r',\s+', ',', content)
        
        # Split into lines and clean each line
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip():  # Skip empty lines
                # Remove extra spaces around commas
                line = re.sub(r'\s*,\s*', ',', line.strip())
                cleaned_lines.append(line)
        
        # Write cleaned content to a temporary file
        temp_file = 'temp_cleaned.csv'
        with open(temp_file, 'w') as f:
            f.write('\n'.join(cleaned_lines))
        
        # Load the cleaned CSV
        products_df = pd.read_csv(temp_file)
        
        # Clean up the data
        # Fill NaN values with empty strings for string columns
        string_columns = products_df.select_dtypes(include=['object']).columns
        products_df[string_columns] = products_df[string_columns].fillna('')
        
        # Convert price to float
        products_df['price'] = pd.to_numeric(products_df['price'], errors='coerce').fillna(0)
        
        # Ensure all string columns are properly formatted
        for col in string_columns:
            products_df[col] = products_df[col].astype(str).str.strip()
        
        # Remove any duplicate rows
        products_df = products_df.drop_duplicates()
        
        # Clean up temporary file
        os.remove(temp_file)
        
        # Verify the data structure
        required_columns = ['id', 'name', 'category', 'available_sizes', 'price']
        missing_columns = [col for col in required_columns if col not in products_df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return
            
        logger.info(f"Loaded {len(products_df)} products from CSV")
        logger.debug(f"CSV columns: {products_df.columns.tolist()}")
        logger.debug(f"Data types:\n{products_df.dtypes}")
        logger.debug(f"First few products:\n{products_df.head()}")
        
        # Verify we have the expected data
        if len(products_df) == 0:
            logger.error("No products loaded from CSV")
            return
            
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return

    # Initialize agent (replace with your API key)
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    if not api_key:
        logger.error("GOOGLE_GEMINI_API_KEY environment variable not set")
        return
        
    agent = FashionAgent(products_df, api_key)
    
    # Test conversation
    test_queries = [
        "I'm looking for a black dress for a party",
        "Something casual for summer brunch"
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        response = await agent.process_message(query)
        print(f"Agent: {response['message']}")
        
        if response['type'] == 'recommendation':
            print("\nRecommendations:")
            for rec in response['recommendations']:
                print(f"• {rec['name']} (${rec['price']:.2f})")
                print(f"  Available sizes: {rec['available_sizes']}")
                print(f"  {rec['match_reason']}\n")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())