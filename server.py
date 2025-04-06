import os
import dotenv
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

dotenv.load_dotenv()

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({'error': "No data found"}), 400

    prompt_text = data['prompt']

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_text),
            ],
        ),
    ]
    
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
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            generated_text += chunk.text
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'response': generated_text}), 200

if __name__ == '__main__':
    app.run(debug=True)
