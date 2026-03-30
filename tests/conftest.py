import pytest
from app import create_app
from app.extensions import db
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MONGO_URI = 'mongodb://mongo:27017/test_finance_db'
#1
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
    # Mock get_collection in every module that imports it
    mock_collection = mock.MagicMock()
    mock_collection.find_one.return_value = None
    mock_collection.update_one.return_value = None
    mock_collection.insert_one.return_value = None

    # Create a chainable cursor mock for .find().sort().limit()
    mock_cursor = mock.MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.__iter__ = mock.Mock(return_value=iter([]))
    mock_collection.find.return_value = mock_cursor

    with mock.patch("app.mongo.financial_summary.get_collection", return_value=mock_collection), \
         mock.patch("app.mongo.investment_summary_mongo.get_collection", return_value=mock_collection), \
         mock.patch("app.mongo.forecast_mongo.get_collection", return_value=mock_collection):
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
