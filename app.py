import os
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Set DATABASE_PATH to a persistent location on hosting if one is available.
DEFAULT_DB = Path(app.instance_path) / "inventory.db"
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", str(DEFAULT_DB)))
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL DEFAULT 'General',
                price REAL NOT NULL DEFAULT 0,
                quantity INTEGER NOT NULL DEFAULT 0,
                description TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            db.executemany("""
                INSERT INTO products (name, sku, category, price, quantity, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                ("Wireless Mouse", "ASH-001", "Electronics", 599.00, 24, "Compact wireless mouse"),
                ("Notebook Set", "ASH-002", "Stationery", 149.00, 12, "Pack of ruled notebooks"),
                ("Desk Lamp", "ASH-003", "Home & Office", 899.00, 5, "LED desk lamp"),
            ])

def product_dict(row):
    item = dict(row)
    item["price"] = round(float(item["price"]), 2)
    return item

@app.route("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.route("/styles.css")
def styles():
    return send_from_directory(app.root_path, "styles.css")


@app.route("/script.js")
def script():
    return send_from_directory(app.root_path, "script.js")

@app.route("/api/products", methods=["GET"])
def list_products():
    query = request.args.get("q", "").strip()
    with get_db() as db:
        if query:
            pattern = f"%{query}%"
            rows = db.execute("""
                SELECT * FROM products
                WHERE name LIKE ? OR sku LIKE ? OR category LIKE ?
                ORDER BY id DESC
            """, (pattern, pattern, pattern)).fetchall()
        else:
            rows = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return jsonify([product_dict(row) for row in rows])

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    sku = str(data.get("sku", "")).strip().upper()
    category = str(data.get("category", "General")).strip() or "General"
    description = str(data.get("description", "")).strip()
    try:
        price = float(data.get("price", 0))
        quantity = int(data.get("quantity", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Price must be a number and quantity must be a whole number."}), 400

    if not name or not sku:
        return jsonify({"error": "Product name and SKU are required."}), 400
    if price < 0 or quantity < 0:
        return jsonify({"error": "Price and quantity cannot be negative."}), 400

    try:
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO products (name, sku, category, price, quantity, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, sku, category, price, quantity, description))
            row = db.execute("SELECT * FROM products WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(product_dict(row)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "That SKU already exists. Please use a unique SKU."}), 409

@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    sku = str(data.get("sku", "")).strip().upper()
    category = str(data.get("category", "General")).strip() or "General"
    description = str(data.get("description", "")).strip()
    try:
        price = float(data.get("price", 0))
        quantity = int(data.get("quantity", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Price must be a number and quantity must be a whole number."}), 400

    if not name or not sku:
        return jsonify({"error": "Product name and SKU are required."}), 400
    if price < 0 or quantity < 0:
        return jsonify({"error": "Price and quantity cannot be negative."}), 400

    try:
        with get_db() as db:
            cursor = db.execute("""
                UPDATE products
                SET name = ?, sku = ?, category = ?, price = ?, quantity = ?, description = ?
                WHERE id = ?
            """, (name, sku, category, price, quantity, description, product_id))
            if cursor.rowcount == 0:
                return jsonify({"error": "Product not found."}), 404
            row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return jsonify(product_dict(row))
    except sqlite3.IntegrityError:
        return jsonify({"error": "That SKU already exists. Please use a unique SKU."}), 409

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    with get_db() as db:
        cursor = db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found."}), 404
    return jsonify({"message": "Product deleted."})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
