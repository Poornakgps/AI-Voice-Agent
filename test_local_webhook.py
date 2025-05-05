#!/usr/bin/env python
"""
Simple script to test your Twilio webhooks locally without default messages.
"""
import requests
import uuid
import xml.etree.ElementTree as ET
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_twiml(twiml_text):
    """Parse TwiML response and extract key information."""
    try:
        root = ET.fromstring(twiml_text)
        say_elements = root.findall(".//Say")
        say_texts = [say.text for say in say_elements if say.text]
        
        record_elements = root.findall(".//Record")
        has_record = len(record_elements) > 0
        
        gather_elements = root.findall(".//Gather")
        has_gather = len(gather_elements) > 0
        
        hangup_elements = root.findall(".//Hangup")
        has_hangup = len(hangup_elements) > 0
        
        return {
            "say_texts": say_texts,
            "has_record": has_record,
            "has_gather": has_gather,
            "has_hangup": has_hangup
        }
    except Exception as e:
        print(f"Error parsing TwiML: {e}")
        return {
            "say_texts": [],
            "has_record": False,
            "has_gather": False,
            "has_hangup": False
        }

def test_voice_webhook(url):
    """Test the voice webhook with a simple request."""
    # Generate a unique call SID
    call_sid = f"TEST{uuid.uuid4().hex[:16].upper()}"
    
    # Get Twilio Account SID from environment or use a dummy one
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
        # Send the request
        response = requests.post(url, data=data, timeout=10)
        print(f"Full request data: {data}")
        print(f"Full response: {response.text}")
        # Check the response
        if response.status_code == 200:
            print("\n✅ Webhook responded with status code 200")
            print("Raw response:")
            print("-" * 50)
            print(response.text)
            print("-" * 50)
            
            # Parse the TwiML
            twiml_info = parse_twiml(response.text)
            
            # Display parsed information
            if twiml_info["say_texts"]:
                print(f"Agent says: \"{twiml_info['say_texts'][0]}\"")
            else:
                print("⚠️ No <Say> element found in response")
                
            if twiml_info["has_record"]:
                print("✅ Response includes <Record> element (will capture user speech)")
            else:
                print("⚠️ No <Record> element found in response")
                
            return response.text, call_sid
        else:
            print(f"❌ Webhook responded with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return None, None

def test_transcribe_webhook(url, call_sid, message=None):
    """Test the transcribe webhook with a user-provided message."""
    # If no message provided, prompt the user to input one
    if message is None:
        message = input("Enter message to test (or press Enter for empty message): ").strip()
    
    # Generate a recording SID
    recording_sid = f"RE{uuid.uuid4().hex[:16].upper()}"
    
    # Get Twilio Account SID from environment
    account_sid = os.environ.get("TWILIO_SID_KEY", "AC00000000000000000000000000000000")
    
    # Create a realistic recording URL
    recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording_sid}"
    
    # Prepare test data
    data = {
        "CallSid": call_sid,
        "AccountSid": account_sid,
        "RecordingSid": recording_sid,
        "RecordingUrl": recording_url,
        "RecordingStatus": "completed",
        "RecordingDuration": "5",
    }
    
    # Only add transcript if there is a message
    if message:
        data["Transcript"] = message
    
    print(f"\nSending transcribe request to: {url}")
    print(f"With message: \"{message}\"" if message else "With empty message")
    
    try:
        # Send the request
        response = requests.post(url, data=data, timeout=10)
        
        # Check the response
        if response.status_code == 200:
            print("✅ Webhook responded with status code 200")
            print("Raw response:")
            print("-" * 50)
            print(response.text)
            print("-" * 50)
            
            # Parse the TwiML
            twiml_info = parse_twiml(response.text)
            
            # Display parsed information
            if twiml_info["say_texts"]:
                print(f"Agent replies: \"{twiml_info['say_texts'][0]}\"")
            else:
                print("⚠️ No <Say> element found in response")
                
            if twiml_info["has_record"]:
                print("✅ Response includes <Record> element (conversation continues)")
            elif twiml_info["has_hangup"]:
                print("✅ Response includes <Hangup> element (conversation ends)")
            else:
                print("⚠️ No <Record> or <Hangup> element found in response")
                
            return response.text
        else:
            print(f"❌ Webhook responded with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Test Twilio webhooks locally")
    parser.add_argument("--url", default=os.environ.get("WEBHOOK_BASE_URL", "http://localhost:8000"), 
                        help="Base URL of the application")
    parser.add_argument("--message", default="", 
                        help="Message to send to the transcribe webhook (empty = interactive mode)")
    parser.add_argument("--voice-path", default=os.environ.get("VOICE_WEBHOOK_PATH", "/webhook/voice"), 
                        help="Path for the voice webhook")
    parser.add_argument("--transcribe-path", default=os.environ.get("TRANSCRIBE_WEBHOOK_PATH", "/webhook/transcribe"), 
                        help="Path for the transcribe webhook")
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    voice_url = f"{base_url}{args.voice_path}"
    transcribe_url = f"{base_url}{args.transcribe_path}"
    
    print("=========================================================")
    print("Voice AI Restaurant Agent - Local Webhook Test")
    print("=========================================================")
    
    # Test voice webhook
    print("\n🔍 Testing voice webhook (call initiation)...")
    voice_response, call_sid = test_voice_webhook(voice_url)
    
    if voice_response and call_sid:
        # Use provided message or go to interactive mode if empty
        message = args.message if args.message else None
        
        # Test transcribe webhook
        print("\n🔍 Testing transcribe webhook (message processing)...")
        test_transcribe_webhook(transcribe_url, call_sid, message)

        # Allow for multi-turn conversation in interactive mode
        if not args.message:
            while True:
                continue_chat = input("\nContinue conversation? (y/n): ").lower()
                if continue_chat != 'y':
                    break
                
                next_message = input("Enter next message: ")
                test_transcribe_webhook(transcribe_url, call_sid, next_message)
    
    print("\n=========================================================")
    print("Test completed")
    print("=========================================================")

if __name__ == "__main__":
    main()