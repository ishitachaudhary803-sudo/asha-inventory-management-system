# Product Catalogue and Inventory Management System

A beginner-friendly web application for Asha & Company. The app lets a user view and search a product catalogue, add new products, edit product details, remove products, and review basic stock statistics.

## Features
- Product catalogue with name, SKU, category, price, stock quantity, and description
- Add, edit, and delete product records
- Search by product name, SKU, or category
- Dashboard counts for products, stock units, low-stock items, and estimated inventory value
- SQLite database with sample starter records
- Input validation and duplicate-SKU checks
- Responsive layout for desktop and mobile screens

## Technology
- HTML, CSS, and JavaScript for the browser interface
- Python and Flask for server routes and application logic
- SQLite for database storage
- Gunicorn as the production web server

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Install dependencies: `pip install -r requirements.txt`
4. Start the app: `python app.py`
5. Open `http://127.0.0.1:5000` in a browser.

The SQLite database is created automatically at `instance/inventory.db` by default. Set the `DATABASE_PATH` environment variable to choose a different database file.

## Deploy on Render
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Runtime: Python

Important: Render web services have an ephemeral filesystem by default. The app can be demonstrated on a free service, but SQLite changes may be lost when the service restarts, sleeps, or redeploys. For persistent live data, configure a persistent storage location or use a managed database. Do not treat the free demo as permanent storage.

## Notes
The included products are fictional sample records for demonstrating the features. They are not actual company inventory or confidential company data.
