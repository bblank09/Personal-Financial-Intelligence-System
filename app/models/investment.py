from app.extensions import db
from datetime import datetime

class Investment(db.Model):
    __tablename__ = 'investment_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    asset_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'asset_name': self.asset_name,
            'quantity': self.quantity,
            'price': self.price,
            'purchase_date': self.purchase_date.strftime('%Y-%m-%d') if self.purchase_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None,
            'is_deleted': self.is_deleted
        }
