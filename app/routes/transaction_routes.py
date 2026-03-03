from flask import Blueprint, request, jsonify, session, render_template
from app.services.financial_service import FinancialService
from app.services.analytics_service import AnalyticsService
from app.routes.auth_routes import login_required
from app.extensions import db
from app.models.transaction import Transaction
from datetime import datetime

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/transactions', methods=['GET'])
@login_required
def transactions_page():
    return render_template('transactions.html')

@transaction_bp.route('/api/transactions', methods=['POST'])
@login_required
def create_transaction():
    data = request.json
    user_id = session.get('user_id')
    
    tx = FinancialService.add_transaction(
        user_id=user_id,
        amount=data.get('amount'),
        tx_type=data.get('type'),
        category=data.get('category'),
        date=data.get('date'),
        note=data.get('note')
    )
    
    # Trigger Mongo Update
    if getattr(tx, 'date', None):
        month_str = tx.date if isinstance(tx.date, str) else tx.date.strftime('%Y-%m')
        AnalyticsService.generate_monthly_summary(user_id, month_str[:7])

    return jsonify({"message": "Transaction added", "transaction": tx.to_dict()}), 201

@transaction_bp.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    user_id = session.get('user_id')
    month_filter = request.args.get('month') # Optional filter 'YYYY-MM'
    category_filter = request.args.get('category')
    type_filter = request.args.get('type')
    
    transactions = FinancialService.get_transactions(
        user_id, 
        month=month_filter, 
        category=category_filter, 
        tx_type=type_filter
    )
    
    return jsonify({"transactions": [tx.to_dict() for tx in transactions]}), 200

@transaction_bp.route('/api/transactions/<int:tx_id>', methods=['PUT'])
@login_required
def update_transaction(tx_id):
    user_id = session.get('user_id')
    data = request.json
    
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id, is_deleted=False).first()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404
        
    for key, value in data.items():
        if hasattr(tx, key) and key not in ['id', 'user_id', 'created_at']:
            if key == 'date' and isinstance(value, str):
                # parse string to date object
                setattr(tx, key, datetime.strptime(value, '%Y-%m-%d').date())
            else:
                setattr(tx, key, value)
            
    db.session.commit()
    
    # Trigger Mongo Update
    month_str = tx.date.strftime('%Y-%m')
    AnalyticsService.generate_monthly_summary(user_id, month_str)
    
    return jsonify({"message": "Transaction updated", "transaction": tx.to_dict()}), 200

@transaction_bp.route('/api/transactions/<int:tx_id>', methods=['DELETE'])
@login_required
def delete_transaction(tx_id):
    user_id = session.get('user_id')
    
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id, is_deleted=False).first()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404
        
    # Soft delete
    tx.is_deleted = True
    db.session.commit()
    
    # Trigger Mongo Update
    month_str = tx.date.strftime('%Y-%m')
    AnalyticsService.generate_monthly_summary(user_id, month_str)
    
    return jsonify({"message": "Transaction deleted successfully"}), 200
