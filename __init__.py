"""
Smart Food, Travel & Expense Recommendation System
A comprehensive recommendation engine for personalized restaurant and travel suggestions
with integrated expense tracking and budget management.
"""

__version__ = "1.0.0"
__author__ = "Smart Recommendation System"

from app import SmartRecommendationApp, create_demo_preferences
from models.models import (
    UserPreferences,
    Restaurant,
    Destination,
    Expense,
    Recommendation,
    BudgetSummary,
    Cuisine,
    TravelCategory,
    ExpenseCategory
)
from models.recommenders import (
    FoodRecommender,
    TravelRecommender,
    ExpenseRecommender,
    ComboRecommender
)

__all__ = [
    'SmartRecommendationApp',
    'create_demo_preferences',
    'UserPreferences',
    'Restaurant',
    'Destination',
    'Expense',
    'Recommendation',
    'BudgetSummary',
    'Cuisine',
    'TravelCategory',
    'ExpenseCategory',
    'FoodRecommender',
    'TravelRecommender',
    'ExpenseRecommender',
    'ComboRecommender',
]
