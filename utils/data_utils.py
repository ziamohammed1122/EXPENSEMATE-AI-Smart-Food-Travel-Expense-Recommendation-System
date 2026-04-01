"""Utility functions for data processing and file handling"""

import csv
import json
from typing import List, Dict, Any
from models.models import (
    Restaurant, Destination, Expense, UserPreferences,
    Cuisine, TravelCategory, ExpenseCategory
)
from datetime import datetime


def load_restaurants_from_csv(filepath: str) -> List[Restaurant]:
    """Load restaurant data from CSV file"""
    restaurants = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    restaurant = Restaurant(
                        restaurant_id=row['restaurant_id'],
                        name=row['name'],
                        cuisine_type=Cuisine[row['cuisine_type'].upper()],
                        rating=float(row['rating']),
                        price_range=row['price_range'],
                        location=row['location'],
                        average_cost=float(row['average_cost']),
                        reviews_count=int(row['reviews_count']),
                        dietary_options=row.get('dietary_options', '').split(',') if row.get('dietary_options') else [],
                        specialties=row.get('specialties', '').split(',') if row.get('specialties') else [],
                        opening_hours=row.get('opening_hours', '9 AM - 11 PM')
                    )
                    restaurants.append(restaurant)
                except (KeyError, ValueError) as e:
                    print(f"Error loading restaurant: {e}")
                    continue
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    return restaurants


def load_destinations_from_csv(filepath: str) -> List[Destination]:
    """Load destination data from CSV file"""
    destinations = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    destination = Destination(
                        destination_id=row['destination_id'],
                        name=row['name'],
                        category=TravelCategory[row['category'].upper()],
                        country=row['country'],
                        distance_km=float(row['distance_km']),
                        estimated_cost_per_day=float(row['estimated_cost_per_day']),
                        rating=float(row['rating']),
                        best_season=row['best_season'],
                        population=row['population'],
                        attractions_count=int(row['attractions_count']),
                        restaurants_count=int(row['restaurants_count']),
                        activities=row.get('activities', '').split(',') if row.get('activities') else [],
                        highlights=row.get('highlights', '').split(',') if row.get('highlights') else []
                    )
                    destinations.append(destination)
                except (KeyError, ValueError) as e:
                    print(f"Error loading destination: {e}")
                    continue
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    return destinations


def load_expenses_from_csv(filepath: str) -> List[Expense]:
    """Load expense data from CSV file"""
    expenses = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    expense = Expense(
                        expense_id=row['expense_id'],
                        user_id=row['user_id'],
                        category=ExpenseCategory[row['category'].upper()],
                        amount=float(row['amount']),
                        currency=row.get('currency', 'USD'),
                        description=row.get('description', ''),
                        date=datetime.fromisoformat(row['date']),
                        location=row.get('location', ''),
                        tags=row.get('tags', '').split(',') if row.get('tags') else []
                    )
                    expenses.append(expense)
                except (KeyError, ValueError) as e:
                    print(f"Error loading expense: {e}")
                    continue
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    return expenses


def save_recommendations_to_json(recommendations: List, filepath: str):
    """Save recommendations to JSON file"""
    rec_data = []
    for rec in recommendations:
        rec_data.append({
            'item_id': rec.item_id,
            'item_name': rec.item_name,
            'item_type': rec.item_type,
            'similarity_score': rec.similarity_score,
            'reasoning': rec.reasoning,
            'estimated_cost': rec.estimated_cost,
            'rating': rec.rating
        })
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rec_data, f, indent=2)
        print(f"Recommendations saved to {filepath}")
    except Exception as e:
        print(f"Error saving recommendations: {e}")


def create_sample_restaurants() -> List[Restaurant]:
    """Create sample restaurant data"""
    return [
        Restaurant(
            restaurant_id="r1",
            name="Mario's Italian Kitchen",
            cuisine_type=Cuisine.ITALIAN,
            rating=4.7,
            price_range="Medium",
            location="Downtown",
            average_cost=45.0,
            reviews_count=523,
            dietary_options=["Vegetarian", "Vegan"],
            specialties=["Pasta", "Risotto"]
        ),
        Restaurant(
            restaurant_id="r2",
            name="Golden Dragon",
            cuisine_type=Cuisine.CHINESE,
            rating=4.3,
            price_range="Low",
            location="Chinatown",
            average_cost=25.0,
            reviews_count=456,
            dietary_options=["Gluten-free"],
            specialties=["Dim Sum", "Noodles"]
        ),
        Restaurant(
            restaurant_id="r3",
            name="Spice Garden",
            cuisine_type=Cuisine.INDIAN,
            rating=4.6,
            price_range="Medium",
            location="Midtown",
            average_cost=35.0,
            reviews_count=612,
            dietary_options=["Vegetarian", "Vegan", "Gluten-free"],
            specialties=["Curry", "Tandoori", "Biryani"]
        ),
        Restaurant(
            restaurant_id="r4",
            name="Sakura Sushi",
            cuisine_type=Cuisine.JAPANESE,
            rating=4.8,
            price_range="High",
            location="Downtown",
            average_cost=65.0,
            reviews_count=734,
            dietary_options=["Vegetarian", "Gluten-free"],
            specialties=["Sushi", "Sashimi", "Ramen"]
        ),
        Restaurant(
            restaurant_id="r5",
            name="Bangkok Sunset",
            cuisine_type=Cuisine.THAI,
            rating=4.5,
            price_range="Medium",
            location="Midtown",
            average_cost=32.0,
            reviews_count=445,
            dietary_options=["Vegetarian", "Vegan"],
            specialties=["Pad Thai", "Curry", "Spring Rolls"]
        ),
        Restaurant(
            restaurant_id="r6",
            name="Mediterranean Coast",
            cuisine_type=Cuisine.MEDITERRANEAN,
            rating=4.4,
            price_range="Medium",
            location="Harbor",
            average_cost=48.0,
            reviews_count=389,
            dietary_options=["Vegetarian", "Vegan", "Gluten-free"],
            specialties=["Seafood", "Olive Oil", "Fresh Vegetables"]
        ),
    ]


def create_sample_destinations() -> List[Destination]:
    """Create sample destination data"""
    return [
        Destination(
            destination_id="d1",
            name="Bali, Indonesia",
            category=TravelCategory.BEACH,
            country="Indonesia",
            distance_km=8000,
            estimated_cost_per_day=60,
            rating=4.7,
            best_season="April-October",
            population="Large",
            attractions_count=15,
            restaurants_count=200,
            activities=["Surfing", "Yoga", "Diving"],
            highlights=["Temples", "Rice Paddies", "Volcanic Mountains"]
        ),
        Destination(
            destination_id="d2",
            name="Swiss Alps",
            category=TravelCategory.MOUNTAIN,
            country="Switzerland",
            distance_km=6000,
            estimated_cost_per_day=150,
            rating=4.9,
            best_season="June-September",
            population="Small",
            attractions_count=20,
            restaurants_count=150,
            activities=["Hiking", "Skiing", "Mountain Biking"],
            highlights=["Glaciers", "Alpine Lakes", "Scenic Trains"]
        ),
        Destination(
            destination_id="d3",
            name="Tokyo, Japan",
            category=TravelCategory.URBAN,
            country="Japan",
            distance_km=9000,
            estimated_cost_per_day=100,
            rating=4.6,
            best_season="March-May, September-November",
            population="Mega",
            attractions_count=30,
            restaurants_count=500,
            activities=["Shopping", "Technology", "Culture"],
            highlights=["Temples", "Modern Architecture", "Street Food"]
        ),
        Destination(
            destination_id="d4",
            name="Rome, Italy",
            category=TravelCategory.HISTORICAL,
            country="Italy",
            distance_km=5000,
            estimated_cost_per_day=80,
            rating=4.8,
            best_season="April-May, September-October",
            population="Large",
            attractions_count=25,
            restaurants_count=300,
            activities=["History", "Art", "Food"],
            highlights=["Colosseum", "Vatican", "Ancient Ruins"]
        ),
        Destination(
            destination_id="d5",
            name="Nepal Adventure",
            category=TravelCategory.ADVENTURE,
            country="Nepal",
            distance_km=7000,
            estimated_cost_per_day=40,
            rating=4.5,
            best_season="October-November, March-April",
            population="Small",
            attractions_count=18,
            restaurants_count=100,
            activities=["Trekking", "Mountaineering", "Rafting"],
            highlights=["Mount Everest", "Kathmandu Valley", "Monasteries"]
        ),
        Destination(
            destination_id="d6",
            name="Barcelona, Spain",
            category=TravelCategory.CULTURAL,
            country="Spain",
            distance_km=5500,
            estimated_cost_per_day=75,
            rating=4.7,
            best_season="May-June, September-October",
            population="Large",
            attractions_count=22,
            restaurants_count=400,
            activities=["Architecture", "Beach", "Nightlife"],
            highlights=["Sagrada Familia", "Park Güell", "Gothic Quarter"]
        ),
    ]


def format_recommendation_for_display(recommendation) -> str:
    """Format recommendation for nice display"""
    text = f"\n{'='*60}\n"
    text += f"🎯 {recommendation.item_name}\n"
    text += f"{'='*60}\n"
    text += f"Type: {recommendation.item_type.upper()}\n"
    text += f"Match Score: {recommendation.similarity_score:.2f}/10\n"
    text += f"Rating: {'⭐' * int(recommendation.rating)} ({recommendation.rating:.1f}/5.0)\n"
    text += f"Estimated Cost: ${recommendation.estimated_cost:.2f}\n"
    text += f"\nWhy You'll Love It:\n"
    for i, reason in enumerate(recommendation.reasoning, 1):
        text += f"  {i}. {reason}\n"
    text += f"{'='*60}\n"
    return text
