import os
import dotenv
from google import genai
from google.genai import types

dotenv.load_dotenv()

# Initialize the GenAI client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_response(contents):
    """
    Accepts:
      - types.Content instances (with .parts of types.Part)
      - types.Part instances
      - plain strings
      - dicts with 'content' keys
    Flattens them to a list of strings, then streams via generate_content_stream.
    """

    # 1) Flatten everything into a list of prompt strings
    prompt_texts = []
    for item in contents:
        # case A: Content(role, parts=[Part,...])
        if isinstance(item, types.Content):
            for part in item.parts:
                prompt_texts.append(part.text)
        # case B: Part(text=...)
        elif isinstance(item, types.Part):
            prompt_texts.append(item.text)
        # case C: dict like {"role": "...", "content": "..."}
        elif isinstance(item, dict) and "content" in item:
            prompt_texts.append(str(item["content"]))
        # case D: already a raw string
        else:
            prompt_texts.append(str(item))

    # 2) Build generate_content config
    config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    # 3) Stream and accumulate the answer
    generated_text = ""
    try:
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=prompt_texts,
            config=config,
        ):
            generated_text += chunk.text
    except Exception as e:
        # Bubble up a clearer exception
        raise Exception(f"Error calling Gemini API: {e}")

    return generated_text
