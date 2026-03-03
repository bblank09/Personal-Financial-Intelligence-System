import pytest
from app import create_app
from app.extensions import db
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MONGO_URI = 'mongodb://mongo:27017/test_finance_db'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

import unittest.mock as mock

@pytest.fixture(autouse=True)
def mock_mongo():
    import app.mongo.investment_summary_mongo
    import app.mongo.financial_summary
    import app.mongo.forecast_mongo
    with mock.patch("app.mongo.investment_summary_mongo.InvestmentSummaryMongo") as mock_invest, \
         mock.patch("app.mongo.forecast_mongo.ForecastMongo") as mock_forecast, \
         mock.patch("app.mongo.financial_summary.FinancialSummaryMongo") as mock_fin:
        
        mock_invest.get_historical_summaries.return_value = []
        yield

@pytest.fixture(autouse=True)
def mock_yfinance():
    with mock.patch("yfinance.Ticker") as MockTicker, \
         mock.patch("yfinance.Search") as MockSearch:
        
        # Mock Search
        mock_search_instance = mock.MagicMock()
        mock_search_instance.quotes = [
            {"symbol": "AAPL", "shortname": "Apple Inc.", "quoteType": "EQUITY", "exchDisp": "NASDAQ"}
        ]
        MockSearch.return_value = mock_search_instance
        
        # Mock Ticker
        import pandas as pd
        mock_ticker_instance = mock.MagicMock()
        df = pd.DataFrame({"Close": [150.0]})
        mock_ticker_instance.history.return_value = df
        MockTicker.return_value = mock_ticker_instance
        
        yield
