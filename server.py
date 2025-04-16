import uuid
import dotenv

from flask import Flask, request, jsonify

from google import genai
from google.genai import types

from core.generate import generate_response

dotenv.load_dotenv()

app = Flask(__name__)

# In-memory storage for users and conversation context
users = {}
conversation_context = {}

@app.route('/')
def index():
    return "Server is Online!"

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# Chat Endpoint
@app.route('/api/v1/feature/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'user_id' not in data or 'message' not in data:
        return jsonify({'error': 'Parameters user_id and message are required.'}), 400

    user_id = data['user_id']
    user_message = data['message']

    # Check if the user is registered
    if user_id not in users:
        return jsonify({'error': 'User not found. Please login or register first.'}), 404

    if user_id not in conversation_context:
        conversation_context[user_id] = []

    # Append new user message into the conversation history
    conversation_context[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Prepare list of contents to send to the Gemini API.
    contents = []
    for msg in conversation_context[user_id]:
        content = types.Content(
            role=msg["role"],
            parts=[types.Part.from_text(text=msg["content"])]
        )
        contents.append(content)

    try:
        reply_text = generate_response(contents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    conversation_context[user_id].append({
        "role": "assistant",
        "content": reply_text
    })

    return jsonify({
        'response': reply_text,
        'context': conversation_context[user_id]
    }), 200

# User Register Endpoint
@app.route('/api/v1/auth/user/register', methods=['POST'])
def register():
    data = request.get_json()
    # Required parameters: username and password
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Parameters username and password are required.'}), 400

    username = data['username']
    password = data['password']
    # Optional: additional user data (e.g., name, email)
    name = data.get('name', '')
    email = data.get('email', '')

    # Check if username already exists
    for user in users.values():
        if user['username'] == username:
            return jsonify({'error': 'Username is already registered.'}), 400

    # Generate a unique user ID using uuid
    user_id = str(uuid.uuid4())

    # Save user data in the dictionary
    users[user_id] = {
        'user_id': user_id,
        'username': username,
        'password': password,  # Do not store plain passwords in production!
        'name': name,
        'email': email
    }

    return jsonify({
        'message': 'Registration successful.',
        'user': users[user_id]
    }), 201

# User Login Endpoint
@app.route('/api/v1/auth/user/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Parameters username and password are required.'}), 400

    username = data['username']
    password = data['password']

    # Search for the user by username and verify the password
    for user in users.values():
        if user['username'] == username and user['password'] == password:
            return jsonify({
                'message': 'Login successful.',
                'user': user
            }), 200

    return jsonify({'error': 'Incorrect username or password.'}), 401

# Update User Data Endpoint
@app.route('/api/v1/auth/user/update', methods=['PUT'])
def update_user():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'error': 'Parameter user_id is required.'}), 400

    user_id = data['user_id']

    if user_id not in users:
        return jsonify({'error': 'User not found.'}), 404

    # Parameters that can be updated: username, password, name, email
    username = data.get('username', users[user_id]['username'])
    password = data.get('password', users[user_id]['password'])
    name = data.get('name', users[user_id]['name'])
    email = data.get('email', users[user_id]['email'])

    # Update the user data
    users[user_id].update({
        'username': username,
        'password': password,
        'name': name,
        'email': email
    })

    return jsonify({
        'message': 'User data updated successfully.',
        'user': users[user_id]
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
