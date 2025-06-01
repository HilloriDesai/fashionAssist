"""
Constants used across the fashion assistant services.
"""

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