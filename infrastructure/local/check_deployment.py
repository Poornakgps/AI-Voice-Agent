#!/usr/bin/env python
"""
Deployment verification script for Voice AI Restaurant Agent.

This script checks the health of the deployed application and verifies that
all components are working properly.
"""
import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime

def check_health(base_url):
    """Check the health endpoint."""
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        health_data = response.json()
        
        print(f"✅ Health check successful")
        print(f"   Status: {health_data['status']}")
        print(f"   Version: {health_data['version']}")
        print(f"   Environment: {health_data['environment']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def check_metrics(base_url):
    """Check the metrics endpoint."""
    try:
        response = requests.get(f"{base_url}/metrics")
        response.raise_for_status()
        metrics_data = response.json()
        
        print(f"✅ Metrics check successful")
        print(f"   Uptime: {metrics_data['uptime']:.2f} seconds")
        print(f"   Memory usage: {metrics_data['memory_usage']:.2f} MB")
        print(f"   CPU usage: {metrics_data['cpu_usage']:.2f}%")
        return True
    except Exception as e:
        print(f"❌ Metrics check failed: {str(e)}")
        return False

def check_admin_config(base_url):
    """Check the admin config endpoint."""
    try:
        response = requests.get(f"{base_url}/admin/config")
        response.raise_for_status()
        config_data = response.json()
        
        print(f"✅ Admin config check successful")
        print(f"   Found {len(config_data)} configuration items")
        return True
    except Exception as e:
        print(f"❌ Admin config check failed: {str(e)}")
        return False

def check_twilio_endpoints(base_url):
    """Check the Twilio webhook endpoints."""
    try:
        # Try health and readiness endpoints
        fallback_response = requests.post(f"{base_url}/webhook/fallback")
        voice_response = requests.post(f"{base_url}/webhook/voice")
        
        # Check if responses are valid TwiML
        is_valid_twiml = (
            '<?xml' in fallback_response.text and 
            '<Response>' in fallback_response.text and
            '<?xml' in voice_response.text and 
            '<Response>' in voice_response.text
        )
        
        if is_valid_twiml:
            print(f"✅ Twilio webhook endpoints check successful")
            return True
        else:
            print(f"❌ Twilio webhook endpoints returned invalid TwiML")
            return False
    except Exception as e:
        print(f"❌ Twilio webhook endpoints check failed: {str(e)}")
        return False

def get_ngrok_url():
    """Get the ngrok public URL."""
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        response.raise_for_status()
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
        return None
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser(description="Check deployment of Voice AI Restaurant Agent")
    parser.add_argument("--url", help="Base URL of the deployed application", default=None)
    args = parser.parse_args()
    
    # Get base URL (either from arguments or ngrok)
    base_url = args.url
    if not base_url:
        print("No URL provided, trying to get ngrok URL...")
        base_url = get_ngrok_url()
    
    if not base_url:
        print("❌ Could not determine application URL. Please provide it with --url or ensure ngrok is running.")
        sys.exit(1)
    
    print(f"🔍 Checking deployment at {base_url}")
    print("=" * 50)
    
    # Run checks
    health_ok = check_health(base_url)
    metrics_ok = check_metrics(base_url)
    admin_ok = check_admin_config(base_url)
    twilio_ok = check_twilio_endpoints(base_url)
    
    # Overall status
    print("=" * 50)
    if all([health_ok, metrics_ok, admin_ok, twilio_ok]):
        print("✅ All checks passed! Deployment is healthy.")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Please review the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()