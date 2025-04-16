import os
import dotenv
from google import genai
from google.genai import types

dotenv.load_dotenv()

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