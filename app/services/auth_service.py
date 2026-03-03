from app.extensions import db
from app.models.user import User
from app.utils.password import hash_password, verify_password

class AuthService:
    @staticmethod
    def register_user(username, email, password):
        if User.query.filter_by(email=email).first():
            return {"error": "Email already exists"}, 400
            
        hashed_password = hash_password(password)
        new_user = User(name=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return {"message": "User registered successfully", "user": new_user.to_dict()}, 201

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email, is_deleted=False).first()
        
        if user and verify_password(user.password_hash, password):
            return {"user_id": user.id, "message": "Login successful"}, 200
        
        return {"error": "Invalid email or password"}, 401
