import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = "change-me"
DATABASE = "expenses.db"
CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config.get("DATABASE", DATABASE))
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    with sqlite3.connect(app.config.get("DATABASE", DATABASE)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            spent_on TEXT NOT NULL)""")


@app.route("/")
def index():
    category = request.args.get("category", "")
    month = request.args.get("month", "")  # format YYYY-MM
    query, params = "SELECT * FROM expenses WHERE 1=1", []
    if category:
        query += " AND category = ?"
        params.append(category)
    if month:
        query += " AND strftime('%Y-%m', spent_on) = ?"
        params.append(month)
    expenses = get_db().execute(query + " ORDER BY spent_on DESC, id DESC", params).fetchall()
    total = sum(e["amount"] for e in expenses)

    summary = {}
    for e in expenses:
        summary[e["category"]] = summary.get(e["category"], 0) + e["amount"]
    return render_template("index.html", expenses=expenses, total=total, summary=summary,
                           categories=CATEGORIES, today=date.today().isoformat(),
                           sel_category=category, sel_month=month)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "")
    spent_on = request.form.get("spent_on", "")
    try:
        amount = float(request.form.get("amount", ""))
    except ValueError:
        amount = 0
    if not title or amount <= 0 or category not in CATEGORIES or not spent_on:
        flash("Please enter a valid title, amount, category and date.", "error")
        return redirect(url_for("index"))
    db = get_db()
    db.execute("INSERT INTO expenses (title, amount, category, spent_on) VALUES (?,?,?,?)",
               (title, amount, category, spent_on))
    db.commit()
    flash("Expense added.")
    return redirect(url_for("index"))


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit(expense_id):
    db = get_db()
    expense = db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if expense is None:
        return "Expense not found", 404
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "error")
            return redirect(url_for("edit", expense_id=expense_id))
        db.execute("UPDATE expenses SET title=?, amount=?, category=?, spent_on=? WHERE id=?",
                   (request.form["title"].strip(), amount, request.form["category"],
                    request.form["spent_on"], expense_id))
        db.commit()
        flash("Expense updated.")
        return redirect(url_for("index"))
    return render_template("edit.html", e=expense, categories=CATEGORIES)


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    flash("Expense deleted.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
