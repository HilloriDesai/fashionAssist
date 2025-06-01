import pandas as pd
import asyncio
import os
from dotenv import load_dotenv
from services.fashion_agent import FashionAgent

# Load environment variables from .env file
load_dotenv()

async def simple_cli():
    products_df = pd.read_csv('Apparels_shared.csv')
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_GEMINI_API_KEY not found in .env file")
    
    agent = FashionAgent(products_df, api_key)
    
    print("Fashion Agent Ready! Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        response = await agent.process_message(user_input)
        print(f"Agent: {response['message']}")
        
        if response['type'] == 'recommendation':
            print("\n📦 Recommendations:")
            for rec in response['recommendations']:
                print(f"• {rec['name']} - ${rec['price']} ({rec['match_reason']})")

if __name__ == "__main__":
    asyncio.run(simple_cli())