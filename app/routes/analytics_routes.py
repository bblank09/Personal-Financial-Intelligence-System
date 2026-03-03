from flask import Blueprint, jsonify, session, render_template, request
from app.services.analytics_service import AnalyticsService
from app.routes.auth_routes import login_required
from app.utils.date_helpers import get_current_month_string

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/', methods=['GET'])
@login_required
def dashboard_page():
    return render_template('dashboard.html')

@analytics_bp.route('/analytics', methods=['GET'])
@login_required
def analytics_page():
    return render_template('analytics.html')

@analytics_bp.route('/api/analytics/<user_id>', methods=['GET'])
@login_required
def get_analytics(user_id):
    # Special mapping for 'me' to infer user from session
    if user_id == 'me':
        user_id = session.get('user_id')
        
    # Verify user is accessing their own analytics
    if str(session.get('user_id')) != str(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    # Accepts a month parameter; defaults to current month
    target_month = request.args.get('month') or get_current_month_string()
    
    # Generate (and upsert) the summary for the given month
    summary = AnalyticsService.generate_monthly_summary(user_id, target_month)
    
    return jsonify(summary), 200
