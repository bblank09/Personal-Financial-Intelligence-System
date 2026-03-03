from app.mongo.mongo_client import get_collection
from datetime import datetime

class FinancialSummaryMongo:
    COLLECTION_NAME = 'financial_summaries'

    @classmethod
    def upsert_summary(cls, user_id, month, data):
        collection = get_collection(cls.COLLECTION_NAME)
        
        document = {
            "user_id": user_id,
            "month": month,
            "total_income": data.get("total_income", 0.0),
            "total_expense": data.get("total_expense", 0.0),
            "saving_rate": data.get("saving_rate", 0.0),
            "financial_score": data.get("financial_score", 0),
            "risk_level": data.get("risk_level", "Medium"),
            "top_category": data.get("top_category", ""),
            "recommendations": data.get("recommendations", []),
            "expense_breakdown": data.get("expense_breakdown", []),
            "cashflow_trend": data.get("cashflow_trend", []),
            "total_investment": data.get("total_investment", 0.0),
            "portfolio_value": data.get("portfolio_value", 0.0),
            "profit": data.get("profit", 0.0),
            "return_percent": data.get("return_percent", 0.0),
            "updated_at": datetime.utcnow(),
            "deleted": False
        }

        # The requirements ask for created_at, but since it's an upsert updated_at make sense. 
        # Add created_at if it's a new insert
        
        existing = collection.find_one({"user_id": user_id, "month": month})
        if not existing:
             document["created_at"] = datetime.utcnow()
        
        collection.update_one(
            {"user_id": user_id, "month": month},
            {"$set": document},
            upsert=True
        )

    @classmethod
    def get_summary_by_user(cls, user_id):
        collection = get_collection(cls.COLLECTION_NAME)
        return list(collection.find({"user_id": user_id, "deleted": False}, {"_id": 0}))

    @classmethod
    def get_summary_by_month(cls, user_id, month):
        collection = get_collection(cls.COLLECTION_NAME)
        return collection.find_one({"user_id": user_id, "month": month, "deleted": False}, {"_id": 0})
