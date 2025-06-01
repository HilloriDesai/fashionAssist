import logging
from typing import Dict, List
from .conversation_manager import ConversationManager
from .product_recommender import ProductRecommender
from .product_filter import ProductFilter

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """
    Handles formatting of different types of responses for the fashion agent.
    Manages the creation of followup, recommendation, and direct conversation responses.
    """
    
    def __init__(self, conversation_manager: ConversationManager, product_recommender: ProductRecommender):
        """
        Initialize the response formatter.
        
        Args:
            conversation_manager: Manager for conversation state
            product_recommender: Recommender for product suggestions
        """
        self.conversation_manager = conversation_manager
        self.product_recommender = product_recommender
        logger.info("Initialized Response Formatter")
    
    def create_followup_response(self, ai_response: Dict) -> Dict:
        """
        Create followup question response.
        
        Args:
            ai_response: Response from AI containing followup information
            
        Returns:
            Dict containing formatted followup response
        """
        # Add the assistant's message to the conversation state
        self.conversation_manager.add_message("assistant", ai_response['message'])
        
        # Create the response with both the message and followup question
        response = {
            "type": "followup",
            "message": ai_response['message'],
            "followup_question": ai_response.get('followup_question', ''),
            "attributes_so_far": self.conversation_manager.get_attributes(),
            "recommendations": [],
            "messages": self.conversation_manager.get_messages(),
        }
        
        return response
    
    def create_recommendation_response(self) -> Dict:
        """
        Create product recommendations response.
        
        Returns:
            Dict containing formatted recommendation response
        """
        logger.info("Creating recommendation response")
        
        # Get product recommendations
        recommendations = ProductFilter.filter_products(
            self.product_recommender.products_df,
            self.conversation_manager.get_attributes(),
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
        
        self.conversation_manager.add_message("assistant", response_message)
        
        # Reset followup count after making a recommendation
        self.conversation_manager.state["followup_count"] = 0
        
        return {
            "type": "recommendation", 
            "message": response_message,
            "recommendations": rec_list,
            "final_attributes": self.conversation_manager.get_attributes(),
            "justification": justification,
            "is_fallback": is_fallback
        }
    
    def _generate_match_reason(self, product: Dict) -> str:
        """
        Generate reason why product matches user's preferences.
        
        Args:
            product: Product information dictionary
            
        Returns:
            String explaining why the product matches
        """
        reasons = []
        
        for attr, value in self.conversation_manager.get_attributes().items():
            if attr in product and product[attr] == value:
                reasons.append(f"matches {attr}: {value}")
        
        return f"Perfect for your request: {', '.join(reasons[:2])}" if reasons else "Great match for your style"
    
    def _generate_justification(self) -> str:
        """
        Generate justification for recommendations.
        
        Returns:
            String explaining the recommendation rationale
        """
        extracted_parts = []
        inferred_parts = []
        
        for attr, value in self.conversation_manager.get_extracted_attributes().items():
            if isinstance(value, list):
                extracted_parts.append(f"{attr}: {', '.join(map(str, value))}")
            else:
                extracted_parts.append(f"{attr}: {value}")
        
        for attr, value in self.conversation_manager.get_inferred_attributes().items():
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