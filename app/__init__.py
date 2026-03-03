from flask import Flask
from app.config import Config
from app.extensions import db, migrate
from app.mongo.mongo_client import init_mongo

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MySQL extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize MongoDB
    init_mongo(app)

    # Register blueprints (routes)
    from app.routes.auth_routes import auth_bp
    from app.routes.transaction_routes import transaction_bp
    from app.routes.investment_routes import investment_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.forecast_routes import forecast_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(forecast_bp)

    @app.context_processor
    def inject_user():
        from flask import session
        from app.models.user import User
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return dict(current_user=user)
        return dict(current_user=None)

    return app
