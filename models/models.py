"""Data models for Smart Recommendation System"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class Cuisine(Enum):
    ITALIAN = "Italian"
    CHINESE = "Chinese"
    INDIAN = "Indian"
    MEXICAN = "Mexican"
    JAPANESE = "Japanese"
    THAI = "Thai"
    AMERICAN = "American"
    MEDITERRANEAN = "Mediterranean"
    KOREAN = "Korean"
    INDIAN_FUSION = "Indian Fusion"
    FRENCH = "French"
    SPANISH = "Spanish"
    TURKISH = "Turkish"
    LEBANESE = "Lebanese"
    VIETNAMESE = "Vietnamese"
    GREEK = "Greek"
    PORTUGUESE = "Portuguese"
    BRAZILIAN = "Brazilian"
    PERUVIAN = "Peruvian"
    ARGENTINIAN = "Argentinian"


class TravelCategory(Enum):
    BEACH = "Beach"
    MOUNTAIN = "Mountain"
    URBAN = "Urban"
    HISTORICAL = "Historical"
    ADVENTURE = "Adventure"
    CULTURAL = "Cultural"
    WELLNESS = "Wellness"
    FAMILY = "Family"
    ENTERTAINMENT = "Entertainment"
    NATURE = "Nature"


class ExpenseCategory(Enum):
    FOOD = "Food"
    ACCOMMODATION = "Accommodation"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    ACTIVITIES = "Activities"
    NIGHTLIFE = "Nightlife"
    DINING = "Dining"


@dataclass
class UserPreferences:
    """User food and travel preferences"""
    user_id: str
    preferred_cuisines: List[Cuisine] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    budget_range: str = "Medium"  # Low, Medium, High
    travel_preferences: List[TravelCategory] = field(default_factory=list)
    group_size: int = 1
    desired_temperature: str = "Any"  # Hot, Cold, Moderate, Any
    spice_level: str = "Medium"  # Low, Medium, High
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Restaurant:
    """Restaurant data model"""
    restaurant_id: str
    name: str
    cuisine_type: Cuisine
    rating: float
    price_range: str  # Low, Medium, High
    location: str
    average_cost: float
    reviews_count: int
    dietary_options: List[str] = field(default_factory=list)
    specialties: List[str] = field(default_factory=list)
    opening_hours: str = "9 AM - 11 PM"
    
    def get_similarity_score(self, preferences: UserPreferences) -> float:
        """Calculate similarity between restaurant and user preferences"""
        score = 0.0
        
        # Cuisine match
        if self.cuisine_type in preferences.preferred_cuisines:
            score += 3.0
        
        # Budget match
        if self.price_range == preferences.budget_range:
            score += 2.0
        elif preferences.budget_range == "High" and self.price_range in ["Medium", "High"]:
            score += 1.0
        elif preferences.budget_range == "Low" and self.price_range == "Low":
            score += 1.5
        
        # Dietary restrictions
        dietary_match = sum(1 for restriction in preferences.dietary_restrictions 
                          if any(opt.lower() == restriction.lower() 
                                for opt in self.dietary_options))
        if dietary_match > 0:
            score += 2.0
        elif len(preferences.dietary_restrictions) == 0:
            score += 1.0
        
        # Rating boost
        score += (self.rating / 10) * 2
        
        return score


@dataclass
class Destination:
    """Travel destination data model"""
    destination_id: str
    name: str
    category: TravelCategory
    country: str
    distance_km: float
    estimated_cost_per_day: float
    rating: float
    best_season: str
    population: str  # Small, Medium, Large, Mega
    attractions_count: int
    restaurants_count: int
    activities: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)
    
    def get_similarity_score(self, preferences: UserPreferences, budget_available: float) -> float:
        """Calculate similarity between destination and user preferences"""
        score = 0.0
        
        # Category match
        if self.category in preferences.travel_preferences:
            score += 3.0
        
        # Budget feasibility (assuming 3-day trip)
        trip_cost = self.estimated_cost_per_day * 3
        if trip_cost <= budget_available * 0.7:
            score += 2.5
        elif trip_cost <= budget_available:
            score += 1.5
        
        # Group size preference
        if self.population == "Large" and preferences.group_size > 2:
            score += 1.0
        elif self.population == "Small" and preferences.group_size <= 2:
            score += 1.0
        
        # Rating boost
        score += (self.rating / 10) * 2
        
        # Attraction count bonus
        if self.attractions_count > 10:
            score += 1.5
        
        return score


@dataclass
class Expense:
    """Expense tracking data model"""
    expense_id: str
    user_id: str
    category: ExpenseCategory
    amount: float
    currency: str = "USD"
    description: str = ""
    date: datetime = field(default_factory=datetime.now)
    location: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Expense amount cannot be negative")


@dataclass
class Recommendation:
    """Recommendation object"""
    item_id: str
    item_name: str
    item_type: str  # "restaurant", "destination", "combo"
    similarity_score: float
    reasoning: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    rating: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.item_name} (Score: {self.similarity_score:.2f}) - {self.reasoning[0] if self.reasoning else ''}"


@dataclass
class BudgetSummary:
    """User's expense and budget summary"""
    user_id: str
    total_spent: float
    budget_remaining: float
    total_budget: float
    spending_by_category: Dict[str, float] = field(default_factory=dict)
    average_daily_spend: float = 0.0
    
    def get_budget_percentage_used(self) -> float:
        """Calculate percentage of budget used"""
        if self.total_budget == 0:
            return 0.0
        return (self.total_spent / self.total_budget) * 100
    
    def is_within_budget(self) -> bool:
        """Check if spending is within budget"""
        return self.budget_remaining >= 0
