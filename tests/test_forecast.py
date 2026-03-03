import pytest
import json
from unittest.mock import MagicMock
from app import create_app
from app.extensions import db
from app.models.user import User

@pytest.fixture
def client(app, mock_mongo):
    return app.test_client()

def test_get_forecast_empty(client):
    # Tests that when there is no data, the API handles it without crashing and returns empty structure
    client.post('/api/register', data=json.dumps({"username": "fcastuser", "email": "fc1@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "fc1@example.com", "password": "pwd"}), content_type='application/json')
    
    res = client.get('/api/forecast')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data == {} # Empty structure since there's no data

def test_get_forecast_populated_monthly_balance(client):
    client.post('/api/register', data=json.dumps({"username": "fcastuser2", "email": "fc2@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "fc2@example.com", "password": "pwd"}), content_type='application/json')
    
    # 1. Add Income and Expense
    from datetime import datetime, timedelta
    d1 = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    d2 = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    client.post('/api/transactions', data=json.dumps({"type": "income", "amount": 3000.0, "category": "Salary", "date": d1, "description": ""}), content_type='application/json')
    client.post('/api/transactions', data=json.dumps({"type": "expense", "amount": 1500.0, "category": "Rent", "date": d2, "description": ""}), content_type='application/json')
    
    res = client.get('/api/forecast')
    assert res.status_code == 200
    data = json.loads(res.data)
    
    # Monthly Forecast Check (Averages over 3 months -> so 3000/3 = 1000)
    assert data['next_month_income'] == 1000.0
    assert data['next_month_expense'] == 500.0
    assert data['expected_saving'] == 500.0
    
    # Balance Projection Check
    # Current balance: 3000 - 1500 = 1500
    # Average daily expense (last 30 days): 1500 / 30 = 50.0
    # Days remaining: 1500 / 50.0 = 30
    assert data['current_balance'] == 1500.0
    assert data['average_daily_expense'] == 50.0
    assert data['estimated_days_remaining'] == 30

def test_get_forecast_populated_investments(client, monkeypatch):
    client.post('/api/register', data=json.dumps({"username": "fcastuser3", "email": "fc3@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "fc3@example.com", "password": "pwd"}), content_type='application/json')
    
    # Mock Investment Summary return so we don't need real investments inserted via YFinance
    class MockService:
        @staticmethod
        def get_portfolio_summary(user_id):
            return {
                "portfolio_value": 11000.0,  # Current Portfolio Value
                "total_investment": 10000.0, # Total Invested
                "profit": 1000.0             # Profit
            }
            
    import app.services.forecast_service
    monkeypatch.setattr(app.services.forecast_service.InvestmentService, "get_portfolio_summary", MockService.get_portfolio_summary)
    
    res = client.get('/api/forecast')
    assert res.status_code == 200
    data = json.loads(res.data)
    
    # Investment check
    # Average Return = 1000 / 10000 = 0.1
    # 6M = 11000 * (1 + (0.1 * 0.5)) = 11550.0
    # 12M = 11000 * (1 + 0.1) = 12100.0
    
    assert data['expected_portfolio_6m'] == pytest.approx(11550.0)
    assert data['expected_portfolio_12m'] == pytest.approx(12100.0)
    assert data['average_return'] == pytest.approx(0.1)
