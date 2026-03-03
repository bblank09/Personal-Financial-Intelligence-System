from app.extensions import db
from app.models.transaction import Transaction
from sqlalchemy import func
from datetime import datetime

class FinancialService:
    @staticmethod
    def add_transaction(user_id, amount, tx_type, category, date, note):
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
            
        new_tx = Transaction(
            user_id=user_id,
            amount=amount,
            type=tx_type,
            category=category,
            date=date,
            note=note
        )
        db.session.add(new_tx)
        db.session.commit()
        return new_tx

    @staticmethod
    def get_transactions(user_id, month=None, category=None, tx_type=None):
        query = Transaction.query.filter_by(user_id=user_id, is_deleted=False)
        if month:
             # assuming month is "YYYY-MM"
             year_str, month_str = month.split('-')
             query = query.filter(
                 func.extract('year', Transaction.date) == int(year_str),
                 func.extract('month', Transaction.date) == int(month_str)
             )
        if category:
             query = query.filter(Transaction.category.ilike(f"%{category}%"))
        if tx_type:
             query = query.filter(Transaction.type == tx_type)
             
        return query.order_by(Transaction.date.desc()).all()

    @staticmethod
    def calculate_total_income(user_id, month=None):
        query = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            Transaction.is_deleted == False
        )
        if month:
             year_str, month_str = month.split('-')
             query = query.filter(
                 func.extract('year', Transaction.date) == int(year_str),
                 func.extract('month', Transaction.date) == int(month_str)
             )
             
        total = query.scalar()
        return float(total) if total else 0.0

    @staticmethod
    def calculate_total_expense(user_id, month=None):
        query = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.is_deleted == False
        )
        if month:
             year_str, month_str = month.split('-')
             query = query.filter(
                 func.extract('year', Transaction.date) == int(year_str),
                 func.extract('month', Transaction.date) == int(month_str)
             )
             
        total = query.scalar()
        return float(total) if total else 0.0

    @staticmethod
    def calculate_saving_rate(user_id, month=None):
        income = FinancialService.calculate_total_income(user_id, month)
        expense = FinancialService.calculate_total_expense(user_id, month)

        if income <= 0:
            return 0.0

        savings = income - expense
        rate = savings / income
        return round(rate, 4)

    @staticmethod
    def get_expense_breakdown(user_id, month=None):
        query = db.session.query(
            Transaction.category, func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.is_deleted == False
        )
        if month:
            year_str, month_str = month.split('-')
            query = query.filter(
                func.extract('year', Transaction.date) == int(year_str),
                func.extract('month', Transaction.date) == int(month_str)
            )
            
        results = query.group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
        
        labels = [r[0] for r in results]
        data = [float(r[1]) for r in results]
        
        return {"labels": labels, "data": data}

    @staticmethod
    def get_cashflow_trend(user_id, month=None, months_back=6):
        import calendar
        from datetime import datetime
        
        if month:
            y_str, m_str = month.split('-')
            target_date = datetime(int(y_str), int(m_str), 1)
        else:
            target_date = datetime.today()
            
        months = []
        for i in range(months_back - 1, -1, -1):
            y = target_date.year
            m = target_date.month - i
            while m <= 0:
                m += 12
                y -= 1
            months.append(f"{y}-{m:02d}")
            
        labels = [calendar.month_abbr[int(m.split('-')[1])] for m in months]
        income_data = []
        expense_data = []
        
        for m in months:
            income_data.append(FinancialService.calculate_total_income(user_id, m))
            expense_data.append(FinancialService.calculate_total_expense(user_id, m))
            
        return {
            "labels": labels,
            "income": income_data,
            "expense": expense_data
        }
