import logging
import pandas as pd
from typing import Dict, List

logger = logging.getLogger(__name__)

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
        
        # Verify required columns exist
        required_columns = ['id', 'name', 'category', 'price', 'available_sizes']
        missing_columns = [col for col in required_columns if col not in products_df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(f"DataFrame missing required columns: {missing_columns}")
        
        filtered = products_df.copy()
        removed_filters = []
        
        # Sort attributes by priority (lowest priority first)
        sorted_attrs = sorted(
            attributes.items(),
            key=lambda x: ProductFilter.ATTRIBUTE_PRIORITIES.get(x[0], 0)
        )
        
        # Try filtering with all attributes first
        filtered = ProductFilter._apply_filters(filtered, dict(sorted_attrs))
        
        # If no results or not enough results, try removing filters one by one
        if len(filtered) == 0 or len(filtered) < top_k:
            logger.info(f"Not enough results ({len(filtered)}), applying fallback logic")
            
            # First try: Remove non-essential filters (priority < 4)
            for attr, value in sorted_attrs:
                if len(filtered) >= top_k:
                    break
                    
                # Skip essential filters (priority >= 4)
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
            
            # Second try: If still no results, try with only category and size
            if len(filtered) == 0:
                logger.info("No results after first fallback, trying with only category and size")
                essential_filters = {
                    k: v for k, v in attributes.items() 
                    if k in ['category', 'size'] and k in attributes
                }
                if essential_filters:
                    filtered = ProductFilter._apply_filters(products_df.copy(), essential_filters)
                    removed_filters = [k for k in attributes.keys() if k not in essential_filters]
                    logger.info(f"Trying with only essential filters. New count: {len(filtered)}")
            
            # Final fallback: If still no results, try with just category
            if len(filtered) == 0 and 'category' in attributes:
                logger.info("No results after second fallback, trying with only category")
                filtered = ProductFilter._apply_filters(
                    products_df.copy(), 
                    {'category': attributes['category']}
                )
                removed_filters = [k for k in attributes.keys() if k != 'category']
                logger.info(f"Trying with only category. New count: {len(filtered)}")
        
        # Score remaining products
        filtered = ProductFilter._score_products(filtered, attributes)
        
        # Add metadata about filtering process
        filtered['is_fallback'] = len(removed_filters) > 0
        filtered['removed_filters'] = str(removed_filters) if len(removed_filters) > 0 else ''
        
        logger.info(f"Final filtered product count: {len(filtered)}")
        logger.debug(f"Removed filters: {removed_filters}")
        
        return filtered.head(top_k)
    
    @staticmethod
    def _apply_filters(products_df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Apply filters to products DataFrame"""
        filtered = products_df.copy()
        
        for attr, value in filters.items():
            if attr == 'price_max':
                filtered = filtered[filtered['price'] <= value]
            elif attr == 'size':
                # Check if size is in available_sizes
                filtered = filtered[filtered['available_sizes'].str.contains(value, case=False, na=False)]
            elif attr in filtered.columns:
                if isinstance(value, list):
                    # For lists, check if any value matches
                    mask = filtered[attr].str.lower().isin([v.lower() for v in value])
                    filtered = filtered[mask]
                else:
                    # For single values, use contains for better matching
                    filtered = filtered[filtered[attr].str.contains(value, case=False, na=False)]
        
        return filtered
    
    @staticmethod
    def _score_products(products_df: pd.DataFrame, attributes: Dict) -> pd.DataFrame:
        """Score products based on attribute matches"""
        scored = products_df.copy()
        scored['score'] = 0
        
        for attr, value in attributes.items():
            if attr in scored.columns:
                if isinstance(value, list):
                    scored['score'] += scored[attr].isin(value).astype(int)
                else:
                    scored['score'] += (scored[attr] == value).astype(int)
        
        # Sort by score in descending order
        return scored.sort_values('score', ascending=False)