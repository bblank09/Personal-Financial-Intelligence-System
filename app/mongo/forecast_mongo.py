from app.mongo.mongo_client import get_collection
from datetime import datetime

class ForecastMongo:
    COLLECTION_NAME = 'forecast_data'

    @classmethod
    def upsert_forecast(cls, user_id, data):
        collection = get_collection(cls.COLLECTION_NAME)
        
        document = {
            "user_id": user_id,
            "next_month_income": data.get("next_month_income"),
            "next_month_expense": data.get("next_month_expense"),
            "expected_saving": data.get("expected_saving"),
            "estimated_days_remaining": data.get("estimated_days_remaining"),
            "expected_portfolio_6m": data.get("expected_portfolio_6m"),
            "expected_portfolio_12m": data.get("expected_portfolio_12m"),
            "updated_at": datetime.utcnow()
        }
        
        # Remove None values so we only update valid fields, and only return valid fields from DB
        clean_doc = {k: v for k, v in document.items() if v is not None}
        
        collection.update_one(
            {"user_id": user_id},
            {"$set": clean_doc},
            upsert=True
        )

    @classmethod
    def get_forecast(cls, user_id):
        collection = get_collection(cls.COLLECTION_NAME)
        return collection.find_one({"user_id": user_id}, {"_id": 0})
