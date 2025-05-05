from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from app.voice.tts import synthesize_speech
from app.voice.stt import transcribe_audio
from app.core.models import VoiceSettings

router = APIRouter()

@router.post("/test/tts")
async def test_tts(text: str = Form(...)):
    """Test TTS by converting text to speech."""
    response = await synthesize_speech(text)
    return JSONResponse({
        "audio_base64": response.audio_content_base64,
        "duration": response.duration_seconds,
        "content_type": response.content_type
    })

@router.post("/test/stt")
async def test_stt(audio_url: str = Form(...)):
    """Test STT by transcribing audio from URL."""
    transcription = await transcribe_audio(audio_url)
    return JSONResponse({"transcription": transcription})