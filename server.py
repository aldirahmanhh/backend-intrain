import os
import dotenv
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

dotenv.load_dotenv()

app = Flask(__name__)

conversation_context = {}

def generate_response(contents):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    generated_text = ""
    try:
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=contents,
            config=generate_content_config,
        ):
            generated_text += chunk.text
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")
    
    return generated_text

@app.route('/')
def index():
    return "Server is Online!"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/chat', methods=['POST'])
def chat():

    data = request.get_json()
    if not data or 'user_id' not in data or 'message' not in data:
        return jsonify({'error': 'Parameter user_id dan message wajib disediakan.'}), 400

    user_id = data['user_id']
    user_message = data['message']

    if user_id not in conversation_context:
        conversation_context[user_id] = []

    # Tambahkan pesan baru dari user ke dalam riwayat
    conversation_context[user_id].append({
        "role": "user",
        "content": user_message
    })

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

if __name__ == '__main__':
    app.run(debug=True)
