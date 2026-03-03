from flask import Blueprint, jsonify, session
from app.services.forecast_service import ForecastService
from app.routes.auth_routes import login_required

forecast_bp = Blueprint('forecast_bp', __name__)

@forecast_bp.route('/api/forecast', methods=['GET'])
@login_required
def get_forecast():
    user_id = session.get('user_id')
    forecast_data = ForecastService.generate_forecast(user_id)
    return jsonify(forecast_data), 200

@forecast_bp.route('/api/forecast/trend', methods=['GET'])
@login_required
def get_forecast_trend():
    user_id = session.get('user_id')
    trend_data = ForecastService.get_trend_chart(user_id)
    return jsonify(trend_data), 200

@forecast_bp.route('/api/forecast/balance', methods=['GET'])
@login_required
def get_forecast_balance():
    user_id = session.get('user_id')
    balance_data = ForecastService.get_balance_chart(user_id)
    return jsonify(balance_data), 200

@forecast_bp.route('/api/forecast/investment', methods=['GET'])
@login_required
def get_forecast_investment():
    user_id = session.get('user_id')
    investment_data = ForecastService.get_investment_chart(user_id)
    return jsonify(investment_data), 200
