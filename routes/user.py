from app import socketio
from app import app, db
from flask import jsonify, request
from flask_cors import cross_origin
from toolz import random_generator, validate_email
from models import ChatMessage, Comment, Group, GroupMember, Message, StoredjwtToken, User, PasswordResetToken, Post
from auth import auth
from datetime import datetime, timedelta
import uuid
from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    posts = Post.query.order_by(Post.created_at.desc()).all()
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
                } for c in sorted(post.comments, key=lambda x: x.created_at, reverse=True)
            ]
            
        })
    return jsonify(results), 200
 
# view post by user_id
@app.route('/view-user-posts/<int:user_id>', methods=['GET'])
def view_user_posts(user_id):
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    results = []
    
    for post in posts:
        results.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author_id': post.user_id,
            'created_at': post.created_at.isoformat(),
            
            'comment': [
                {
                    'id': c.id,
                    'comment': c.comment,
                    'author_id': c.user_id,
                    'created_at': c.created_at.isoformat()
                } for c in sorted(post.comments, key=lambda x: x.created_at, reverse=True)
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

# view comment
@app.route('/post/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    comments = [
        {
                'id' : c.id,
                'comment': c.comment,
                'author_id' : c.user_id,
                'created_at' : c.created_at.isoformat()
                } for c in post.comments
            
    ]
    return jsonify(comments), 200


# edit post after 24 hours
@app.route('/post/<int:post_id>/edit', methods=['PUT'])
@auth.login_required
def edit_post(post_id):
    data = request.json
    current_user = auth.current_user()
    
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 400
    
    # check ownership
    if post.user_id != current_user.id:
        return jsonify({'error': 'You can only edit your own posts'}), 403
    
    # check time restriction
    time_limit = post.created_at + timedelta(hours=3)
    if datetime.utcnow() > time_limit:
        return jsonify({'error': 'Edit window has expired. Posts can only be edited within 3 hours'}), 403
    
    # changes update
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    db.session.commit()
    
    return jsonify({'success': True, 
                    'message' : 'Post updated successfully',
                    'post' : {
                        'id' : post.id,
                        'title': post.title,
                        'content' : post.content,
                        'created_at' : post.created_at.isoformat()
                    }
                    
                    }), 200
    

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
 

# create group
@app.route('/groups', methods=['POST'])
@auth.login_required
def create_group():
    data = request.json
    current_user = auth.current_user()
    
    group = Group(
        name = data.get('name'),
        owner_id = current_user.id,
        invite_link = str(uuid.uuid4())  #unique join link
        
    )
    
    db.session.add(group)
    db.session.commit()
    
    # add creator as member
    membership = GroupMember(user_id=current_user.id, group_id=group.id, role="admin")
    db.session.add(membership)
    db.session.commit()
    
    return jsonify({
        "id" : group.id,
        "name": group.name,
        "invite_link" : f"/join/{group.invite_link}"
    }), 201
    
    

# join group through link
@app.route('/join/<invite_link>', methods=['POST'])
@auth.login_required
def join_group(invite_link):
    current_user = auth.current_user()
    
    group = Group.query.filter_by(invite_link=invite_link).first()
    
    if not group:
        return jsonify({'error': 'Invalid link'}), 404
    
    # prevent duplicate join
    if GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first():
        return jsonify({'error': 'Already a member'}), 400
    
    member = GroupMember(user_id=current_user.id, group_id=group.id)
    db.session.add(member)
    db.session.commit()
    
    return jsonify({'success': f'You joined {group.name}'}), 200



# to remove member
@app.route('/groups/<int:group_id>/remover/<int:user_id>', methods=['DELETE'])
@auth.login_required
def remove_member(group_id, user_id):
    current_user = auth.current_user()
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({'error': 'group not found'}), 404
    
    # only admin or self removal allowed
    if group.owner_id != current_user.id and current_user != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'User not in group'}), 404
    
    db.session.delete(membership)
    db.session.commit()
    
    return jsonify({'success': 'User removed'}), 200


# delete Group
@app.route('/groups/<int:group_id>', methods=['DELETE'])
@auth.login_required
def delete_group(group_id):
    current_user = auth.current_user()
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    if group.owner_id != current_user.id:
        return jsonify({"error": "Only the owner can delete the group"}), 403
    
    # delete related rows
    GroupMember.query.filter_by(group_id=group_id).delete()
    Message.query.filter_by(group_id=group_id).delete()
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({"success": "Group deleted"}), 200


# Send message in Group
@app.route('/groups/<int:group_id>', methods=['POST'])
@auth.login_required
def send_message(group_id):
    current_user = auth.current_user()
    data = request.json
    
    # check membership
    membership = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    msg = Message(group_id=group_id, user_id=current_user.id, content=data.get('content'))
    db.session.add(msg)
    db.session.commit()
    
    socketio.emit(
    "new_message",
    {"message": msg.content, "user": current_user.username},
    room=f"group_{group_id}"
)
    
    return jsonify({'success': True, 'message_id': msg.id}), 201


# view message 
@app.route("/groups/<int:group_id>/messages", methods=["GET"])
@auth.login_required
def view_messages(group_id):
    current_user = auth.current_user()

    # check if user is a member of the group
    membership = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    if not membership:
        return jsonify({"error": "You are not a member of this group"}), 403

    # fetch all messages for this group, newest first (or oldest first if you prefer)
    messages = Message.query.filter_by(group_id=group_id).order_by(Message.created_at.asc()).all()

    # prepare response
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "user_id": msg.user_id,
            "username": msg.user.username,   # assuming relationship User
            # "reply_to": msg.reply_to
        })

    return jsonify(result), 200

# 

# chat with ai
# @app.route('/interpret', methods=['POST'])
# def interpret_dream():
#     data = request.json
#     dream_text = data.get("dream")
    
#     if not dream_text:
#         return jsonify({'error': "No dream provided"})
    
#     # call openai
#     response = client.responses.create(
#         model = 'gpt-4.1-mini',
        
#         input=f"You are a dream interpretation AI. Interpret the following dream: {dream_text}",
        
#         max_output_tokens = 500
#     )
    
#      # The text output is in response.output_text
#     interpretation = response.output_text
#     return jsonify({"interpretation": interpretation})


# chat with ai
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    dream_text = data.get("dream")
    token = request.headers.get("Authorization")  # if logged in

    if not dream_text:
        return jsonify({'error': "No dream provided"}), 400

    current_user = None
    if token:
        current_user = auth.current_user()  # logged in user

    # If guest, only allow once
    if not current_user:
        # no user means guest → no chat history
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"You are a dream interpretation AI. Interpret the following dream: {dream_text}",
            max_output_tokens=500
        )
        return jsonify({"interpretation": response.output_text, "guest": True})

    # If logged in, fetch conversation history
    history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at).all()
    messages = [{"role": h.role, "content": h.content} for h in history]

    # Add new user message
    messages.append({"role": "user", "content": dream_text})

    # Call OpenAI with history
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a dream interpretation AI. Be empathetic and insightful."},
            *messages
        ],
        max_tokens=500
    )

    reply = response.choices[0].message["content"]

    # Save user + AI messages to DB
    db.session.add(ChatMessage(user_id=current_user.id, role="user", content=dream_text))
    db.session.add(ChatMessage(user_id=current_user.id, role="assistant", content=reply))
    db.session.commit()

    return jsonify({"reply": reply, "guest": False})
