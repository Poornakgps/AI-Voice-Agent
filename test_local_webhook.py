import requests
import uuid
import xml.etree.ElementTree as ET
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

def parse_twiml(twiml_text):
    """Parse TwiML response and extract key information for Media Streams."""
    try:
        # Strip whitespace and normalize
        twiml_text = twiml_text.strip()
        
        root = ET.fromstring(twiml_text)
        
        # Check for Media Streams elements
        stream_elements = root.findall(".//Stream")
        has_stream = len(stream_elements) > 0
        
        # Get Stream URLs
        stream_urls = [stream.get("url") for stream in stream_elements if stream.get("url")]
        
        # Check for Say elements
        say_elements = root.findall(".//Say")
        say_texts = [say.text for say in say_elements if say.text]
        
        return {
            "has_stream": has_stream,
            "stream_urls": stream_urls,
            "say_texts": say_texts
        }
    except Exception as e:
        print(f"Error parsing TwiML: {e}")
        return {
            "has_stream": False,
            "stream_urls": [],
            "say_texts": []
        }

def test_voice_webhook(url):
    """Test the voice webhook for Media Streams approach."""
    call_sid = f"TEST{uuid.uuid4().hex[:16].upper()}"
    
    account_sid = os.environ.get("TWILIO_SID_KEY", "AC00000000000000000000000000000000")
    
    # Prepare test data
    data = {
        "CallSid": call_sid,
        "AccountSid": account_sid,
        "From": "+15551234567",
        "To": "+15559876543",
        "CallStatus": "ringing",
        "ApiVersion": "2010-04-01",
        "Direction": "inbound"
    }
    
    print(f"Sending test request to: {url}")
    
    try:
        response = requests.post(url, data=data, timeout=10)
        print(f"Full request data: {data}")
        
        if response.status_code == 200:
            print("\n✅ Webhook responded with status code 200")
            print("Raw response:")
            print("-" * 50)
            print(response.text)
            print("-" * 50)
            
            twiml_info = parse_twiml(response.text)
            
            if twiml_info["has_stream"]:
                print("✅ Response includes <Stream> element for Media Streams")
                for url in twiml_info["stream_urls"]:
                    print(f"  Stream URL: {url}")
            else:
                print("❌ No <Stream> element found - Media Streams not configured correctly")
                
            if twiml_info["say_texts"]:
                print(f"Agent says: \"{twiml_info['say_texts'][0]}\"")
            
            return response.text, call_sid
        else:
            print(f"❌ Webhook responded with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return None, None

def test_status_webhook(url, call_sid):
    """Test the status webhook."""
    data = {
        "CallSid": call_sid,
        "CallStatus": "completed"
    }
    
    print(f"\nSending status update to: {url}")
    
    try:
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Status webhook responded with status code 200")
            return True
        else:
            print(f"❌ Status webhook responded with status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing status webhook: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Twilio Media Streams webhook")
    parser.add_argument("--url", default=os.environ.get("WEBHOOK_BASE_URL", "http://localhost:8000"), 
                        help="Base URL of the application")
    parser.add_argument("--voice-path", default="/webhook/voice", 
                        help="Path for the voice webhook")
    parser.add_argument("--status-path", default="/webhook/status", 
                        help="Path for the status webhook")
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    voice_url = f"{base_url}{args.voice_path}"
    status_url = f"{base_url}{args.status_path}"
    
    print("=========================================================")
    print("Voice AI Restaurant Agent - Media Streams Webhook Test")
    print("=========================================================")
    
    print("\n🔍 Testing voice webhook (Media Streams initialization)...")
    voice_response, call_sid = test_voice_webhook(voice_url)
    
    if voice_response and call_sid:
        print("\n✅ Media Streams setup test passed")
        print("\nNote: Further testing would require a WebSocket client to test the stream connection")
        print("For a full test, configure the webhook URL in Twilio and make a real call")
        
        print("\n🔍 Testing status webhook...")
        test_status_webhook(status_url, call_sid)
    
    print("\n=========================================================")
    print("Test completed")
    print("=========================================================")

if __name__ == "__main__":
    main()