from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json

app = Flask(__name__)

# In-memory storage
data_storage = {
    "monthly_expenses": [],
    "debt_tracker": [],
    "expense_trends": [],
    "reminders": [],
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Get user inputs
    monthly_income = float(request.form['income'])
    savings_goal = float(request.form['savings_goal']) if request.form['savings_goal'] else 0
    expense_names = request.form.getlist('expense_names[]')
    expense_amounts = request.form.getlist('expense_amounts[]')
    categories = request.form.getlist('categories[]')

    # Convert expense amounts
    expense_values = [float(amount) for amount in expense_amounts]

    # Categorize and calculate totals
    total_expenses = sum(expense_values)
    essential_expenses = sum(expense_values[i] for i in range(len(categories)) if categories[i] == 'Essential')
    optional_expenses = total_expenses - essential_expenses
    leftover_budget = monthly_income - total_expenses
    remaining_for_savings = leftover_budget

    # Spending advice
    recommendation = (
        "You have enough budget for optional expenses. Enjoy!" 
        if leftover_budget > 0.2 * monthly_income else 
        "Consider reducing optional expenses and prioritizing essentials."
    )

    # Savings advice
    savings_recommendation = (
        "You're on track to meet your savings goal!" 
        if remaining_for_savings >= savings_goal else 
        f"You need to save an additional ${savings_goal - remaining_for_savings:.2f} to reach your goal."
    )

    # Store current month's expenses
    current_month = datetime.now().strftime('%B')
    data_storage["monthly_expenses"].append({
        "month": current_month,
        "total_expenses": total_expenses,
        "essential": essential_expenses,
        "optional": optional_expenses,
    })

    # Calculate forecast and trends
    average_spending = sum([month["total_expenses"] for month in data_storage["monthly_expenses"]]) / len(data_storage["monthly_expenses"])
    forecasted_spending = average_spending + (0.1 * average_spending)

    # Store data for trends
    data_storage["expense_trends"].append({
        "date": datetime.now().strftime('%Y-%m-%d'),
        "total": total_expenses,
    })

    # Debt repayment and reminders
    debts = [{"name": debt["name"], "amount": debt["amount"], "paid": debt["paid"]} for debt in data_storage["debt_tracker"]]
    reminders = [{"title": reminder["title"], "due_date": reminder["due_date"]} for reminder in data_storage["reminders"]]

    results = {
        "total_expenses": total_expenses,
        "essential_expenses": essential_expenses,
        "optional_expenses": optional_expenses,
        "leftover_budget": leftover_budget,
        "savings_goal": savings_goal,
        "recommendation": recommendation,
        "savings_recommendation": savings_recommendation,
        "forecasted_spending": forecasted_spending,
        "expense_trends": data_storage["expense_trends"],
        "debts": debts,
        "reminders": reminders,
    }

    return render_template('results.html', results=results)

@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    title = request.form['title']
    due_date = request.form['due_date']
    data_storage["reminders"].append({"title": title, "due_date": due_date})
    return redirect(url_for('index'))

@app.route('/add_debt', methods=['POST'])
def add_debt():
    name = request.form['name']
    amount = float(request.form['amount'])
    data_storage["debt_tracker"].append({"name": name, "amount": amount, "paid": False})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)




