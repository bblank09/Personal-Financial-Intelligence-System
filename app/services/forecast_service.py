from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.transaction import Transaction
from app.services.investment_service import InvestmentService
from app.mongo.forecast_mongo import ForecastMongo
from app.extensions import db

class ForecastService:

    @staticmethod
    def generate_forecast(user_id):
        forecast_data = {}

        # --------------------------------------------------
        # SECTION 1: Monthly Forecast (Last 3 Months)
        # --------------------------------------------------
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        
        income_query = float(db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            Transaction.is_deleted == False,
            Transaction.date >= three_months_ago
        ).scalar() or 0.0)

        expense_query = float(db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.is_deleted == False,
            Transaction.date >= three_months_ago
        ).scalar() or 0.0)

        # Check if we have transactions representing enough valid data points (for simplicity, relying on amounts > 0)
        has_monthly_data = (income_query > 0) or (expense_query > 0)

        if has_monthly_data:
            next_month_income = income_query / 3.0
            next_month_expense = expense_query / 3.0
            expected_saving = next_month_income - next_month_expense
            
            forecast_data['next_month_income'] = next_month_income
            forecast_data['next_month_expense'] = next_month_expense
            forecast_data['expected_saving'] = expected_saving

        # --------------------------------------------------
        # SECTION 2: Balance Projection
        # --------------------------------------------------
        total_income = float(db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            Transaction.is_deleted == False
        ).scalar() or 0.0)

        total_expense = float(db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.is_deleted == False
        ).scalar() or 0.0)

        current_balance = total_income - total_expense

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        last_30_expense = float(db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.is_deleted == False,
            Transaction.date >= thirty_days_ago
        ).scalar() or 0.0)

        if last_30_expense > 0:
            average_daily_expense = last_30_expense / 30.0
            if average_daily_expense > 0 and current_balance > 0:
                estimated_days = current_balance / average_daily_expense
                forecast_data['estimated_days_remaining'] = int(estimated_days)

        # --------------------------------------------------
        # SECTION 3: Investment Projection
        # --------------------------------------------------
        investment_summary = InvestmentService.get_portfolio_summary(user_id)
        current_portfolio_value = investment_summary.get('portfolio_value', 0.0)
        total_investment_cost = investment_summary.get('total_investment', 0.0)
        total_profit = investment_summary.get('profit', 0.0)

        if total_investment_cost > 0:
            average_return = total_profit / total_investment_cost
            expected_6m = current_portfolio_value * (1 + (average_return * 0.5))
            expected_12m = current_portfolio_value * (1 + average_return)
            
            forecast_data['expected_portfolio_6m'] = expected_6m
            forecast_data['expected_portfolio_12m'] = expected_12m

        # Store to DB (only what's requested by MongoDB requirements)
        if forecast_data:
            ForecastMongo.upsert_forecast(user_id, forecast_data)

        # Attach UI-mandatory display data that isn't stored in Mongo
        if 'estimated_days_remaining' in forecast_data:
            forecast_data['current_balance'] = current_balance
            forecast_data['average_daily_expense'] = average_daily_expense

        if 'expected_portfolio_6m' in forecast_data:
            forecast_data['average_return'] = average_return

        return forecast_data

    @staticmethod
    def get_trend_chart(user_id):
        # Last 3 months actual + next month forecast
        today = datetime.utcnow()
        months_data = []
        income_data = []
        expense_data = []
        
        # Calculate historical for last 3 months
        for i in range(3, 0, -1):
            start_date = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_label = start_date.strftime('%b')
            
            income = float(db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                Transaction.is_deleted == False,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or 0.0)
            
            expense = float(db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.is_deleted == False,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or 0.0)
            
            months_data.append(month_label)
            income_data.append(income)
            expense_data.append(expense)
            
        # Add forecast for next month
        forecast = ForecastService.generate_forecast(user_id)
        next_income = forecast.get('next_month_income', 0.0)
        next_expense = forecast.get('next_month_expense', 0.0)
        
        next_month_label = (today.replace(day=1) + timedelta(days=32)).strftime('%b')
        months_data.append(next_month_label)
        income_data.append(next_income)
        expense_data.append(next_expense)
        
        return {
            "months": months_data,
            "income": income_data,
            "expense": expense_data,
            "forecast_index": 3
        }

    @staticmethod
    def get_balance_chart(user_id):
        forecast = ForecastService.generate_forecast(user_id)
        current_balance = forecast.get('current_balance')
        avg_daily = forecast.get('average_daily_expense')
        days_rem = forecast.get('estimated_days_remaining')
        
        if current_balance is None or avg_daily is None or days_rem is None:
            return {}
            
        days = []
        balances = []
        
        # Plot up to 5 points plus 0
        step = max(1, days_rem // 5)
        
        current_day = 0
        while current_day < days_rem:
            days.append(current_day)
            balances.append(max(0, current_balance - (current_day * avg_daily)))
            current_day += step
            
        if days[-1] != days_rem:
            days.append(days_rem)
            balances.append(0)
            
        return {
            "days": days,
            "balance": balances
        }
        
    @staticmethod
    def get_investment_chart(user_id):
        forecast = ForecastService.generate_forecast(user_id)
        investment_summary = InvestmentService.get_portfolio_summary(user_id)
        current_val = investment_summary.get('portfolio_value')
        six_m = forecast.get('expected_portfolio_6m')
        twelve_m = forecast.get('expected_portfolio_12m')
        
        if current_val is None or six_m is None or twelve_m is None or current_val == 0:
            return {}
            
        return {
            "labels": ["Now", "6 Months", "12 Months"],
            "values": [current_val, six_m, twelve_m]
        }
