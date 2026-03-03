from flask import Blueprint, request, jsonify, session, render_template
from app.services.investment_service import InvestmentService
from app.services.analytics_service import AnalyticsService
from app.routes.auth_routes import login_required
from datetime import datetime

investment_bp = Blueprint('investment_bp', __name__)

@investment_bp.route('/investments', methods=['GET'])
@login_required
def investments_page():
    return render_template('investments.html')

@investment_bp.route('/api/investments', methods=['POST'])
@login_required
def create_investment():
    data = request.json
    user_id = session.get('user_id')
    
    purchase_date_str = data.get('purchase_date')
    if purchase_date_str:
        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
    else:
        purchase_date = datetime.utcnow().date()
        
    quantity = data.get('quantity')
    if quantity is not None:
        quantity = float(quantity)
        
    price = data.get('price')
    if price is not None:
        price = float(price)

    inv = InvestmentService.add_investment(
        user_id=user_id,
        symbol=data.get('symbol'),
        asset_name=data.get('asset_name'),
        quantity=quantity,
        price=price,
        purchase_date=purchase_date
    )
    
    # Trigger analytics sumupdate
    AnalyticsService.generate_monthly_summary(user_id, datetime.utcnow().strftime('%Y-%m'))
    
    return jsonify({"message": "Investment transaction added", "investment": inv.to_dict()}), 201

@investment_bp.route('/api/investments', methods=['GET'])
@login_required
def get_investments():
    user_id = session.get('user_id')
    investments = InvestmentService.get_investments(user_id)
    return jsonify({"transactions": [inv.to_dict() for inv in investments]}), 200

@investment_bp.route('/api/investments/summary', methods=['GET'])
@login_required
def get_investment_summary():
    user_id = session.get('user_id')
    summary = InvestmentService.get_portfolio_summary(user_id)
    
    # Fetch historical data for charts
    from app.mongo.investment_summary_mongo import InvestmentSummaryMongo
    historical = InvestmentSummaryMongo.get_historical_summaries(user_id)
    summary['historical'] = historical
    
    return jsonify(summary), 200

@investment_bp.route('/api/investments/<int:inv_id>', methods=['PUT'])
@login_required
def update_investment(inv_id):
    user_id = session.get('user_id')
    data = request.json
    
    if 'purchase_date' in data and isinstance(data['purchase_date'], str):
        data['purchase_date'] = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        
    if 'price' in data and data['price'] is not None:
        data['price'] = float(data['price'])
    if 'quantity' in data and data['quantity'] is not None:
        data['quantity'] = float(data['quantity'])
        
    inv = InvestmentService.update_investment(user_id, inv_id, data)
    
    if not inv:
        return jsonify({"error": "Investment not found"}), 404
        
    AnalyticsService.generate_monthly_summary(user_id, datetime.utcnow().strftime('%Y-%m'))
    return jsonify({"message": "Investment updated", "investment": inv.to_dict()}), 200

@investment_bp.route('/api/investments/<int:inv_id>', methods=['DELETE'])
@login_required
def delete_investment(inv_id):
    user_id = session.get('user_id')
    success = InvestmentService.delete_investment(user_id, inv_id)
    
    if not success:
        return jsonify({"error": "Investment not found"}), 404
        
    AnalyticsService.generate_monthly_summary(user_id, datetime.utcnow().strftime('%Y-%m'))
    return jsonify({"message": "Investment deleted successfully"}), 200

@investment_bp.route('/api/assets/search', methods=['GET'])
@login_required
def search_assets():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
        
    try:
        import yfinance as yf
        results = yf.Search(query, max_results=8).quotes
        
        assets = []
        for r in results:
            if 'symbol' in r and 'shortname' in r:
                # User specifically requested "Current price" in search results
                # Let's conditionally add it
                current_price = None
                
                assets.append({
                    "symbol": r['symbol'],
                    "name": r['shortname'],
                    "type": r.get('quoteType', 'Other'),
                    "exchange": r.get('exchDisp', '')
                    # Note: We don't fetch price here automatically for all 8 results because 
                    # querying 8 tickers in a debounce can be slow and hit rate limits.
                    # Price is fetched via the explicit /api/assets/price route below.
                })
        return jsonify(assets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@investment_bp.route('/api/assets/price', methods=['GET'])
@login_required
def get_asset_price():
    ticker = request.args.get('ticker')
    date_str = request.args.get('date') # Format YYYY-MM-DD
    
    if not ticker:
        return jsonify({"error": "Ticker required"}), 400
        
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        
        # 1. Fetch current price
        current_hist = t.history(period="1d")
        current_price = None
        if not current_hist.empty:
            current_price = float(current_hist['Close'].iloc[-1])
            
        # 2. Fetch historical price if date is provided
        historical_price = None
        if date_str:
            # Add one day to be safe with timezone issues and ensure we get a quote
            from datetime import timedelta
            start_dt = datetime.strptime(date_str, '%Y-%m-%d')
            end_dt = start_dt + timedelta(days=3) # Window of 3 days to catch weekends/holidays
            
            hist = t.history(start=start_dt.strftime('%Y-%m-%d'), end=end_dt.strftime('%Y-%m-%d'))
            if not hist.empty:
                historical_price = float(hist['Close'].iloc[0])
                
        return jsonify({
            "ticker": ticker,
            "current_price": current_price,
            "historical_price": historical_price
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
