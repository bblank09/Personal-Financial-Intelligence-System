import pytest
import json
from app.services.analytics_service import AnalyticsService


def test_health_score_excellent():
    # saving > 0.4
    score, risk = AnalyticsService.calculate_health_score(0.45)
    assert score == 95
    assert risk == "Low"


def test_health_score_good():
    # saving > 0.2
    score, risk = AnalyticsService.calculate_health_score(0.25)
    assert score == 80
    assert risk == "Low"


def test_health_score_poor():
    # saving > 0.1
    score, risk = AnalyticsService.calculate_health_score(0.15)
    assert score == 60
    assert risk == "Medium"


def test_health_score_critical():
    # saving <= 0
    score, risk = AnalyticsService.calculate_health_score(-0.1)
    assert score <= 50
    assert risk == "High"


def test_get_analytics_api(client):
    client.post('/api/register', data=json.dumps({"username": "analyticsuser", "email": "analytics@example.com", "password": "pwd"}), content_type='application/json')
    login_res = client.post('/api/login', data=json.dumps({"email": "analytics@example.com", "password": "pwd"}), content_type='application/json')
    user_id = json.loads(login_res.data)['user_id']

    response = client.get('/api/analytics/me')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_income' in data
    assert 'total_expense' in data
    assert 'financial_score' in data


def test_get_analytics_unauthorized(client):
    # Register and login as user A
    client.post('/api/register', data=json.dumps({"username": "userA", "email": "a@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "a@example.com", "password": "pwd"}), content_type='application/json')

    # Try to access user 99999's analytics
    response = client.get('/api/analytics/99999')
    assert response.status_code == 403
    assert b"Unauthorized" in response.data
