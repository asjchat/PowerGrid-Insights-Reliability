# Grid Insights Dashboard

A polished dashboard for visualizing U.S. grid reliability metrics (SAIDI, SAIFI, CAIDI), with an executive summary and metric definitions.

## Files
- `grid_insights_dashboard_app.py` — Dash application entry point
- `grid_insights_dashboard_version_1.md` — Executive summary and definitions
- `requirements.txt` — Python dependencies
- `Procfile` — Process definition for Gunicorn on platforms like Render or Heroku

## Local Run
```bash
pip install -r requirements.txt
python grid_insights_dashboard_app.py
```

## Deployment Notes
Use `grid_insights_dashboard_app:app.server` as the WSGI target for Gunicorn.
