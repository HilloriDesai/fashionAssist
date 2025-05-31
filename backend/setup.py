import pandas as pd

def load_products(csv_path):
    """Load and validate product data"""
    df = pd.read_csv(csv_path)
    
    # Ensure required columns exist
    required_cols = ['name', 'price', 'category']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"Warning: Missing columns {missing_cols}")
    
    return df

# Test with sample data if CSV not ready
products = load_products('apparels_shared.csv')