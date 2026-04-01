import sys
import os
import pandas as pd
import numpy as np
import streamlit as st

# Ensure parent package (app, models) is importable
sys.path.insert(0, os.path.abspath('..'))

from app import SmartRecommendationApp, create_demo_preferences

st.set_page_config(page_title='SmartReco Demo', layout='wide')

# Currency conversion: 1 USD = 84 INR (approximate)
USD_TO_INR = 84

def format_currency(amount):
    """Convert USD to INR and format with ₹ symbol"""
    return f"₹{amount * USD_TO_INR:,.0f}"

@st.cache_resource
def get_app():
    return SmartRecommendationApp(data_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

app = get_app()
user_prefs = create_demo_preferences()

st.sidebar.title('SmartReco — Demo Frontend')
mode = st.sidebar.selectbox('Choose view', ['Overview', 'Food Recommendations', 'Travel Recommendations', 'Trip Package', 'Budget & Expenses', 'Explore Restaurants'])

st.title('Smart Food, Travel & Expense Recommendation System')
st.markdown('A small Streamlit demo that uses the local `SmartRecommendationApp` library (Prices in Indian Rupees ₹)')

if mode == 'Overview':
    st.subheader('System Overview')
    stats = app.get_stats()
    st.write(stats)
    st.markdown('### Sample demo user')
    st.json({
        'user_id': user_prefs.user_id,
        'budget_range': user_prefs.budget_range,
        'group_size': user_prefs.group_size,
        'preferred_cuisines': [c.value for c in user_prefs.preferred_cuisines],
        'travel_preferences': [c.value for c in user_prefs.travel_preferences],
        'currency': 'Indian Rupees (₹)'
    })

elif mode == 'Food Recommendations':
    st.subheader('Food Recommendations')
    top_n = st.sidebar.slider('Top N', 1, 20, 5)
    if st.button('Get Food Recommendations'):
        recs = app.get_food_recommendations(user_prefs, top_n=top_n)
        if not recs:
            st.info('No recommendations found')
        else:
            rows = []
            for r in recs:
                rows.append({
                    'Name': r.item_name,
                    'Score': round(r.similarity_score, 2),
                    'Rating': r.rating,
                    'Est Cost': format_currency(getattr(r, 'estimated_cost', getattr(r, 'average_cost', 0))),
                    'Reason': (r.reasoning[0] if r.reasoning else '')
                })
            st.dataframe(pd.DataFrame(rows))

elif mode == 'Travel Recommendations':
    st.subheader('Travel Recommendations')
    budget = st.sidebar.number_input('Budget (₹)', value=1500*USD_TO_INR, step=5000)
    top_n = st.sidebar.slider('Top N', 1, 20, 5)
    if st.button('Get Travel Recommendations'):
        recs = app.get_travel_recommendations(user_prefs, budget=budget/USD_TO_INR, top_n=top_n)
        rows = []
        for r in recs:
            rows.append({
                'Name': r.item_name,
                'Score': round(r.similarity_score, 2),
                'Rating': r.rating,
                'Est Trip Cost (3d)': format_currency(getattr(r, 'estimated_cost', 0)),
                'Reason': (r.reasoning[0] if r.reasoning else '')
            })
        st.dataframe(pd.DataFrame(rows))

elif mode == 'Trip Package':
    st.subheader('Trip Package Recommendation')
    total_budget = st.sidebar.number_input('Total Budget (₹)', value=2000*USD_TO_INR, step=5000)
    if st.button('Get Trip Package'):
        trip = app.get_trip_package(user_prefs, total_budget=total_budget/USD_TO_INR)
        st.json(trip)
        if trip.get('status') == 'success':
            st.metric('Estimated Total Cost', format_currency(trip.get('estimated_total_cost', 0)))

elif mode == 'Budget & Expenses':
    st.subheader('Budget & Expense Tracking')
    total_budget = st.sidebar.number_input('Total Budget for summary (₹)', value=2000*USD_TO_INR, step=5000)
    if st.button('Compute Budget Summary'):
        summary = app.get_budget_summary(user_prefs.user_id, total_budget/USD_TO_INR)
        st.write('Total Budget:', format_currency(summary.total_budget))
        st.write('Total Spent:', format_currency(summary.total_spent))
        st.write('Remaining:', format_currency(summary.budget_remaining))
        st.write('Avg Daily Spend:', format_currency(summary.average_daily_spend))
        st.write('Spending by Category:')
        spending_inr = {k: v * USD_TO_INR for k, v in summary.spending_by_category.items()}
        st.bar_chart(pd.Series(spending_inr))

    st.markdown('### Add Expense')
    from models.models import ExpenseCategory
    with st.form('add_expense'):
        cat = st.selectbox('Category', [c for c in ExpenseCategory])
        amt = st.number_input('Amount (₹)', min_value=0.0, value=1680.0)
        desc = st.text_input('Description', value='')
        submitted = st.form_submit_button('Add')
        if submitted:
            app.add_expense(user_prefs.user_id, cat, float(amt)/USD_TO_INR, desc)
            st.success('Expense added')

    if st.button('Show Logged Expenses'):
        # Filter expenses for demo user
        exps = [e for e in app.expenses if getattr(e, 'user_id', None) == user_prefs.user_id]
        if exps:
            rows = [{'Category': e.category.value if hasattr(e.category, 'value') else str(e.category), 'Amount': format_currency(e.amount), 'Description': e.description} for e in exps]
            st.table(pd.DataFrame(rows))
        else:
            st.info('No expenses logged for demo user')

elif mode == 'Explore Restaurants':
    st.subheader('Explore Restaurants')
    cuisines = sorted({r.cuisine_type.value for r in app.restaurants})
    sel = st.selectbox('Cuisine', ['All'] + cuisines)
    filtered = app.restaurants if sel == 'All' else [r for r in app.restaurants if r.cuisine_type.value == sel]
    rows = [{'Name': r.name, 'Cuisine': r.cuisine_type.value, 'Rating': r.rating, 'Avg Cost': format_currency(r.average_cost)} for r in filtered]
    st.dataframe(pd.DataFrame(rows))

st.markdown('---')
st.caption('Streamlit demo for the Smart Recommendation System — tailored for local testing and demos.')
