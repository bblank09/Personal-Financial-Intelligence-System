from app.mongo.mongo_client import get_collection
from datetime import datetime

class InvestmentSummaryMongo:
    collection_name = 'investment_summary'

    @staticmethod
    def get_collection():
        return get_collection(InvestmentSummaryMongo.collection_name)

    @staticmethod
    def upsert_summary(user_id, month, data):
        """
        Stores or updates an investment summary for a specific user and month.
        Data should contain: total_investment, portfolio_value, profit, allocation
        """
        collection = InvestmentSummaryMongo.get_collection()
        
        # Prepare the document structure
        document = {
            "user_id": user_id,
            "month": month,
            "total_investment": data.get("total_investment", 0.0),
            "portfolio_value": data.get("portfolio_value", 0.0),
            "profit": data.get("profit", 0.0),
            "allocation": data.get("allocation", {}),
            "updated_at": datetime.utcnow()
        }

        # Update if exists, otherwise insert (upsert)
        collection.update_one(
            {"user_id": user_id, "month": month},
            {"$set": document},
            upsert=True
        )

    @staticmethod
    def get_summary(user_id, month):
        collection = InvestmentSummaryMongo.get_collection()
        return collection.find_one({"user_id": user_id, "month": month}, {'_id': 0})
        
    @staticmethod
    def get_historical_summaries(user_id, months_back=6):
        """
        Fetches historical investment summaries to build the Monthly Performance Chart.
        Returns a timeline sorted chronologically.
        """
        collection = InvestmentSummaryMongo.get_collection()
        all_summaries = list(collection.find(
            {"user_id": user_id},
            {'_id': 0}
        ).sort("month", -1).limit(months_back))
        
        # Reverse to get chronological order
        return sorted(all_summaries, key=lambda x: x['month'])
