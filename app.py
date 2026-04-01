"""Main application module for Smart Recommendation System"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add paths for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from models.models import (
    UserPreferences, Restaurant, Destination, Expense,
    Cuisine, TravelCategory, ExpenseCategory, Recommendation
)
from models.recommenders import (
    FoodRecommender, TravelRecommender, ExpenseRecommender, ComboRecommender
)
from utils.data_utils import (
    load_restaurants_from_csv, load_destinations_from_csv,
    load_expenses_from_csv, create_sample_restaurants,
    create_sample_destinations, format_recommendation_for_display,
    save_recommendations_to_json
)


class SmartRecommendationApp:
    """Main application for Smart Food, Travel & Expense Recommendations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.restaurants: List[Restaurant] = []
        self.destinations: List[Destination] = []
        self.expenses: List[Expense] = []
        
        # Initialize recommenders
        self.food_recommender = None
        self.travel_recommender = None
        self.expense_recommender = None
        self.combo_recommender = None
        
        self._load_data()
        self._initialize_recommenders()
    
    def _load_data(self):
        """Load data from CSV files or create sample data"""
        print("Loading data...")
        
        # Try to load from CSV, fall back to sample data
        restaurants_csv = Path(self.data_dir) / "restaurants.csv"
        if restaurants_csv.exists():
            self.restaurants = load_restaurants_from_csv(str(restaurants_csv))
        else:
            self.restaurants = create_sample_restaurants()
            print(f"  [i] Using {len(self.restaurants)} sample restaurants")
        
        destinations_csv = Path(self.data_dir) / "destinations.csv"
        if destinations_csv.exists():
            self.destinations = load_destinations_from_csv(str(destinations_csv))
        else:
            self.destinations = create_sample_destinations()
            print(f"  [i] Using {len(self.destinations)} sample destinations")
        
        expenses_csv = Path(self.data_dir) / "expenses.csv"
        if expenses_csv.exists():
            self.expenses = load_expenses_from_csv(str(expenses_csv))
            print(f"  [OK] Loaded {len(self.expenses)} expenses")
        else:
            self.expenses = []
            print(f"  [i] No expense data loaded yet")
        
        print(f"[OK] Data loaded: {len(self.restaurants)} restaurants, "
              f"{len(self.destinations)} destinations\n")
    
    def _initialize_recommenders(self):
        """Initialize all recommender engines"""
        self.food_recommender = FoodRecommender(self.restaurants)
        self.travel_recommender = TravelRecommender(self.destinations)
        self.expense_recommender = ExpenseRecommender(self.expenses)
        self.combo_recommender = ComboRecommender(
            self.food_recommender,
            self.travel_recommender,
            self.expense_recommender
        )
    
    def get_food_recommendations(self, preferences: UserPreferences, top_n: int = 5) -> List[Recommendation]:
        """Get personalized restaurant recommendations"""
        return self.food_recommender.recommend_restaurants(preferences, top_n)
    
    def get_travel_recommendations(self, preferences: UserPreferences, 
                                  budget: float, top_n: int = 5) -> List[Recommendation]:
        """Get personalized destination recommendations"""
        return self.travel_recommender.recommend_destinations(preferences, budget, top_n)
    
    def get_trip_package(self, preferences: UserPreferences, total_budget: float) -> Dict:
        """Get a complete trip recommendation with food and travel"""
        return self.combo_recommender.recommend_trip_package(
            preferences, total_budget, self.expenses
        )
    
    def add_expense(self, user_id: str, category: ExpenseCategory, 
                   amount: float, description: str = "", location: str = "") -> str:
        """Add a new expense"""
        expense = Expense(
            expense_id=f"exp_{len(self.expenses) + 1}",
            user_id=user_id,
            category=category,
            amount=amount,
            description=description,
            location=location
        )
        self.expense_recommender.add_expense(expense)
        self.expenses.append(expense)
        return expense.expense_id
    
    def get_budget_summary(self, user_id: str, total_budget: float):
        """Get budget summary for a user"""
        return self.expense_recommender.get_budget_summary(user_id, total_budget)
    
    def get_spending_recommendations(self, user_id: str, total_budget: float) -> List[str]:
        """Get spending recommendations based on budget"""
        budget_summary = self.expense_recommender.get_budget_summary(user_id, total_budget)
        return self.expense_recommender.get_spending_recommendations(budget_summary)
    
    def create_user_profile(self, user_id: str, budget_range: str = "Medium",
                           group_size: int = 1) -> UserPreferences:
        """Create a new user profile"""
        return UserPreferences(
            user_id=user_id,
            budget_range=budget_range,
            group_size=group_size
        )
    
    def explore_restaurants_by_cuisine(self, cuisine: Cuisine, limit: int = 10000):
        """Explore restaurants by cuisine type (up to 10,000)"""
        restaurants = self.food_recommender.get_restaurants_by_cuisine(cuisine, limit)
        return restaurants
    
    def explore_destinations_by_category(self, category: TravelCategory, limit: int = 10):
        """Explore destinations by category"""
        destinations = self.travel_recommender.get_destinations_by_category(category, limit)
        return destinations
    
    def get_stats(self) -> Dict:
        """Get application statistics"""
        return {
            "total_restaurants": len(self.restaurants),
            "total_destinations": len(self.destinations),
            "total_expenses_tracked": len(self.expenses),
            "cuisines_available": len(Cuisine),
            "travel_categories": len(TravelCategory),
            "expense_categories": len(ExpenseCategory)
        }


def create_demo_preferences() -> UserPreferences:
    """Create demo user preferences for testing"""
    prefs = UserPreferences(
        user_id="user_demo_001",
        preferred_cuisines=[Cuisine.ITALIAN, Cuisine.CHINESE, Cuisine.MEDITERRANEAN],
        dietary_restrictions=["Vegetarian"],
        budget_range="Medium",
        travel_preferences=[TravelCategory.BEACH, TravelCategory.CULTURAL],
        group_size=2,
        spice_level="Medium"
    )
    return prefs


def main():
    """Main function demonstrating the application"""
    print("=" * 70)
    print("SMART FOOD, TRAVEL & EXPENSE RECOMMENDATION SYSTEM")
    print("=" * 70)
    print()
    
    # Initialize app
    app = SmartRecommendationApp()
    
    # Display stats
    stats = app.get_stats()
    print("System Statistics:")
    for key, value in stats.items():
        print(f"   * {key}: {value}")
    print()
    
    # Create demo user
    print("Creating Demo User Profile...")
    user_prefs = create_demo_preferences()
    print(f"   User ID: {user_prefs.user_id}")
    print(f"   Budget: {user_prefs.budget_range}")
    print(f"   Group Size: {user_prefs.group_size}")
    print(f"   Dietary Preferences: {user_prefs.dietary_restrictions}")
    print()
    
    # Get food recommendations
    print("FOOD RECOMMENDATIONS")
    print("-" * 70)
    food_recs = app.get_food_recommendations(user_prefs, top_n=3)
    for i, rec in enumerate(food_recs, 1):
        print(f"{i}. {rec.item_name} (Score: {rec.similarity_score:.2f})")
        if rec.reasoning:
            print(f"   Why: {rec.reasoning[0]}")
    
    # Get travel recommendations
    print("\nTRAVEL RECOMMENDATIONS")
    print("-" * 70)
    travel_recs = app.get_travel_recommendations(user_prefs, budget=1500, top_n=3)
    for i, rec in enumerate(travel_recs, 1):
        print(f"{i}. {rec.item_name} (Score: {rec.similarity_score:.2f})")
        if rec.reasoning:
            print(f"   Why: {rec.reasoning[0]}")
    
    # Get complete trip package
    print("\nCOMPLETE TRIP PACKAGE RECOMMENDATION")
    print("-" * 70)
    trip = app.get_trip_package(user_prefs, total_budget=2000)
    
    if trip['status'] == 'success':
        print(f"Budget Summary:")
        print(f"  * Total Budget: ${trip['budget_summary']['total_budget']:.2f}")
        print(f"  * Already Spent: ${trip['budget_summary']['spent']:.2f}")
        print(f"  * Remaining: ${trip['budget_summary']['remaining']:.2f}")
        print(f"  * Budget Used: {trip['budget_summary']['percentage_used']:.1f}%")
        print(f"\nEstimated Trip Cost: ${trip['estimated_total_cost']:.2f}")
        
        if trip['destination_recommendations']:
            print(f"\nRecommended Destination:")
            dest = trip['destination_recommendations'][0]
            print(f"   {dest.item_name} (Score: {dest.similarity_score:.2f})")
            print(f"   Est. Cost: ${dest.estimated_cost:.2f}")
        
        if trip['restaurant_recommendations']:
            print(f"\nRecommended Restaurants:")
            for rec in trip['restaurant_recommendations'][:2]:
                print(f"   * {rec.item_name} - ${rec.estimated_cost:.2f}/meal")
    
    # Budget tracking example
    print("\n\nBUDGET TRACKING EXAMPLE")
    print("-" * 70)
    
    # Add some sample expenses
    app.add_expense(user_prefs.user_id, ExpenseCategory.ACCOMMODATION, 150, "Hotel for 1 night")
    app.add_expense(user_prefs.user_id, ExpenseCategory.FOOD, 45, "Dinner at Mario's")
    app.add_expense(user_prefs.user_id, ExpenseCategory.TRANSPORT, 50, "Taxi rides")
    
    budget_summary = app.get_budget_summary(user_prefs.user_id, 2000)
    print(f"User: {user_prefs.user_id}")
    print(f"Total Budget: ${budget_summary.total_budget:.2f}")
    print(f"Spent: ${budget_summary.total_spent:.2f}")
    print(f"Remaining: ${budget_summary.budget_remaining:.2f}")
    print(f"Average Daily Spend: ${budget_summary.average_daily_spend:.2f}")
    
    print(f"\nSpending by Category:")
    for category, amount in budget_summary.spending_by_category.items():
        pct = (amount / budget_summary.total_budget) * 100
        print(f"   * {category}: ${amount:.2f} ({pct:.1f}%)")
    
    recommendations = app.get_spending_recommendations(user_prefs.user_id, 2000)
    print(f"\nBudget Recommendations:")
    for rec in recommendations:
        print(f"   {rec}")
    
    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
