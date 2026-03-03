from flask import Blueprint, request, jsonify, session, render_template
from app.services.auth_service import AuthService
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # If it's an API request, return 401
            if request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            # If it's a web page, redirect to login
            return render_template('login.html')
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return render_template('dashboard.html') # Redirect or render root
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    response, status_code = AuthService.register_user(
        data.get('username'), 
        data.get('email'), 
        data.get('password')
    )
    return jsonify(response), status_code

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    response, status_code = AuthService.login_user(
        data.get('email'), 
        data.get('password')
    )
    if status_code == 200:
        session['user_id'] = response.get('user_id')
    return jsonify(response), status_code

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200
