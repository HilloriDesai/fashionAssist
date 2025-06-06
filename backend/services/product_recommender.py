import logging
import pandas as pd
from typing import Dict, List

logger = logging.getLogger(__name__)

class ProductRecommender:
    """
    Handles product recommendations and filtering.
    Works with ProductFilter to provide smart recommendations.
    """
    
    def __init__(self, products_df: pd.DataFrame):
        """
        Initialize the product recommender.
        
        Args:
            products_df: DataFrame containing product information
        """
        self.products_df = products_df
        logger.info(f"Initialized ProductRecommender with {len(products_df)} products")
        
    def get_recommendations(self, attributes: Dict, top_k: int = 3) -> pd.DataFrame:
        """
        Get product recommendations based on attributes.
        
        Args:
            attributes: User preferences and requirements
            top_k: Number of recommendations to return
            
        Returns:
            DataFrame containing recommended products
        """
        from .product_filter import ProductFilter
        return ProductFilter.filter_products(self.products_df, attributes, top_k)