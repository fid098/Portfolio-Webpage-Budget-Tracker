from flask import Flask, render_template, flash, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime, timedelta
import io 
import base64
import matplotlib.pyplot as plt



def get_db():
    conn = sqlite3.connect("users_information.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/experiences")
def experiences():
    return render_template("experiences.html")

@app.route("/budget", methods=["GET", "POST"])
def budget():
    if "user_id" not in session:
        flash("Please log in to access this page.", "warning")
        return redirect("/login")
    
    conn = get_db()
    user_id = session["user_id"]

    budget = conn.execute("""
        SELECT cash, rent, savings, investments, miscellaneous
        FROM budget
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if budget is None:
        conn.execute("INSERT INTO budget (user_id) VALUES (?)", (user_id,))
        conn.commit()
        budget = conn.execute("""
            SELECT cash, rent, savings, investments, miscellaneous
            FROM budget
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    totals = conn.execute("""
        SELECT 
            SUM(CASE WHEN transaction_type='Income' THEN amount ELSE 0 END) AS total_income,
            SUM(CASE WHEN transaction_type='Expense' THEN amount ELSE 0 END) AS total_expense
        FROM transactions
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    total_income = totals["total_income"] or 0
    total_expense = totals["total_expense"] or 0
    current_balance = total_income - total_expense

    if request.method == "POST":
        cash = float(request.form.get("cash", 0))
        rent = float(request.form.get("rent", 0))
        savings = float(request.form.get("savings", 0))
        investments = float(request.form.get("investments", 0))
        miscellaneous = float(request.form.get("miscellaneous", 0))

        budget_total = cash + rent + savings + investments + miscellaneous

        if budget_total > current_balance:
            flash("Total budget exceeds current balance. Adjust amounts.", "danger")
        else:
            conn.execute("""
                UPDATE budget
                SET cash = ?, rent = ?, savings = ?, investments = ?, miscellaneous = ?
                WHERE user_id = ?
            """, (cash, rent, savings, investments, miscellaneous, user_id))
            conn.commit()
            flash("Budget updated successfully!", "success")


    budget = conn.execute("""
        SELECT cash, rent, savings, investments, miscellaneous
        FROM budget
        WHERE user_id = ?
    """, (user_id,)).fetchone()

 
    budget_total = sum([budget["cash"], budget["rent"], budget["savings"], budget["investments"], budget["miscellaneous"]])
    balance_left_to_budget = current_balance - budget_total

    def get_transactions_since(days):
        since_date = (datetime.now() - timedelta(days=days)).date()
        return conn.execute("""
            SELECT t.description, t.amount, t.transaction_type, t.date, c.name AS category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.categories_id
            WHERE t.user_id = ? AND t.date >= ?
            ORDER BY t.date DESC, t.transaction_id DESC
        """, (user_id, since_date)).fetchall()

    recent_transactions = {
        "last_week": get_transactions_since(7),
        "last_month": get_transactions_since(30),
        "last_6_months": get_transactions_since(180),
        "last_year": get_transactions_since(365)
    }

    conn.close()
    
    return render_template(
        "budget.html",
        budget=budget,
        total_income=totals["total_income"] or 0,
        total_expense=totals["total_expense"] or 0,
        current_balance=current_balance,
        balance_left_to_budget=balance_left_to_budget,
        recent_transactions=recent_transactions
    )

@app.route("/transaction", methods=["GET", "POST"])
def transaction():
    if "user_id" not in session:
        flash("Please log in to access this page.", "warning")
        return redirect("/login")
    
    conn = get_db()
    user_id = session["user_id"]

    if request.method == "POST":
        description = request.form.get("description")
        amount = float(request.form.get("amount", 0))
        category_name = request.form.get("category")
        t_type = request.form.get("type")
        date = request.form.get("date")
        budget_category = request.form.get("budget_category").lower()

        if not all([description, amount, category_name, t_type, date]):
            flash("All fields are required.", "danger")
            conn.close()
            return redirect("/transaction")

        category = conn.execute("""
            SELECT categories_id 
            FROM categories 
            WHERE name = ? AND (user_created = 0 OR user_created = 1)
        """, (category_name,)).fetchone()

        if category is None:
            flash("Invalid category.", "danger")
            conn.close()
            return redirect("/transaction")
        
        category_id = category["categories_id"]

        if t_type == "Expense" and budget_category in ["cash", "rent", "savings", "investments", "miscellaneous"]:
            current_amount = conn.execute(f"SELECT {budget_category} FROM budget WHERE user_id = ?", (user_id,)).fetchone()[0] or 0
            if amount > current_amount:
                flash(f"Not enough funds in {budget_category} to cover this expense.", "danger")
                conn.close()
                return redirect("/transaction")
    
            conn.execute(f"UPDATE budget SET {budget_category} = ? WHERE user_id = ?", (current_amount - amount, user_id))

# Insert the transaction
        conn.execute("""
            INSERT INTO transactions (user_id, category_id, amount, transaction_type, description, date, budget_category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, category_id, amount, t_type, description, date, budget_category))
        conn.commit()
        flash("Transaction added successfully!", "success")


    transactions = conn.execute("""
        SELECT t.description, t.amount, t.transaction_type, t.date, c.name AS category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.categories_id
        WHERE t.user_id = ?
        ORDER BY t.date DESC, t.transaction_id DESC
    """, (user_id,)).fetchall()

    totals = conn.execute("""
        SELECT 
            SUM(CASE WHEN transaction_type='Income' THEN amount ELSE 0 END) AS total_income,
            SUM(CASE WHEN transaction_type='Expense' THEN amount ELSE 0 END) AS total_expense,
            SUM(CASE WHEN transaction_type='Income' THEN amount ELSE -amount END) AS net_balance
        FROM transactions
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    budget = conn.execute("""
        SELECT cash, rent, savings, investments, miscellaneous
        FROM budget
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    current_balance = totals["net_balance"] or 0
    budget_total = sum([budget["cash"], budget["rent"], budget["savings"], budget["investments"], budget["miscellaneous"]])
    balance_left_to_budget = current_balance - budget_total

    conn.close()

    return render_template(
    "transaction.html",
    transactions=transactions,
    total_income=totals["total_income"] or 0,
    total_expense=totals["total_expense"] or 0,
    net_balance=totals["net_balance"] or 0,
    budget=budget,
    balance_left_to_budget=balance_left_to_budget
)
   
    
@app.route("/summary")
def summary():
    if "user_id" not in session:
        flash("Please log in to access this page.", "warning")
        return redirect("/login")
    
    conn = get_db()
    user_id = session["user_id"]

    income_pie = conn.execute("""
    SELECT c.name AS category_name, SUM(t.amount) AS total 
    FROM transactions t
    JOIN categories c ON t.category_id = c.categories_id
    WHERE t.user_id = ? AND t.transaction_type = 'Income'
    GROUP BY c.name
    """, (user_id,)).fetchall()

    expense_pie = conn.execute("""
    SELECT c.name AS category_name, SUM(t.amount) AS total  
    FROM transactions t
    JOIN categories c ON t.category_id = c.categories_id
    WHERE t.user_id = ? AND t.transaction_type = 'Expense'
    GROUP BY c.name
    """, (user_id,)).fetchall()

    budget = conn.execute(""" SELECT cash, savings, rent, investments, miscellaneous FROM budget WHERE user_id = ?""", (user_id,)).fetchone()
    conn.close()

    def make_pies(labels, values):
        if not values or sum(values) == 0:
            return None
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)
        return img_base64
    

    income_chart = make_pies([row["category_name"] for row in income_pie], [row["total"] for row in income_pie])
    expense_chart = make_pies([row["category_name"] for row in expense_pie], [row["total"] for row in expense_pie])
    budget_chart = make_pies(["Cash", "Savings", "Rent", "Investments", "Miscellaneous"], [budget["cash"], budget["savings"], budget["rent"], budget["investments"], budget["miscellaneous"]])


    return render_template(
        "summary.html",
        income_chart=income_chart,
        expense_chart=expense_chart,
        budget_chart=budget_chart
    )
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username", "danger")
            return redirect("/login")
        elif not password:
            flash("Must provide password", "danger")
            return redirect("/login")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username and/or password", "danger")
            return redirect("/login")

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        flash("Logged in successfully!", "success")
        return redirect("/budget")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect("/")

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        name = request.form.get("name")

        if not username:
            flash("Must provide username", "danger")
            return redirect("/create_account")
        elif not password:
            flash("Must provide password", "danger")
            return redirect("/create_account")
        elif not confirmation:
            flash("Must provide password confirmation", "danger")
            return redirect("/create_account")
        elif password != confirmation:
            flash("Passwords do not match", "danger")
            return redirect("/create_account")
        elif not name:
            flash("Must provide name", "danger")
            return redirect("/create_account")

        hash_pw = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (name, username, hash) VALUES (?, ?, ?)", (name, username, hash_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already taken", "danger")
            return redirect("/create_account")
        finally:
            conn.close()

        flash("Account created successfully! Please log in.", "success")
        return redirect("/login")
    
    return render_template("create_account.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
