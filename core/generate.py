import os
import dotenv
from google import genai
from google.genai import types
from googletrans import Translator  # add this

dotenv.load_dotenv()

# Initialize the GenAI client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize translator
translator = Translator()

def generate_response(contents):
    """
    Accepts:
      - types.Content instances (with .parts of types.Part)
      - types.Part instances
      - plain strings
      - dicts with 'content' keys
    Flattens them to a list of strings, then streams via generate_content_stream.
    Finally, translates the result into Bahasa Indonesia.
    """

    # 1) Flatten everything into a list of prompt strings
    prompt_texts = []
    for item in contents:
        if isinstance(item, types.Content):
            for part in item.parts:
                prompt_texts.append(part.text)
        elif isinstance(item, types.Part):
            prompt_texts.append(item.text)
        elif isinstance(item, dict) and "content" in item:
            prompt_texts.append(str(item["content"]))
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
        raise Exception(f"Error calling Gemini API: {e}")

    # 4) Translate to Bahasa Indonesia
    try:
        translated = translator.translate(generated_text, dest="id").text
    except Exception as e:
        # If translation fails, fall back to original
        translated = generated_text

    return translated
