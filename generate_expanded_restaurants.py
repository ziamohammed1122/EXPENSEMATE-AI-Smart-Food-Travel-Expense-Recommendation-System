"""Script to generate expanded restaurant database with up to 10,000 restaurants per cuisine"""

import csv
import random
from itertools import cycle

# Configuration
CUISINES = ['ITALIAN', 'CHINESE', 'MEXICAN', 'JAPANESE', 'INDIAN', 'AMERICAN', 'FRENCH', 'THAI']
LOCATIONS = ['Chinatown', 'University Area', 'Financial District', 'Uptown', 'Downtown', 
             'Beach Area', 'Suburban', 'Old Town', 'Entertainment District', 'Harbor',
             'City Center', 'Riverside', 'Mountain View', 'Arts District', 'Tech Park']
DIETARY_OPTIONS = [
    ['Halal', 'Gluten-free', 'Vegan', 'Kosher'],
    ['Organic'],
    ['Organic', 'Kosher', 'Low-Carb'],
    ['Vegetarian', 'Vegan'],
    ['Gluten-free', 'Low-Carb'],
    ['Halal', 'Kosher'],
    ['Organic', 'Vegetarian'],
    ['Vegan', 'Gluten-free']
]

CUISINES_SPECIALTIES = {
    'ITALIAN': ['Seafood Pasta', 'Pizza', 'Risotto', 'Pasta'],
    'CHINESE': ['Dim Sum', 'Noodles', 'Peking Duck', 'Fried Rice'],
    'MEXICAN': ['Tacos', 'Enchiladas', 'Burritos', 'Quesadillas'],
    'JAPANESE': ['Sushi', 'Ramen', 'Tempura', 'Tonkatsu'],
    'INDIAN': ['Butter Chicken', 'Biryani', 'Samosa', 'Naan'],
    'AMERICAN': ['Burgers', 'Steaks', 'BBQ', 'Ribs'],
    'FRENCH': ['Coq au Vin', 'Escargot', 'Crêpes', 'Beef Bourguignon'],
    'THAI': ['Green Curry', 'Pad Thai', 'Tom Yum', 'Satay']
}

RESTAURANT_NAMES = {
    'ITALIAN': ['Italian', 'The Italian Place', 'Italian Kitchen', 'Italian House', 'Roma', 'Bella Italia', 'Trattoria'],
    'CHINESE': ['China', 'The Chinese Place', 'Dragon', 'Golden Dragon', 'Pearl', 'Mandarin', 'Red Lantern'],
    'MEXICAN': ['Mexico', 'The Mexican Place', 'El Mercado', 'Casa Verde', 'Fiesta', 'Taco King', 'Aztec'],
    'JAPANESE': ['Japan', 'The Japanese Place', 'Sakura', 'Tokyo', 'Zen', 'Fujiyama', 'Kabuki'],
    'INDIAN': ['India', 'The Indian Place', 'Taj', 'Spice Route', 'Maharaja', 'Himalaya', 'Curry House'],
    'AMERICAN': ['American', 'The American Place', 'Liberty', 'Main Street Diner', 'Classic Grill', 'Patriot', 'Stars & Stripes'],
    'FRENCH': ['France', 'Le Français', 'Parisian', 'Monet', 'Louis', 'French Bistro', 'Provence'],
    'THAI': ['Thailand', 'The Thai Place', 'Bangkok', 'Orchid', 'Siam', 'Thai Royal', 'Golden Temple']
}

PRICE_RANGES = ['Low', 'Medium', 'High', 'Very High']


def generate_restaurants(restaurants_per_cuisine=1250):
    """Generate 10,000 restaurants (1,250 per cuisine x 8 cuisines)"""
    restaurants = []
    restaurant_id = 1
    
    for cuisine in CUISINES:
        for i in range(restaurants_per_cuisine):
            # Generate varied restaurant names
            name_template = random.choice(RESTAURANT_NAMES[cuisine])
            if i % 3 != 0 or name_template in ['Italian', 'China', 'Mexico', 'Japan', 'India', 'America', 'France', 'Thailand']:
                name = f"{name_template} {i + 1}"
            else:
                name = name_template
            
            # Generate random attributes with ratings 8.5-10
            rating = round(random.uniform(8.5, 10.0), 1)
            price_range = random.choice(PRICE_RANGES)
            location = random.choice(LOCATIONS)
            
            # Average cost based on price range
            avg_cost_range = {
                'Low': (10, 30),
                'Medium': (30, 60),
                'High': (60, 100),
                'Very High': (100, 200)
            }
            avg_cost = round(random.uniform(*avg_cost_range[price_range]), 2)
            
            reviews_count = random.randint(50, 1000)
            dietary_options = ', '.join(random.choice(DIETARY_OPTIONS))
            
            # Get specialties for the cuisine
            specialties = ', '.join(random.sample(CUISINES_SPECIALTIES[cuisine], 
                                                 k=min(3, len(CUISINES_SPECIALTIES[cuisine]))))
            
            # Random opening hours
            opening_hour = random.choice([9, 10, 11, 12])
            closing_hour = random.choice([10, 11])
            opening_hours = f"{opening_hour} AM - {closing_hour} PM"
            
            restaurants.append({
                'restaurant_id': f'r{restaurant_id}',
                'name': name,
                'cuisine_type': cuisine,
                'rating': rating,
                'price_range': price_range,
                'location': location,
                'average_cost': avg_cost,
                'reviews_count': reviews_count,
                'dietary_options': dietary_options,
                'specialties': specialties,
                'opening_hours': opening_hours
            })
            
            restaurant_id += 1
    
    return restaurants


def main():
    print("Generating expanded restaurant database...")
    restaurants = generate_restaurants(restaurants_per_cuisine=1250)
    
    # Write to CSV
    csv_file = 'data/restaurants.csv'
    fieldnames = ['restaurant_id', 'name', 'cuisine_type', 'rating', 'price_range', 
                  'location', 'average_cost', 'reviews_count', 'dietary_options', 
                  'specialties', 'opening_hours']
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(restaurants)
    
    print(f"✅ Generated {len(restaurants)} restaurants")
    print(f"   - {len(restaurants) // len(CUISINES)} restaurants per cuisine")
    print(f"   - {len(CUISINES)} different cuisines")
    print(f"   - Saved to: {csv_file}")
    
    # Print statistics
    by_cuisine = {}
    for r in restaurants:
        cuisine = r['cuisine_type']
        by_cuisine[cuisine] = by_cuisine.get(cuisine, 0) + 1
    
    print("\nRestaurants per cuisine:")
    for cuisine, count in sorted(by_cuisine.items()):
        print(f"  {cuisine}: {count}")


if __name__ == '__main__':
    main()
