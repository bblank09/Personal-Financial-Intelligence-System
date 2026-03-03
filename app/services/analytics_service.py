from app.services.financial_service import FinancialService
from app.services.recommendation_service import RecommendationService
from app.mongo.financial_summary import FinancialSummaryMongo
from app.models.transaction import Transaction
from app.services.investment_service import InvestmentService
from sqlalchemy import func

class AnalyticsService:

    @staticmethod
    def calculate_health_score(saving_rate):
        # Score calculation based on savings ratio
        # Example: >0.4 Excellent (90-100)
        # >0.2 Good (70-89)
        # >0.1 Poor (50-69)
        # <=0 Critical (<50)
        
        if saving_rate > 0.4:
            score = 95
            risk = "Low"
        elif saving_rate > 0.2:
            score = 80
            risk = "Low"
        elif saving_rate > 0.1:
            score = 60
            risk = "Medium"
        elif saving_rate > 0:
             score = 40
             risk = "High"
        else:
            # negative saving rate limit to 0 logically or small number
            score = max(0, int(50 + (saving_rate * 100))) 
            if score > 50: score = 50 # Cap it
            risk = "High"

        return score, risk

    @staticmethod
    def get_top_expense_category(user_id, month=None):
        query = Transaction.query.with_entities(
            Transaction.category, func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.is_deleted == False
        )
        if month:
             year_str, month_str = month.split('-')
             query = query.filter(
                 func.extract('year', Transaction.date) == int(year_str),
                 func.extract('month', Transaction.date) == int(month_str)
             )
             
        result = query.group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).first()
        
        return result.category if result else "None"

    @staticmethod
    def generate_monthly_summary(user_id, month):
        income = FinancialService.calculate_total_income(user_id, month)
        expense = FinancialService.calculate_total_expense(user_id, month)
        saving_rate = FinancialService.calculate_saving_rate(user_id, month)

        score, risk = AnalyticsService.calculate_health_score(saving_rate)
        top_category = AnalyticsService.get_top_expense_category(user_id, month)
        recommendations = RecommendationService.generate_recommendations(saving_rate, income, expense)
        
        expense_breakdown = FinancialService.get_expense_breakdown(user_id, month)
        cashflow_trend = FinancialService.get_cashflow_trend(user_id, month=month, months_back=6)
        investment_totals = InvestmentService.calculate_totals(user_id)

        summary_data = {
            "total_income": income,
            "total_expense": expense,
            "saving_rate": saving_rate,
            "financial_score": score,
            "risk_level": risk,
            "top_category": top_category,
            "recommendations": recommendations,
            "expense_breakdown": expense_breakdown,
            "cashflow_trend": cashflow_trend,
            "total_investment": investment_totals["total_investment"],
            "portfolio_value": investment_totals["portfolio_value"],
            "profit": investment_totals["profit"],
            "return_percent": investment_totals["return_percent"]
        }
        
        # Store in MongoDB
        AnalyticsService.store_summary_mongo(user_id, month, summary_data)
        
        # Also store the specific isolated investment summary in the requested collection
        from app.mongo.investment_summary_mongo import InvestmentSummaryMongo
        invalid_keys = ['total_income', 'total_expense', 'saving_rate', 'financial_score', 'risk_level', 'top_category', 'recommendations', 'expense_breakdown', 'cashflow_trend']
        inv_data = {k: v for k, v in summary_data.items() if k not in invalid_keys}
        InvestmentSummaryMongo.upsert_summary(user_id, month, inv_data)

        return summary_data

    @staticmethod
    def store_summary_mongo(user_id, month, data):
        FinancialSummaryMongo.upsert_summary(user_id, month, data)
