# Expense Tracker (Flask + SQLite)

A simple web app to record, filter and summarise personal expenses.

## Features
- Add, edit and delete expenses (full CRUD)
- Filter by category and month using SQL queries
- Automatic total and per-category percentage breakdown
- Server-side input validation + SQLite `CHECK` constraint
- Unit tests with unittest

## UI
Gen-Z dark theme: aurora gradient background, glassmorphism cards, pill buttons and emoji accents (pure CSS, no JS frameworks).

## Tech
Python, Flask, SQLite, HTML, CSS (Jinja2 templates)

## Run
```bash
pip install -r requirements.txt
python app.py        # open http://127.0.0.1:5000
python -m unittest   # run tests
```
