def calculate_metrics(record):
    needs = (
        record.housing_rent +
        record.food_dining +
        record.transportation +
        record.utilities
    )
    wants = (
        record.entertainment +
        record.miscellaneous
    )
    total_expenses = needs + wants
    savings = record.monthly_savings
    income = record.monthly_income

    savings_rate = (savings / income) * 100 if income > 0 else 0
    expense_ratio = (total_expenses / income) * 100 if income > 0 else 0
    debt_ratio = (record.total_debt / income) * 100 if income > 0 else 0
    
    needs_ratio = (needs / income) * 100 if income > 0 else 0
    wants_ratio = (wants / income) * 100 if income > 0 else 0

    return {
        "needs": needs,
        "wants": wants,
        "total_expenses": total_expenses,
        "savings": savings,
        "income": income,
        "savings_rate": savings_rate,
        "expense_ratio": expense_ratio,
        "debt_ratio": debt_ratio,
        "needs_ratio": needs_ratio,
        "wants_ratio": wants_ratio
    }

def generate_advice(metrics, record):
    advice = []
    
    # 50-30-20 Rule check
    if metrics["needs_ratio"] > 50:
        advice.append("🚨 Your essential expenses (needs) exceed 50% of your income. Consider reducing housing or transportation costs if possible.")
    else:
        advice.append("✅ Great job keeping your essential expenses under 50% of your income.")

    if metrics["wants_ratio"] > 30:
        advice.append("🚨 You are spending more than 30% of your income on wants. Try to cut back on entertainment and miscellaneous expenses.")
    else:
        advice.append("✅ Your discretionary spending is well within the 30% limit.")

    if metrics["savings_rate"] < 20:
        advice.append("🚨 Your savings rate is below the recommended 20%. Try to allocate more towards your future goals.")
    else:
        advice.append("✅ Excellent! You are saving 20% or more of your income.")

    # Rent specific check request
    rent_ratio = (record.housing_rent / metrics["income"]) * 100 if metrics["income"] > 0 else 0
    if rent_ratio > 30:
        advice.append("⚠️ Your housing costs are over 30% of your income, which could strain your budget.")
    
    # Emergency fund check (assume 6 months of total expenses needed)
    target_emergency_fund = metrics["total_expenses"] * 6
    if record.total_savings < target_emergency_fund:
        shortfall = target_emergency_fund - record.total_savings
        advice.append( f"⚠️ Your current savings (₹{record.total_savings:,.2f}) don't cover a 6-month emergency fund (₹{target_emergency_fund:,.2f}). You need ₹{shortfall:,.2f} more.")
    else:
        advice.append("🛡️ You have a solid emergency fund that covers at least 6 months of expenses.")

    if metrics["debt_ratio"] > 40:
        advice.append("🚨 Your debt-to-income ratio is high. Prioritize paying down high-interest debt immediately.")

    return advice

def calculate_health_score(metrics, record):
    score = 100

    # Penalize based on savings rate
    if metrics["savings_rate"] < 20:
        score -= (20 - metrics["savings_rate"]) * 1.5

    # Penalize based on excessive needs
    if metrics["needs_ratio"] > 50:
        score -= (metrics["needs_ratio"] - 50) * 1.5

    # Penalize based on excessive wants
    if metrics["wants_ratio"] > 30:
        score -= (metrics["wants_ratio"] - 30) * 1.5

    # Penalize based on high debt
    if metrics["debt_ratio"] > 30:
        score -= 20
    elif metrics["debt_ratio"] > 10:
        score -= 10

    # Bonus for good emergency fund
    target_emergency_fund = metrics["total_expenses"] * 6
    if record.total_savings >= target_emergency_fund and target_emergency_fund > 0:
        score += 10

    return max(0, min(100, round(score)))

def analyze_finances(record):
    metrics = calculate_metrics(record)
    advice = generate_advice(metrics, record)
    score = calculate_health_score(metrics, record)

    return {
        "metrics": metrics,
        "advice": advice,
        "score": score
    }
