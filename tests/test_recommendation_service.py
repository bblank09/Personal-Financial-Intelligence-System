from app.services.recommendation_service import RecommendationService


def test_recommendation_negative_saving():
    recs = RecommendationService.generate_recommendations(-0.1, 1000, 1100)
    assert any("Critical" in r for r in recs)


def test_recommendation_low_saving():
    recs = RecommendationService.generate_recommendations(0.05, 1000, 950)
    assert any("Warning" in r for r in recs)


def test_recommendation_moderate_saving():
    recs = RecommendationService.generate_recommendations(0.15, 1000, 850)
    assert any("On Track" in r for r in recs)


def test_recommendation_excellent_saving():
    recs = RecommendationService.generate_recommendations(0.3, 1000, 700)
    assert any("Excellent" in r for r in recs)


def test_recommendation_no_income():
    recs = RecommendationService.generate_recommendations(0, 0, 500)
    assert any("expenses but no income" in r for r in recs)
