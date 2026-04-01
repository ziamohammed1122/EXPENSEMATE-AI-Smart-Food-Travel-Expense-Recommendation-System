"""
Flask API backend for Smart Recommendation System
Serves data to the HTML frontend
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from app import SmartRecommendationApp, create_demo_preferences
import os
from pathlib import Path

app_flask = Flask(__name__)
CORS(app_flask)

# Initialize recommendation app
recommendation_app = SmartRecommendationApp(data_dir='data')
demo_user = create_demo_preferences()

# Track database loading state
database_state = {
    'loaded': True,
    'restaurants_count': len(recommendation_app.restaurants),
    'destinations_count': len(recommendation_app.destinations),
    'expenses_count': len(recommendation_app.expenses),
    'last_loaded': None,
    'data_dir': 'data'
}

# Currency conversion
USD_TO_INR = 84

# ==================== Database Management Endpoints ====================

@app_flask.route('/api/database/status', methods=['GET'])
def get_database_status():
    """Get database loading status and statistics
    
    Returns:
    {
        'status': 'loaded' or 'error',
        'restaurants_count': number of restaurants loaded,
        'destinations_count': number of destinations loaded,
        'expenses_count': number of expenses loaded,
        'total_items': total number of items,
        'data_directory': path to data directory,
        'last_loaded': timestamp of last load
    }
    """
    try:
        return jsonify({
            'status': 'loaded' if database_state['loaded'] else 'not_loaded',
            'restaurants_count': len(recommendation_app.restaurants),
            'destinations_count': len(recommendation_app.destinations),
            'expenses_count': len(recommendation_app.expenses),
            'total_items': len(recommendation_app.restaurants) + len(recommendation_app.destinations) + len(recommendation_app.expenses),
            'data_directory': database_state['data_dir'],
            'last_loaded': database_state['last_loaded']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app_flask.route('/api/database/load', methods=['POST'])
def load_database():
    """Load/reload the database from CSV files
    
    Request JSON (optional):
    {
        'data_dir': 'data' (optional, defaults to 'data')
    }
    
    Returns:
    {
        'status': 'success' or 'error',
        'message': status message,
        'restaurants_loaded': number of restaurants,
        'destinations_loaded': number of destinations,
        'expenses_loaded': number of expenses
    }
    """
    from datetime import datetime
    
    try:
        data = request.json or {}
        data_dir = data.get('data_dir', 'data')
        
        # Check if data directory exists
        if not Path(data_dir).exists():
            return jsonify({
                'status': 'error',
                'message': f'Data directory not found: {data_dir}'
            }), 400
        
        # Reload the application with the specified data directory
        global recommendation_app
        recommendation_app = SmartRecommendationApp(data_dir=data_dir)
        
        # Update database state
        database_state['loaded'] = True
        database_state['restaurants_count'] = len(recommendation_app.restaurants)
        database_state['destinations_count'] = len(recommendation_app.destinations)
        database_state['expenses_count'] = len(recommendation_app.expenses)
        database_state['last_loaded'] = datetime.now().isoformat()
        database_state['data_dir'] = data_dir
        
        return jsonify({
            'status': 'success',
            'message': f'Database loaded successfully',
            'restaurants_loaded': len(recommendation_app.restaurants),
            'destinations_loaded': len(recommendation_app.destinations),
            'expenses_loaded': len(recommendation_app.expenses),
            'timestamp': database_state['last_loaded']
        })
        
    except Exception as e:
        database_state['loaded'] = False
        return jsonify({
            'status': 'error',
            'message': f'Failed to load database: {str(e)}'
        }), 500


@app_flask.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    stats = recommendation_app.get_stats()
    return jsonify(stats)

@app_flask.route('/api/user', methods=['GET'])
def get_user():
    """Get demo user profile"""
    return jsonify({
        'user_id': demo_user.user_id,
        'budget_range': demo_user.budget_range,
        'group_size': demo_user.group_size,
        'preferred_cuisines': [c.value for c in demo_user.preferred_cuisines],
        'travel_preferences': [c.value for c in demo_user.travel_preferences],
        'dietary_restrictions': demo_user.dietary_restrictions
    })

@app_flask.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """Get all restaurants
    
    Query parameters:
    - cuisine: Filter by cuisine type (e.g., 'ITALIAN', 'all' for no filter)
    - limit: Maximum number of results (default: 100, max: 10000)
    """
    cuisine_filter = request.args.get('cuisine', 'all')
    limit = min(int(request.args.get('limit', 100)), 10000)
    
    restaurants = []
    for r in recommendation_app.restaurants:
        if cuisine_filter == 'all' or r.cuisine_type.value == cuisine_filter:
            restaurants.append({
                'id': r.restaurant_id,
                'name': r.name,
                'cuisine': r.cuisine_type.value,
                'rating': r.rating,
                'cost': r.average_cost * USD_TO_INR,
                'price_range': r.price_range
            })
            if len(restaurants) >= limit:
                break
    return jsonify(restaurants)

@app_flask.route('/api/cuisines', methods=['GET'])
def get_cuisines():
    """Get unique cuisines"""
    cuisines = sorted({r.cuisine_type.value for r in recommendation_app.restaurants})
    return jsonify(cuisines)

@app_flask.route('/api/explore-cuisine/<cuisine>', methods=['GET'])
def explore_cuisine(cuisine):
    """Explore restaurants by specific cuisine
    
    Query parameters:
    - limit: Maximum number of results (default: 100, max: 10000)
    
    Returns up to 10,000 restaurants for the specified cuisine.
    """
    limit = min(int(request.args.get('limit', 100)), 10000)
    
    # Convert string to Cuisine enum
    from models.models import Cuisine
    try:
        cuisine_enum = Cuisine[cuisine.upper()]
    except KeyError:
        return jsonify({'error': f'Unknown cuisine: {cuisine}'}), 400
    
    restaurants = recommendation_app.food_recommender.get_restaurants_by_cuisine(
        cuisine_enum, limit=limit
    )
    
    results = []
    for r in restaurants:
        results.append({
            'id': r.restaurant_id,
            'name': r.name,
            'cuisine': r.cuisine_type.value,
            'rating': r.rating,
            'cost': r.average_cost * USD_TO_INR,
            'price_range': r.price_range,
            'location': r.location,
            'reviews': r.reviews_count,
            'dietary_options': r.dietary_options,
            'specialties': r.specialties
        })
    
    return jsonify({
        'cuisine': cuisine.upper(),
        'total_results': len(results),
        'restaurants': results
    })

@app_flask.route('/api/food-recommendations', methods=['POST'])
def get_food_recs():
    """Get food recommendations"""
    data = request.json
    top_n = data.get('top_n', 5)
    recs = recommendation_app.get_food_recommendations(demo_user, top_n=top_n)
    
    results = []
    for r in recs:
        results.append({
            'name': r.item_name,
            'score': round(r.similarity_score, 2),
            'rating': r.rating,
            'cost': getattr(r, 'estimated_cost', 0) * USD_TO_INR,
            'reasoning': r.reasoning[0] if r.reasoning else 'Great match!'
        })
    return jsonify(results)

@app_flask.route('/api/travel-recommendations', methods=['POST'])
def get_travel_recs():
    """Get travel recommendations"""
    data = request.json
    budget_inr = data.get('budget', 1500 * USD_TO_INR)
    top_n = data.get('top_n', 5)
    budget_usd = budget_inr / USD_TO_INR
    
    recs = recommendation_app.get_travel_recommendations(demo_user, budget=budget_usd, top_n=top_n)
    
    results = []
    for r in recs:
        results.append({
            'name': r.item_name,
            'score': round(r.similarity_score, 2),
            'rating': r.rating,
            'cost': getattr(r, 'estimated_cost', 0) * USD_TO_INR,
            'reasoning': r.reasoning[0] if r.reasoning else 'Perfect destination!'
        })
    return jsonify(results)

@app_flask.route('/api/trip-package', methods=['POST'])
def get_trip_pkg():
    """Get trip package recommendation"""
    data = request.json
    budget_inr = data.get('budget', 2000 * USD_TO_INR)
    budget_usd = budget_inr / USD_TO_INR
    
    trip = recommendation_app.get_trip_package(demo_user, total_budget=budget_usd)
    
    if trip['status'] == 'success':
        dest_recs = [{
            'name': d.item_name,
            'score': d.similarity_score,
            'cost': d.estimated_cost * USD_TO_INR
        } for d in trip.get('destination_recommendations', [])]
        
        food_recs = [{
            'name': f.item_name,
            'cost': f.estimated_cost * USD_TO_INR
        } for f in trip.get('restaurant_recommendations', [])]
        
        return jsonify({
            'status': 'success',
            'total_cost': trip.get('estimated_total_cost', 0) * USD_TO_INR,
            'destinations': dest_recs,
            'restaurants': food_recs
        })
    else:
        return jsonify({'status': 'error', 'message': trip.get('message')})

@app_flask.route('/api/budget-summary', methods=['POST'])
def get_budget_summary():
    """Get budget summary"""
    data = request.json
    budget_inr = data.get('budget', 2000 * USD_TO_INR)
    budget_usd = budget_inr / USD_TO_INR
    
    summary = recommendation_app.get_budget_summary(demo_user.user_id, budget_usd)
    
    spending_by_category = {}
    for cat, amt in summary.spending_by_category.items():
        spending_by_category[cat] = amt * USD_TO_INR
    
    return jsonify({
        'total_budget': summary.total_budget * USD_TO_INR,
        'total_spent': summary.total_spent * USD_TO_INR,
        'budget_remaining': summary.budget_remaining * USD_TO_INR,
        'avg_daily_spend': summary.average_daily_spend * USD_TO_INR,
        'budget_percentage': summary.get_budget_percentage_used(),
        'spending_by_category': spending_by_category
    })

@app_flask.route('/api/add-expense', methods=['POST'])
def add_expense():
    """Add an expense"""
    from models.models import ExpenseCategory
    data = request.json
    category_str = data.get('category')
    amount_inr = data.get('amount')
    description = data.get('description', '')
    
    # Convert category string to enum
    category = ExpenseCategory[category_str.upper()]
    amount_usd = amount_inr / USD_TO_INR
    
    exp_id = recommendation_app.add_expense(demo_user.user_id, category, amount_usd, description)
    return jsonify({'success': True, 'expense_id': exp_id})

@app_flask.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get logged expenses"""
    exps = [e for e in recommendation_app.expenses if getattr(e, 'user_id', None) == demo_user.user_id]
    results = [{
        'category': e.category.value if hasattr(e.category, 'value') else str(e.category),
        'amount': e.amount * USD_TO_INR,
        'description': e.description
    } for e in exps]
    return jsonify(results)

# ==================== New Frontend API Endpoints ====================

@app_flask.route('/api/recommendations/food', methods=['POST'])
def get_food_recommendations():
    """Get food recommendations with filtering
    
    Request JSON:
    {
        "budget": 50 (USD),
        "cuisine": "Italian" (optional),
        "min_rating": 3.5 (optional),
        "top_n": 5 (optional)
    }
    """
    data = request.json
    budget = data.get('budget', 50)
    cuisine = data.get('cuisine', '')
    min_rating = float(data.get('min_rating', 0))
    top_n = data.get('top_n', 5)
    
    recommendations = []
    
    for r in recommendation_app.restaurants:
        # Filter by budget and rating
        if r.average_cost <= budget and r.rating >= min_rating:
            # Filter by cuisine if specified
            if cuisine and r.cuisine_type.value != cuisine:
                continue
            
            recommendations.append({
                'id': r.restaurant_id,
                'name': r.name,
                'emoji': '🍽️',
                'description': f"{r.cuisine_type.value} • {r.location}",
                'cuisine': r.cuisine_type.value,
                'price': round(r.average_cost * USD_TO_INR, 2),
                'rating': round(r.rating, 1),
                'location': r.location,
                'reviews': r.reviews_count
            })
            
            if len(recommendations) >= top_n:
                break
    
    return jsonify({'recommendations': recommendations, 'total': len(recommendations)})

@app_flask.route('/api/recommendations/travel', methods=['POST'])
def get_travel_recommendations():
    """Get travel recommendations with filtering
    
    Request JSON:
    {
        "budget": 2000 (USD),
        "travel_type": "Adventure" (optional),
        "duration": 7 (days, optional),
        "top_n": 5 (optional)
    }
    """
    data = request.json
    budget = data.get('budget', 2000)
    travel_type = data.get('travel_type', '')
    duration = data.get('duration', 7)
    top_n = data.get('top_n', 5)
    
    recommendations = []
    
    for d in recommendation_app.destinations:
        # Filter by budget
        if hasattr(d, 'estimated_cost_per_day') and (d.estimated_cost_per_day * 3) <= budget:
            # Filter by travel type if specified
            if travel_type and d.category.value != travel_type:
                continue
            
            recommendations.append({
                'id': d.destination_id,
                'name': d.name,
                'emoji': '🌍',
                'description': f"{d.country} • {d.population}",
                'type': d.category.value if hasattr(d, 'category') else 'Adventure',
                'budget_range': f"${(d.estimated_cost_per_day * 3):.0f}",
                'rating': round(getattr(d, 'rating', 4.5), 1),
                'location': d.country,
                'best_season': getattr(d, 'best_season', 'Year-round')
            })
            
            if len(recommendations) >= top_n:
                break
    
    return jsonify({'recommendations': recommendations, 'total': len(recommendations)})

@app_flask.route('/api/recommendations/budget', methods=['POST'])
def get_budget_recommendations():
    """Get budget analysis and recommendations
    
    Request JSON:
    {
        "budget": 5000 (USD total),
        "category": "Food" (optional),
        "duration": 7 (days),
        "top_n": 5 (optional)
    }
    """
    data = request.json
    total_budget = data.get('budget', 5000)
    category = data.get('category', '')
    duration = data.get('duration', 7)
    top_n = data.get('top_n', 5)
    
    daily_budget = total_budget / duration if duration > 0 else total_budget
    
    # Suggested budget allocations
    allocations = {
        'Accommodation': {'percentage': 40, 'emoji': '🏨'},
        'Food': {'percentage': 30, 'emoji': '🍽️'},
        'Transportation': {'percentage': 15, 'emoji': '🚗'},
        'Activities': {'percentage': 10, 'emoji': '🎭'},
        'Shopping': {'percentage': 5, 'emoji': '🛍️'}
    }
    
    recommendations = []
    
    for cat, details in allocations.items():
        if category and cat != category:
            continue
        
        allocated = (total_budget * details['percentage']) / 100
        daily = allocated / duration if duration > 0 else allocated
        
        recommendations.append({
            'id': f"budget_{cat.lower()}",
            'name': f"{cat} Budget",
            'emoji': details['emoji'],
            'description': f"${daily:.2f} per day • {details['percentage']}% of total",
            'category': cat,
            'budget_range': f"${allocated:.0f} total",
            'daily_budget': f"${daily:.2f}",
            'percentage': details['percentage']
        })
        
        if len(recommendations) >= top_n:
            break
    
    return jsonify({'recommendations': recommendations, 'total': len(recommendations)})

@app_flask.route('/api/recommendations/all', methods=['GET'])
def get_all_recommendations():
    """Get all available recommendations (restaurants + destinations)"""
    recommendations = []
    
    # Add top restaurants
    for r in recommendation_app.restaurants[:5]:
        recommendations.append({
            'id': r.restaurant_id,
            'name': r.name,
            'emoji': '🍽️',
            'description': f"{r.cuisine_type.value} • {r.location}",
            'type': 'Restaurant',
            'cuisine': r.cuisine_type.value,
            'price': round(r.average_cost * USD_TO_INR, 2),
            'rating': round(r.rating, 1)
        })
    
    # Add top destinations
    for d in recommendation_app.destinations[:5]:
        recommendations.append({
            'id': d.destination_id,
            'name': d.name,
            'emoji': '🌍',
            'description': d.description,
            'type': 'Destination',
            'budget_range': f"${getattr(d, 'estimated_cost', 100) * USD_TO_INR:.0f}",
            'rating': round(getattr(d, 'rating', 4.5), 1)
        })
    
    return jsonify({'recommendations': recommendations, 'total': len(recommendations)})

if __name__ == '__main__':
    app_flask.run(debug=True, port=5000)
