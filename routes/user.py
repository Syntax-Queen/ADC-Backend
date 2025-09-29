from app import app, db
from flask import jsonify, request
from flask_cors import cross_origin
from toolz import random_generator, validate_email
from models import Comment, StoredjwtToken, User, PasswordResetToken, Post
from auth import auth

# Sign up
@app.route('/signup', methods=['POST'])
# @cross_origin()
def sign_up():
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if email is None and password is None:
            return jsonify({'error': 'Invalid input'}), 400
        
        if username is None or len(username) < 3:
            return jsonify({'error': 'Username must be more than 2 characters'}), 400
        
        if not  validate_email(email):
            return jsonify({'error': 'Enter a valid email address'}), 400
        
        exists = User.query.filter(User.email == email).first()
        if exists is not None:
            return jsonify({'error': 'User with email already exists'}), 400
        
        if password is None or  len(password) < 6:
            return jsonify({'error': 'Password must be more than 6 characters'})
        
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        new_user.set_password(password)
        
        try:
            db.session.commit()
            return jsonify({'success': True, 'Created': 'Account created successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'User signup error: {e}'}), 400
        
        

# Login 
@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.json

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User with this email does not exist'}), 404

    if not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 400

    # Remove old token if it exists
    saved_token = StoredjwtToken.query.filter_by(user_id=user.id).first()
    if saved_token:
        db.session.delete(saved_token)
        db.session.commit()

    # Generate new token
    token = user.generate_auth_token()
    new_jwt_token = StoredjwtToken(user_id=user.id, jwt_token=token)
    db.session.add(new_jwt_token)
    db.session.commit()

    return jsonify({'success': True, 'token': token}), 200


# forget password
@app.route('/forget-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    
    # check if email exists
    if email is None:
        return jsonify({'error': 'Please enter email'}), 400
    
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({'error': 'User with this email does not exist'}), 400
    
    # create a password reset token
    token = random_generator(8)
    reset = PasswordResetToken(token=token, user_id=user.id, used=False)
    db.session.add(reset)
    db.session.commit()
    
    # send password reset token to email
    return jsonify({'success': True, 'message': 'Password reset email sent'}), 200

# reset password
@app.route('/reset-password', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    new_password = request.json.get('new_password')
    confirm_password = request.json.get('confirm_password')
    
    if new_password is None or confirm_password != new_password:
        return jsonify({'error': 'Password does not match'}), 400
    
    if token is None:
        return jsonify({'error': 'Please enter token'}), 400
    
    reset = PasswordResetToken.query.filter_by(token=token).first()
    if reset is None:
        return jsonify({'error': 'Invalid token'}), 400
    
    if reset.used:
        return jsonify({'error': 'Token has been used already'}), 400
    
    user = User.query.filter_by(id=reset.user_id).first()
    if user is None:
        return jsonify({'error':' User not found'}), 400
    
    user.set_password(new_password)
    reset.used = True
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password reset successfully'}), 200


# delete users
@app.route('/<int:did>', methods=['DELETE'])
def delete_user(did):
    user = User.query.filter(User.id == did).first()
    if user is None:
        return jsonify({'error': 'User does not exit'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'done': True, 'Message': f'{user.username} Account deleted successfully'})
    

# Post
@app.route('/post', methods=['POST'])
@auth.login_required
def post():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    current_user = auth.current_user()
    
    if not title or not content:
        return jsonify({'error':False, 'Message': 'Invalid input'}), 400
    
    post = Post(title=title, content=content, user_id=current_user.id)
    
    db.session.add(post)
    db.session.commit()
    return jsonify({
        'success': True, 
        'post': {
            'id': post.id,
            'title':post.title,
            'content': post.content,
            'author': current_user.username
            
        }
        }), 201


# view all posts and comments
@app.route('/view-posts-comment', methods=['GET'])
def view_post_comment():
    posts = Post.query.all()
    results = []
    
    for post in posts:
        results.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author_id' : post.user_id,
            'created_at' : post.created_at.isoformat(),
            
            'comment': [
                {
                    'id' : c.id,
                    'comment': c.comment,
                    'author_id' : c.user_id,
                    'created_at' : c.created_at.isoformat()
                } for c in post.comments
            ]
            
        })
    return jsonify(results), 200
 
 
# view single post with the comment
@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    
    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    result = {
        'id': post.id,
        'title' : post.title,
        'content': post.content,
        'author_id' : post.user_id,
        'created_at' : post.created_at.isoformat(),
        
        'comments' : [
            {
            'id' : c.id,
                    'comment': c.comment,
                    'author_id' : c.user_id,
                    'created_at' : c.created_at.isoformat()
                } for c in post.comments
            ]
        
    } 
    return jsonify(result), 200


# post comment   
@app.route('/add-comment/<int:post_id>', methods=['POST'])
@auth.login_required
def add_comment(post_id):
    data = request.json
    comment = data.get('comment')
    current_user = auth.current_user()
    
    if not comment:
        return jsonify({'error': 'Comment content is required'}), 400
    
    # check if post exist
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # create comment
    user_comment = Comment(comment=comment, user_id=current_user.id, post_id=post.id)
    
    db.session.add(user_comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': user_comment.id,
            'comment': user_comment.comment,
            'author': current_user.username,
            'post_id': post.id,
            'created_at' : user_comment.created_at.isoformat()
        }
    }), 201
    