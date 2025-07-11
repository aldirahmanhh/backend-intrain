import os
import uuid
import tempfile
from dotenv import load_dotenv
from pydub import AudioSegment
from google.cloud import speech, storage
from gtts import gTTS

load_dotenv()

SA_PATH    = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCS_BUCKET = os.getenv("GCS_BUCKET")
if not SA_PATH or not os.path.isfile(SA_PATH):
    raise RuntimeError("Set GOOGLE_APPLICATION_CREDENTIALS to your key file")
if not GCS_BUCKET:
    raise RuntimeError("Set GCS_BUCKET in your .env")

# Initialize GCS & STT clients
_storage = storage.Client.from_service_account_json(SA_PATH)
_bucket  = _storage.bucket(GCS_BUCKET)
_stt     = speech.SpeechClient.from_service_account_file(SA_PATH)

def _upload_file(local_path: str, dest_path: str, content_type: str) -> str:
    blob = _bucket.blob(dest_path)
    blob.upload_from_filename(local_path, content_type=content_type)
    return f"https://storage.googleapis.com/{GCS_BUCKET}/{dest_path}"

def _convert_to_mp3_with_pydub(input_path: str) -> str:
    """
    Load any audio file via pydub, resample to 16kHz mono, and export as MP3.
    """
    sound = AudioSegment.from_file(input_path)
    sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    out_tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    # implicit libmp3lame
    sound.export(out_tmp.name, format="mp3")
    return out_tmp.name

def transcribe_audio_file(uploaded_file) -> str:
    """
    1) Save raw upload to disk.
    2) Convert to 16kHz mono MP3 via pydub.
    3) Upload to GCS.
    4) Call Google STT with encoding=MP3.
    """
    # 1) Save incoming file
    raw_tmp = tempfile.NamedTemporaryFile(delete=False)
    uploaded_file.save(raw_tmp.name)

    # 2) Re-encode to correct MP3
    mp3_path = _convert_to_mp3_with_pydub(raw_tmp.name)

    # 3) Upload
    dest     = f"raw_audio/{uuid.uuid4()}.mp3"
    _upload_file(mp3_path, dest, "audio/mp3")
    gcs_uri  = f"gs://{GCS_BUCKET}/{dest}"

    # 4) Recognize
    audio_req = speech.RecognitionAudio(uri=gcs_uri)
    config    = speech.RecognitionConfig(
        encoding          = speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz = 16000,
        language_code     = "id-ID"
    )
    resp = _stt.recognize(config=config, audio=audio_req)
    # concatenate all results
    return " ".join(r.alternatives[0].transcript for r in resp.results)

def synthesize_text_to_mp3(text: str) -> str:
    """
    Synthesize via gTTS, upload, and return public MP3 URL.
    """
    tts_tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    gTTS(text=text, lang="id").save(tts_tmp.name)
    dest    = f"tts_audio/{uuid.uuid4()}.mp3"
    return _upload_file(tts_tmp.name, dest, "audio/mp3")
