"""Recommendation engines for food, travel, and combined recommendations"""

from typing import List, Dict, Optional
from models.models import (
    Restaurant, Destination, UserPreferences, Recommendation,
    ExpenseCategory, Expense, BudgetSummary
)
from datetime import datetime, timedelta
import statistics


class FoodRecommender:
    """Recommends restaurants based on user preferences"""
    
    def __init__(self, restaurants: List[Restaurant]):
        self.restaurants = restaurants
    
    def recommend_restaurants(self, preferences: UserPreferences, top_n: int = 5) -> List[Recommendation]:
        """Get top N restaurant recommendations"""
        scores = []
        
        for restaurant in self.restaurants:
            score = restaurant.get_similarity_score(preferences)
            scores.append((restaurant, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for restaurant, score in scores[:top_n]:
            reasoning = self._generate_reasoning(restaurant, preferences)
            rec = Recommendation(
                item_id=restaurant.restaurant_id,
                item_name=restaurant.name,
                item_type="restaurant",
                similarity_score=score,
                reasoning=reasoning,
                estimated_cost=restaurant.average_cost,
                rating=restaurant.rating
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_reasoning(self, restaurant: Restaurant, preferences: UserPreferences) -> List[str]:
        """Generate human-readable reasons for recommendation"""
        reasons = []
        
        if restaurant.cuisine_type in preferences.preferred_cuisines:
            reasons.append(f"Matches your preferred {restaurant.cuisine_type.value} cuisine")
        
        if restaurant.rating >= 4.5:
            reasons.append(f"Highly rated ({restaurant.rating}/5.0)")
        
        if restaurant.price_range == preferences.budget_range:
            reasons.append(f"Fits your {preferences.budget_range} budget")
        
        dietary_match = [opt for opt in restaurant.dietary_options 
                        if any(opt.lower() == restriction.lower() 
                               for restriction in preferences.dietary_restrictions)]
        if dietary_match:
            reasons.append(f"Offers {', '.join(dietary_match)} options")
        
        if not reasons:
            reasons.append("Good overall match for your preferences")
        
        return reasons[:3]  # Return top 3 reasons
    
    def get_restaurants_by_cuisine(self, cuisine_type, limit: int = 10000) -> List[Restaurant]:
        """Filter restaurants by cuisine type
        
        Args:
            cuisine_type: The cuisine type to filter by
            limit: Maximum number of restaurants to return (default: 10,000)
        
        Returns:
            List of restaurants matching the cuisine, up to the limit
        """
        restaurants = [r for r in self.restaurants 
                      if r.cuisine_type == cuisine_type]
        return restaurants[:limit]
    
    def get_restaurants_by_budget(self, budget_range: str, limit: int = 10000) -> List[Restaurant]:
        """Filter restaurants by price range
        
        Args:
            budget_range: The price range to filter by
            limit: Maximum number of restaurants to return (default: 10,000)
        
        Returns:
            List of restaurants matching the budget, up to the limit
        """
        restaurants = [r for r in self.restaurants 
                      if r.price_range == budget_range]
        return restaurants[:limit]


class TravelRecommender:
    """Recommends travel destinations based on user preferences"""
    
    def __init__(self, destinations: List[Destination]):
        self.destinations = destinations
    
    def recommend_destinations(self, preferences: UserPreferences, 
                              budget_available: float, top_n: int = 5) -> List[Recommendation]:
        """Get top N destination recommendations"""
        scores = []
        
        for destination in self.destinations:
            score = destination.get_similarity_score(preferences, budget_available)
            scores.append((destination, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for destination, score in scores[:top_n]:
            reasoning = self._generate_reasoning(destination, preferences, budget_available)
            rec = Recommendation(
                item_id=destination.destination_id,
                item_name=destination.name,
                item_type="destination",
                similarity_score=score,
                reasoning=reasoning,
                estimated_cost=destination.estimated_cost_per_day * 3,  # 3-day trip
                rating=destination.rating
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_reasoning(self, destination: Destination, 
                           preferences: UserPreferences, 
                           budget_available: float) -> List[str]:
        """Generate human-readable reasons for recommendation"""
        reasons = []
        
        if destination.category in preferences.travel_preferences:
            reasons.append(f"Matches your interest in {destination.category.value} travel")
        
        if destination.rating >= 4.5:
            reasons.append(f"Highly rated destination ({destination.rating}/5.0)")
        
        trip_cost = destination.estimated_cost_per_day * 3
        if trip_cost <= budget_available:
            reasons.append(f"Fits within your budget (est. ${trip_cost:.0f} for 3 days)")
        
        if destination.attractions_count > 10:
            reasons.append(f"Rich with {destination.attractions_count} attractions")
        
        if not reasons:
            reasons.append("Great destination to explore")
        
        return reasons[:3]
    
    def get_destinations_by_category(self, category, limit: int = 10) -> List[Destination]:
        """Filter destinations by category"""
        return [d for d in self.destinations 
                if d.category == category][:limit]
    
    def get_budget_friendly_destinations(self, max_cost: float, limit: int = 10) -> List[Destination]:
        """Get destinations within budget"""
        return [d for d in self.destinations 
                if d.estimated_cost_per_day <= max_cost][:limit]


class ExpenseRecommender:
    """Provides expense tracking and budget recommendations"""
    
    def __init__(self, expenses: List[Expense]):
        self.expenses = expenses
    
    def get_budget_summary(self, user_id: str, total_budget: float) -> BudgetSummary:
        """Get expense summary for a user"""
        user_expenses = [e for e in self.expenses if e.user_id == user_id]
        
        total_spent = sum(e.amount for e in user_expenses)
        budget_remaining = total_budget - total_spent
        
        # Calculate by category
        spending_by_category = {}
        for category in ExpenseCategory:
            spent = sum(e.amount for e in user_expenses if e.category == category)
            if spent > 0:
                spending_by_category[category.value] = spent
        
        # Calculate daily average
        if user_expenses:
            days_span = (max(e.date for e in user_expenses) - 
                        min(e.date for e in user_expenses)).days + 1
            average_daily = total_spent / max(days_span, 1)
        else:
            average_daily = 0.0
        
        return BudgetSummary(
            user_id=user_id,
            total_spent=total_spent,
            budget_remaining=budget_remaining,
            total_budget=total_budget,
            spending_by_category=spending_by_category,
            average_daily_spend=average_daily
        )
    
    def get_spending_recommendations(self, budget_summary: BudgetSummary) -> List[str]:
        """Get budget and spending recommendations"""
        recommendations = []
        
        budget_percentage = budget_summary.get_budget_percentage_used()
        
        if budget_percentage > 90:
            recommendations.append("⚠️ ALERT: You've used over 90% of your budget!")
        elif budget_percentage > 75:
            recommendations.append("⚠️ WARNING: You're approaching your budget limit (75%+ used)")
        
        if not budget_summary.is_within_budget():
            overspend = abs(budget_summary.budget_remaining)
            recommendations.append(f"❌ You've exceeded your budget by ${overspend:.2f}")
        
        # Category-based recommendations
        categories = budget_summary.spending_by_category
        if categories:
            max_category = max(categories.items(), key=lambda x: x[1])
            if max_category[1] > budget_summary.total_budget * 0.4:
                recommendations.append(f"💡 Tip: {max_category[0]} is {(max_category[1]/budget_summary.total_budget)*100:.1f}% of your budget")
        
        if budget_percentage < 50:
            recommendations.append("✅ Good job! You're on track with your spending")
        
        return recommendations
    
    def add_expense(self, expense: Expense):
        """Add new expense"""
        self.expenses.append(expense)
    
    def get_expenses_by_category(self, user_id: str, category: ExpenseCategory) -> List[Expense]:
        """Get all expenses for a user in a category"""
        return [e for e in self.expenses 
                if e.user_id == user_id and e.category == category]
    
    def get_expenses_by_date_range(self, user_id: str, 
                                   start_date: datetime, 
                                   end_date: datetime) -> List[Expense]:
        """Get expenses within a date range"""
        return [e for e in self.expenses 
                if e.user_id == user_id and start_date <= e.date <= end_date]


class ComboRecommender:
    """Combines food and travel recommendations with budget constraints"""
    
    def __init__(self, food_recommender: FoodRecommender, 
                 travel_recommender: TravelRecommender,
                 expense_recommender: ExpenseRecommender):
        self.food_recommender = food_recommender
        self.travel_recommender = travel_recommender
        self.expense_recommender = expense_recommender
    
    def recommend_trip_package(self, preferences: UserPreferences, 
                              total_budget: float, 
                              existing_expenses: List[Expense]) -> Dict:
        """Recommend a complete trip package with food and travel"""
        
        # Calculate remaining budget
        budget_summary = self.expense_recommender.get_budget_summary(
            preferences.user_id, total_budget
        )
        remaining_budget = budget_summary.budget_remaining
        
        if remaining_budget <= 0:
            return {
                "status": "error",
                "message": "Budget exceeded. No recommendations available."
            }
        
        # Recommend destination (uses 70% of remaining budget)
        destination_budget = remaining_budget * 0.7
        destinations = self.travel_recommender.recommend_destinations(
            preferences, destination_budget, top_n=3
        )
        
        # Recommend restaurants (uses 30% of remaining budget)
        food_budget = remaining_budget * 0.3
        restaurants = self.food_recommender.recommend_restaurants(
            preferences, top_n=5
        )
        
        return {
            "status": "success",
            "budget_summary": {
                "total_budget": total_budget,
                "spent": budget_summary.total_spent,
                "remaining": remaining_budget,
                "percentage_used": budget_summary.get_budget_percentage_used()
            },
            "destination_recommendations": destinations,
            "restaurant_recommendations": restaurants,
            "estimated_total_cost": (destinations[0].estimated_cost if destinations else 0) + 
                                   (restaurants[0].estimated_cost * 3 if restaurants else 0)  # 3 meals
        }
