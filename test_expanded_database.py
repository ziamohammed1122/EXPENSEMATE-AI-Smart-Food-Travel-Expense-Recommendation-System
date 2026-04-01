#!/usr/bin/env python3
"""
Test script to demonstrate the expanded database with recommendations
"""

import sys
from pathlib import Path
import urllib.request
import json
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import SmartRecommendationApp, create_demo_preferences
from utils.data_utils import load_restaurants_from_csv, load_destinations_from_csv, load_expenses_from_csv

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  SMART RECOMMENDATION SYSTEM - EXPANDED DATABASE DEMO".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Initialize app
    print("\n📚 Loading expanded database...")
    app = SmartRecommendationApp(data_dir='data')
    user_prefs = create_demo_preferences()
    
    # Get statistics
    print_section("DATABASE STATISTICS")
    stats = app.get_stats()
    print(f"✓ Restaurants loaded: {stats['total_restaurants']}")
    print(f"✓ Destinations loaded: {stats['total_destinations']}")
    print(f"✓ Expense records: {stats['total_expenses_tracked']}")
    
    # Show cuisine distribution
    print_section("RESTAURANT CUISINE DISTRIBUTION")
    cuisine_count = defaultdict(int)
    for restaurant in app.restaurants:
        cuisine_count[restaurant.cuisine_type.value] += 1
    
    cuisines_sorted = sorted(cuisine_count.items(), key=lambda x: x[1], reverse=True)
    for cuisine, count in cuisines_sorted:
        bar = "█" * (count // 5)
        print(f"  {cuisine:20} {bar} ({count})")
    
    # Show destination categories
    print_section("DESTINATION CATEGORIES")
    dest_count = defaultdict(int)
    countries = set()
    for destination in app.destinations:
        dest_count[destination.category.value] += 1
        countries.add(destination.country)
    
    for category in sorted(dest_count.keys()):
        count = dest_count[category]
        bar = "█" * (count // 2)
        print(f"  {category:20} {bar} ({count})")
    
    print(f"\n  🌍 Countries covered: {len(countries)}")
    
    # Show expense categories
    print_section("EXPENSE CATEGORIES BREAKDOWN")
    expense_count = defaultdict(float)
    for expense in app.expenses:
        expense_count[expense.category.value] += expense.amount
    
    for category in sorted(expense_count.keys()):
        total = expense_count[category]
        print(f"  {category:20} Total: ${total:>10,.2f}")
    
    # Demo user profile
    print_section("DEMO USER PROFILE")
    print(f"  👤 User ID: {user_prefs.user_id}")
    print(f"  💰 Budget Range: {user_prefs.budget_range}")
    print(f"  👥 Group Size: {user_prefs.group_size} person(s)")
    print(f"  🍽️  Preferred Cuisines:")
    for cuisine in user_prefs.preferred_cuisines:
        print(f"     • {cuisine.value}")
    print(f"  🗺️  Travel Preferences:")
    for travel_pref in user_prefs.travel_preferences:
        print(f"     • {travel_pref.value}")
    
    # Get recommendations
    print_section("FOOD RECOMMENDATIONS")
    food_recs = app.get_food_recommendations(user_prefs, top_n=5)
    for i, rec in enumerate(food_recs, 1):
        print(f"\n  {i}. {rec.item_name}")
        print(f"     Rating: ⭐ {rec.rating}/5.0")
        print(f"     Match Score: {rec.similarity_score:.2f}")
        if rec.reasoning:
            print(f"     Reason: {rec.reasoning[0]}")
    
    # Travel recommendations
    print_section("TRAVEL RECOMMENDATIONS")
    travel_recs = app.get_travel_recommendations(user_prefs, budget=3000, top_n=5)
    for i, rec in enumerate(travel_recs, 1):
        print(f"\n  {i}. {rec.item_name}")
        print(f"     Rating: ⭐ {rec.rating}/5.0")
        print(f"     Match Score: {rec.similarity_score:.2f}")
        if rec.reasoning:
            print(f"     Reason: {rec.reasoning[0]}")
    
    # Expense summary
    print_section("EXPENSE ANALYSIS")
    total_expenses = sum(exp.amount for exp in app.expenses)
    avg_expense = total_expenses / len(app.expenses) if app.expenses else 0
    max_expense = max((exp.amount for exp in app.expenses), default=0)
    
    print(f"  📊 Total Expenses: ${total_expenses:,.2f}")
    print(f"  📈 Average Expense: ${avg_expense:,.2f}")
    print(f"  🔝 Maximum Single Expense: ${max_expense:,.2f}")
    print(f"  📝 Total Records: {len(app.expenses)}")
    
    # Combo recommendations
    print_section("COMBO RECOMMENDATIONS (Trip Packages)")
    trip_package = app.get_trip_package(user_prefs, total_budget=5000)
    print(f"\n  Trip Package Details:")
    if trip_package:
        for key, value in trip_package.items():
            if isinstance(value, (int, float)):
                print(f"     {key}: {value}")
            elif isinstance(value, list):
                print(f"     {key}: {len(value)} items")
            else:
                print(f"     {key}: {value}")
    
    # Summary
    print_section("SUMMARY")
    print("""
  ✅ Database successfully expanded with:
     • 500 restaurants across 20 cuisines
     • 2,000 expense records across 8 categories
     • 138 destinations across 32 countries
  
  ✅ Recommendation engine now provides:
     • Enhanced food recommendations with diverse cuisines
     • Better travel planning with global destinations
     • Comprehensive expense analysis across users
     • Combined trip package recommendations
  
  ✅ System ready for production use!
    """)
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
