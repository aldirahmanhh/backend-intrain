import os
import uuid
import tempfile

from google.cloud import speech
from google.cloud import storage
from gtts import gTTS

SA_PATH    = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_BUCKET = os.getenv("GCP_BUCKET")
if not SA_PATH or not os.path.isfile(SA_PATH):
    raise RuntimeError("Set GOOGLE_APPLICATION_CREDENTIALS to your key file")
if not GCP_BUCKET:
    raise RuntimeError("Set GCP_BUCKET in your .env")

_storage = storage.Client.from_service_account_json(SA_PATH)
_bucket  = _storage.bucket(GCP_BUCKET)
_stt     = speech.SpeechClient.from_service_account_file(SA_PATH)

def _upload(local_path, dest, content_type):
    blob = _bucket.blob(dest)
    blob.upload_from_filename(local_path, content_type=content_type)
    return f"https://storage.googleapis.com/{GCP_BUCKET}/{dest}"

def transcribe_mp3_file(uploaded_mp3) -> str:
    # 1) Save the incoming MP3
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    uploaded_mp3.save(tmp.name)

    # 2) Upload it straight to GCS as MP3
    dest = f"raw_audio/{uuid.uuid4()}.mp3"
    _bucket.blob(dest).upload_from_filename(tmp.name, content_type="audio/mp3")
    gcs_uri = f"gs://{GCP_BUCKET}/{dest}"

    # 3) Ask STT to decode MP3 directly
    audio  = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding         = speech.RecognitionConfig.AudioEncoding.MP3,
        language_code    = "id-ID"
    )
    response = _stt.recognize(config=config, audio=audio)

    # 4) Build transcript
    return " ".join(r.alternatives[0].transcript for r in response.results)

def synthesize_to_mp3(text: str) -> str:
    from gtts import gTTS
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    gTTS(text=text, lang="id").save(tmp.name)
    dest = f"tts_audio/{uuid.uuid4()}.mp3"
    return _upload(tmp.name, dest, "audio/mp3")