Streamlit Frontend for Smart Recommendation System
=================================================

Quickstart
---------

1. Create a Python environment (optional but recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:

   ```powershell
   cd frontend
   streamlit run streamlit_app.py
   ```

Notes
-----
- The frontend loads the local `SmartRecommendationApp` module from the parent folder. Ensure you run Streamlit from the `smart-reco` folder or that `app.py` and `models/` are reachable relative to the frontend script.
- This demo is intended for local development and exploration, not production deployment.
