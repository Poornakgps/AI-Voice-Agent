import requests
import base64
import sys
import os

def test_tts(text, server_url="http://localhost:8000"):
    """Test text-to-speech conversion."""
    print(f"Testing TTS with text: '{text}'")
    
    response = requests.post(
        f"{server_url}/test/tts",
        data={"text": text}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    filename = "test_output.mp3"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(data["audio_base64"]))
    
    print(f"Audio saved to {filename}")
    print(f"Duration: {data['duration']} seconds")
    return True

def test_stt(audio_url, server_url="http://localhost:8000"):
    """Test speech-to-text transcription."""
    print(f"Testing STT with URL: '{audio_url}'")
    
    response = requests.post(
        f"{server_url}/test/stt",
        data={"audio_url": audio_url}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    print(f"Transcription: '{data['transcription']}'")
    return True

def test_full_loop(text, server_url="http://localhost:8000"):
    """Test complete TTS -> STT pipeline with OpenAI for transcription."""
    import uuid
    import openai
    import os
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment")
        return False
    
    filename = f"test_output_{uuid.uuid4()}.mp3"
    
    print(f"Testing TTS with text: '{text}'")
    response = requests.post(
        f"{server_url}/test/tts",
        data={"text": text}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    try:
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data["audio_base64"]))
        
        print(f"Audio saved to {filename}")
        print(f"Duration: {data['duration']} seconds")
        
        client = openai.OpenAI(api_key=api_key)
        
        with open(filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        original = text.lower()
        transcribed = transcription.text.lower()
        
        print(f"Original text: '{original}'")
        print(f"Transcribed: '{transcribed}'")
        
        return True
    except Exception as e:
        print(f"Error in test loop: {str(e)}")
        return False
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python test_audio_api.py tts 'Text to convert to speech'")
        print("  python test_audio_api.py stt 'http://example.com/audio.mp3'")
        sys.exit(1)
    
    test_type = sys.argv[1]
    value = sys.argv[2]
    
    if test_type == "tts":
        test_tts(value)
    elif test_type == "stt":
        test_stt(value)
    elif test_type == "full_loop":
        test_full_loop(value)
    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)
        
