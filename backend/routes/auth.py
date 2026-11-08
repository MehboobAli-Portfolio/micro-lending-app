from datetime import datetime, timedelta
import os
from flask import Blueprint, jsonify, request
import bcrypt
import jwt
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)
JWT_SECRET = os.getenv('JWT_SECRET', 'super_secret_micro_lending_key_2026')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
        
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    except Exception:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()
        
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
        
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(hours=8)
        }, JWT_SECRET, algorithm="HS256")
        
        return jsonify({'token': token, 'message': 'Access granted to Finance Manager dashboard.'}), 200
        
    return jsonify({'error': 'Authentication failure, access denied.'}), 401