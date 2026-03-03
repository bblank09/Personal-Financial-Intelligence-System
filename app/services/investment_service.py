from app.extensions import db
from app.models.investment import Investment
from sqlalchemy import func

class InvestmentService:
    @staticmethod
    def get_investments(user_id):
        return Investment.query.filter_by(user_id=user_id, is_deleted=False).order_by(Investment.purchase_date.desc()).all()

    @staticmethod
    def add_investment(user_id, symbol, asset_name, quantity, price, purchase_date):
        new_inv = Investment(
            user_id=user_id,
            symbol=symbol,
            asset_name=asset_name,
            quantity=quantity,
            price=price,
            purchase_date=purchase_date
        )
        db.session.add(new_inv)
        db.session.commit()
        return new_inv

    @staticmethod
    def update_investment(user_id, inv_id, data):
        inv = Investment.query.filter_by(id=inv_id, user_id=user_id, is_deleted=False).first()
        if not inv:
            return None
        
        for key, value in data.items():
            if hasattr(inv, key) and key not in ['id', 'user_id', 'created_at']:
                setattr(inv, key, value)
        
        db.session.commit()
        return inv

    @staticmethod
    def delete_investment(user_id, inv_id):
        inv = Investment.query.filter_by(id=inv_id, user_id=user_id, is_deleted=False).first()
        if not inv:
            return False
            
        inv.is_deleted = True
        db.session.commit()
        return True

    @staticmethod
    def get_portfolio_summary(user_id):
        """
        Groups transactions by symbol.
        Calculates average price, fetches current price via yfinance, and computes profit.
        """
        transactions = Investment.query.filter_by(user_id=user_id, is_deleted=False).all()
        
        portfolio = {}
        for t in transactions:
            sym = t.symbol
            if sym not in portfolio:
                portfolio[sym] = {
                    "symbol": sym,
                    "asset_name": t.asset_name,
                    "total_quantity": 0.0,
                    "total_invested": 0.0
                }
            portfolio[sym]["total_quantity"] += t.quantity
            portfolio[sym]["total_invested"] += (t.quantity * t.price)

        total_investment = 0.0
        total_portfolio_value = 0.0
        allocation = {}

        try:
            import yfinance as yf
        except ImportError:
            yf = None

        assets = []
        for sym, data in portfolio.items():
            if data["total_quantity"] <= 0:
                continue

            avg_price = data["total_invested"] / data["total_quantity"]
            data["avg_price"] = avg_price
            
            current_price = avg_price # fallback
            if yf:
                try:
                    # Append -USD for crypto if not present and if it seems like a common crypto
                    fetch_sym = sym
                    if fetch_sym.upper() in ['BTC', 'ETH', 'SOL', 'ADA', 'XRP', 'DOGE', 'DOT']:
                        fetch_sym = f"{fetch_sym.upper()}-USD"
                        
                    ticker = yf.Ticker(fetch_sym)
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                except Exception:
                    pass
            
            data["current_price"] = current_price
            current_value = data["total_quantity"] * current_price
            data["current_value"] = current_value
            data["profit"] = current_value - data["total_invested"]
            data["return_percent"] = round((data["profit"] / data["total_invested"]) * 100, 2) if data["total_invested"] > 0 else 0.0
            
            total_investment += data["total_invested"]
            total_portfolio_value += current_value
            assets.append(data)
            allocation[sym] = current_value

        profit = total_portfolio_value - total_investment
        return_percent = round((profit / total_investment) * 100, 2) if total_investment > 0 else 0.0

        # Normalize allocation percentages
        if total_portfolio_value > 0:
            for sym in allocation:
                allocation[sym] = round((allocation[sym] / total_portfolio_value) * 100, 2)

        return {
            "assets": assets,
            "total_investment": total_investment,
            "portfolio_value": total_portfolio_value,
            "profit": profit,
            "return_percent": return_percent,
            "allocation": allocation
        }

    @staticmethod
    def calculate_totals(user_id):
        # Fallback method used by AnalyticsService (legacy compatibility)
        summary = InvestmentService.get_portfolio_summary(user_id)
        return {
            "total_investment": summary["total_investment"],
            "portfolio_value": summary["portfolio_value"],
            "profit": summary["profit"],
            "return_percent": summary["return_percent"],
            "allocation": summary["allocation"]
        }
