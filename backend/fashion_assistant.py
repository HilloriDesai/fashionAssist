"""
Main entry point for the fashion assistant application.
Coordinates the interaction between different services.
"""

import logging
import asyncio
import pandas as pd
import os
import re
from services.fashion_agent import FashionAgent

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

async def main():
    """Main entry point for the fashion assistant"""
    try:
        # Load data from CSV
        products_df = await load_products_data()
        if products_df is None:
            return
            
        # Initialize agent
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
                    
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)

async def load_products_data() -> pd.DataFrame:
    """Load and clean product data from CSV"""
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
            return None
            
        logger.info(f"Loaded {len(products_df)} products from CSV")
        logger.debug(f"CSV columns: {products_df.columns.tolist()}")
        logger.debug(f"Data types:\n{products_df.dtypes}")
        logger.debug(f"First few products:\n{products_df.head()}")
        
        # Verify we have the expected data
        if len(products_df) == 0:
            logger.error("No products loaded from CSV")
            return None
            
        return products_df
            
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return None

if __name__ == "__main__":
    # Run the example
    asyncio.run(main()) 