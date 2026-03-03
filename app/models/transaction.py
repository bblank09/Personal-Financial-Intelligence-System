from app.extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.today)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'type': self.type,
            'category': self.category,
            'date': self.date.isoformat() if self.date else None,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
