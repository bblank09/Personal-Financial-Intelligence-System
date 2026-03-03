import pytest
from app.services.analytics_service import AnalyticsService

def test_health_score_excellent():
    # saving > 0.4
    score, risk = AnalyticsService.calculate_health_score(0.45)
    assert score == 95
    assert risk == "Low"

def test_health_score_poor():
    # saving > 0.1
    score, risk = AnalyticsService.calculate_health_score(0.15)
    assert score == 60
    assert risk == "Medium"
