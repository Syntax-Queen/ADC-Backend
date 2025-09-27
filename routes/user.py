from app import app, db
from flask import jsonify, request
# from flask_cors import cross_origin
from toolz import validate_email, random_generator
from models import StoredjwtToken, User, PasswordResetToken, CartItem, Product
from auth import auth

# Sign up
@app.route('/signup', methods=['POST'])
# @cross_origin()
def sign_up():
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email is None and password is None:
            return jsonify({'error': 'Invalid input'}), 400
        
        if not  validate_email(email):
            return jsonify({'error': 'Enter a valid email address'}), 400
        
        exists = User.query.filter(User.email == email).first()
        if exists is not None:
            return jsonify({'error': 'User with email already exists'}), 400
        
        if password is None or  len(password) > 6:
            return jsonify({'error': 'Password must be more than 6 characters'})
        
        new_user = User(email=email)
        db.session.add(new_user)
        new_user.set_password(password)
        
        try:
            db.session.commit()
            return jsonify({'success': True, 'Created': 'Account created successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'User signup error: {e}'}), 400