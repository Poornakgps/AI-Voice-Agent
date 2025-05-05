#!/usr/bin/env python
"""
Updated Twilio credentials testing script for Voice AI Restaurant Agent.

This script validates the Twilio API credentials and explores the Twilio account
without making actual phone calls.
"""
import os
import sys
import argparse
import json
from datetime import datetime
from dotenv import load_dotenv

# Try to load .env file
if os.path.exists(".env"):
    load_dotenv()

# Check for required environment variables
TWILIO_API_KEY = os.environ.get("TWILIO_API_KEY", "")
TWILIO_API_SECRET = os.environ.get("TWILIO_API_SECRET", "")
TWILIO_SID_KEY = os.environ.get("TWILIO_SID_KEY", "")  # Account SID

def validate_credentials():
    """Validate that the Twilio credentials are properly set."""
    missing = []
    if not TWILIO_API_KEY:
        missing.append("TWILIO_API_KEY")
    if not TWILIO_API_SECRET:
        missing.append("TWILIO_API_SECRET")
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please set these in your .env file or directly in your environment")
        return False
    
    return True

def test_twilio_client():
    """Test creating a Twilio client with the credentials."""
    try:
        from twilio.rest import Client
        
        # Create client with API key authentication
        if TWILIO_SID_KEY:
            # If we have an account SID, use that with the API key/secret
            client = Client(TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_SID_KEY)
        else:
            # Otherwise just use the API key/secret
            client = Client(TWILIO_API_KEY, TWILIO_API_SECRET)
        
        print("✅ Successfully created Twilio client")
        return client
    except ImportError:
        print("❌ Failed to import the Twilio package")
        print("Please install it with: pip install twilio")
        return None
    except Exception as e:
        print(f"❌ Failed to create Twilio client: {str(e)}")
        return None

def explore_phone_numbers(client):
    """Explore the phone numbers in the Twilio account."""
    if not client:
        return
    
    print("\n📞 Phone Numbers:")
    try:
        # List phone numbers
        incoming_numbers = client.incoming_phone_numbers.list()
        if incoming_numbers:
            for number in incoming_numbers:
                print(f"Phone Number: {number.phone_number}")
                print(f"  Friendly Name: {number.friendly_name}")
                print(f"  SID: {number.sid}")
                
                # Print URLs if they exist
                if hasattr(number, 'voice_url') and number.voice_url:
                    print(f"  Voice URL: {number.voice_url}")
                if hasattr(number, 'sms_url') and number.sms_url:
                    print(f"  SMS URL: {number.sms_url}")
                
                # Print other webhook URLs if they exist
                attrs_to_check = [
                    'status_callback', 'voice_fallback_url', 
                    'sms_fallback_url', 'voice_status_callback_url'
                ]
                
                for attr in attrs_to_check:
                    if hasattr(number, attr) and getattr(number, attr):
                        print(f"  {attr.replace('_', ' ').title()}: {getattr(number, attr)}")
                
                print()
        else:
            print("No phone numbers found in this account")
    except Exception as e:
        print(f"❌ Error retrieving phone numbers: {str(e)}")

def check_webhook_url(number, attribute):
    """Safely check for webhook URL attributes that might not exist."""
    if hasattr(number, attribute):
        return getattr(number, attribute)
    return None

def explore_webhook_settings(client):
    """Explore the webhook settings for phone numbers."""
    if not client:
        return
    
    print("\n🔄 Webhook Settings Check:")
    try:
        # List phone numbers
        incoming_numbers = client.incoming_phone_numbers.list()
        if not incoming_numbers:
            print("No phone numbers found to check webhook settings")
            return
            
        for number in incoming_numbers:
            print(f"Phone Number: {number.phone_number}")
            
            # Check voice URL
            voice_url = check_webhook_url(number, 'voice_url')
            if voice_url:
                print(f"  ✅ Voice URL: {voice_url}")
            else:
                print("  ❌ No Voice URL configured")
            
            # Check voice method
            voice_method = check_webhook_url(number, 'voice_method')
            if voice_method:
                print(f"  ✅ Voice Method: {voice_method}")
            
            # Check status callback
            status_callback = check_webhook_url(number, 'status_callback')
            if status_callback:
                print(f"  ✅ Status Callback: {status_callback}")
            else:
                print("  ⚠️ No Status Callback configured")
            
            # Check status callback method
            status_callback_method = check_webhook_url(number, 'status_callback_method')
            if status_callback_method:
                print(f"  ✅ Status Callback Method: {status_callback_method}")
            
            print()
            
    except Exception as e:
        print(f"❌ Error checking webhook settings: {str(e)}")

def configure_webhook(client, phone_number_sid, base_url):
    """Configure webhook URLs for a phone number."""
    try:
        # Update the phone number with webhook URLs
        update_params = {
            'voice_url': f"{base_url}/webhook/voice",
            'voice_method': 'POST',
            'status_callback': f"{base_url}/webhook/status",
            'status_callback_method': 'POST'
        }
        
        phone_number = client.incoming_phone_numbers(phone_number_sid).update(**update_params)
        
        print(f"✅ Successfully configured webhooks for {phone_number.phone_number}")
        
        # Print updated webhook URLs
        if hasattr(phone_number, 'voice_url'):
            print(f"  Voice URL: {phone_number.voice_url}")
        if hasattr(phone_number, 'status_callback'):
            print(f"  Status Callback: {phone_number.status_callback}")
            
        return True
    except Exception as e:
        print(f"❌ Error configuring webhooks: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Twilio credentials and explore account")
    parser.add_argument("--configure", help="Configure webhook URLs with this base URL (e.g., https://example.ngrok.io)")
    parser.add_argument("--phone", help="Phone number SID to configure (required if --configure is used)")
    args = parser.parse_args()
    
    print("=========================================================")
    print("Voice AI Restaurant Agent - Twilio Credentials Test")
    print("=========================================================")
    
    # Validate credentials
    if not validate_credentials():
        return
    
    # Test creating a client
    client = test_twilio_client()
    if not client:
        return
    
    # Explore the phone numbers
    explore_phone_numbers(client)
    
    # Check webhook settings
    explore_webhook_settings(client)
    
    # Configure webhook if requested
    if args.configure:
        if not args.phone:
            print("❌ You must specify a phone number SID with --phone when using --configure")
            return
        
        configure_webhook(client, args.phone, args.configure)
    
    print("\n=========================================================")
    print("Test completed")
    print("=========================================================")

if __name__ == "__main__":
    main()