#!/usr/bin/env python
"""
End-to-end testing script for Voice AI Restaurant Agent.

This script conducts end-to-end tests against a deployed instance of the application,
simulating Twilio voice API calls.
"""
import os
import sys
import json
import time
import argparse
import requests
import random
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Test cases for simulating conversations
TEST_CONVERSATIONS = [
    # Menu inquiry flow
    [
        "Hello, what's on your menu?",
        "Do you have any vegetarian options?",
        "Are there any special offers today?",
        "Thanks, that's all I needed"
    ],
    # Reservation flow
    [
        "Hi, I'd like to make a reservation",
        "For tomorrow at 7 PM",
        "There will be 4 people",
        "My name is John Smith",
        "My phone number is 555-123-4567",
        "No special requests, thank you"
    ],
    # Dietary restriction flow
    [
        "Do you have gluten-free options?",
        "What about dairy-free dishes?",
        "Which is your most popular gluten-free dish?",
        "Thank you for the information"
    ]
]

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

def simulate_call(base_url, conversation):
    """Simulate a complete conversation flow."""
    print(f"Simulating conversation with {len(conversation)} turns")
    
    # Generate a unique call SID for this test
    call_sid = f"TEST{uuid.uuid4().hex[:16].upper()}"
    
    # Start the call
    print("\n📞 Initiating call...")
    
    try:
        # Call the voice webhook to start
        response = requests.post(
            f"{base_url}/webhook/voice",
            data={"CallSid": call_sid, "From": "+15551234567", "To": "+15559876543"}
        )
        response.raise_for_status()
        
        # Parse the initial TwiML
        twiml_info = parse_twiml(response.text)
        if twiml_info["say_texts"]:
            print(f"🤖 Agent: {twiml_info['say_texts'][0]}")
        
        # Go through each turn in the conversation
        for i, user_message in enumerate(conversation):
            print(f"\n👤 User: {user_message}")
            
            # Simulate recording URL
            recording_url = f"https://example.com/recordings/{call_sid}/{i}"
            recording_sid = f"RE{uuid.uuid4().hex[:16].upper()}"
            
            # Call the transcribe webhook
            response = requests.post(
                f"{base_url}/webhook/transcribe",
                data={
                    "CallSid": call_sid,
                    "RecordingUrl": recording_url,
                    "RecordingSid": recording_sid,
                    "Transcript": user_message  # For testing, we pass the transcript directly
                }
            )
            response.raise_for_status()
            
            # Parse the TwiML response
            twiml_info = parse_twiml(response.text)
            
            # Display the agent's response
            if twiml_info["say_texts"]:
                print(f"🤖 Agent: {twiml_info['say_texts'][0]}")
            
            # Check if the call has ended
            if twiml_info["has_hangup"]:
                print("📞 Call ended by agent")
                break
            
            # Small delay to simulate real-time conversation
            time.sleep(0.5)
        
        # End the call (send status callback)
        requests.post(
            f"{base_url}/webhook/status",
            data={"CallSid": call_sid, "CallStatus": "completed"}
        )
        
        print("\n✅ Conversation simulation completed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during conversation simulation: {str(e)}")
        return False

def run_tests(base_url, num_tests=1):
    """Run multiple conversation tests."""
    successful = 0
    failed = 0
    
    # Select random conversations for testing
    test_cases = random.choices(TEST_CONVERSATIONS, k=num_tests)
    
    print(f"Running {num_tests} test conversation(s) against {base_url}")
    print("=" * 60)
    
    for i, conversation in enumerate(test_cases):
        print(f"\nTest #{i+1}/{num_tests}")
        print("-" * 40)
        
        if simulate_call(base_url, conversation):
            successful += 1
        else:
            failed += 1
        
        print("-" * 40)
        
        # Add delay between tests
        if i < len(test_cases) - 1:
            time.sleep(2)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Test summary: {successful} successful, {failed} failed")
    
    return failed == 0

def main():
    parser = argparse.ArgumentParser(description="Run end-to-end tests for Voice AI Restaurant Agent")
    parser.add_argument("--url", help="Base URL of the deployed application", default=None)
    parser.add_argument("--tests", type=int, help="Number of test conversations to run", default=1)
    args = parser.parse_args()
    
    # Get base URL
    base_url = args.url
    if not base_url:
        # Try to get ngrok URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            tunnels = response.json()["tunnels"]
            for tunnel in tunnels:
                if tunnel["proto"] == "https":
                    base_url = tunnel["public_url"]
                    break
        except Exception:
            pass
    
    if not base_url:
        print("❌ Could not determine application URL. Please provide it with --url or ensure ngrok is running.")
        sys.exit(1)
    
    # Run tests
    success = run_tests(base_url, args.tests)
    
    if success:
        print("✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()