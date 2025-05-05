#!/usr/bin/env python
"""
Environment setup helper for Voice AI Restaurant Agent.

This script helps set up the environment variables needed for local deployment.
"""
import os
import sys
import argparse
import secrets
import subprocess
from pathlib import Path

def generate_env_file(env_file_path, overwrite=False):
    """Generate .env file from .env.example with configured values."""
    # Get the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Check if .env file already exists
    if env_file_path.exists() and not overwrite:
        print(f"❌ {env_file_path} already exists. Use --overwrite to replace it.")
        return False
    
    # Check if .env.example exists
    env_example_path = project_root / ".env.example"
    if not env_example_path.exists():
        print(f"❌ {env_example_path} not found.")
        return False
    
    # Read .env.example
    with open(env_example_path, "r") as f:
        env_example = f.read()
    
    # Generate values for empty fields
    env_lines = []
    for line in env_example.splitlines():
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            env_lines.append(line)
            continue
            
        # Handle lines with equals sign
        if "=" in line:
            key, value = line.split("=", 1)
            # Generate values for empty or placeholder fields
            if "dummy" in value.lower() or "your" in value.lower() or not value.strip():
                if key == "OPENAI_API_KEY":
                    value = input("Enter your OpenAI API key (leave empty for mock): ").strip() or "dummy_key_for_local_development"
                elif key == "OPENAIORG_ID":
                    value = input("Enter your OpenAI Organization ID (leave empty if not needed): ").strip() or ""
                elif key == "TWILIO_API_KEY":
                    value = input("Enter your Twilio API Key (leave empty for mock): ").strip() or "dummy_key_for_local_development"
                elif key == "TWILIO_API_SECRET":
                    value = input("Enter your Twilio API Secret (leave empty for mock): ").strip() or "dummy_secret_for_local_development"
                elif key == "NGROK_AUTHTOKEN":
                    value = input("Enter your ngrok auth token (leave empty for basic use): ").strip() or ""
            env_lines.append(f"{key}={value}")
        else:
            # Add lines without equals sign as-is (might be malformed, but preserve them)
            print(f"Warning: Line without '=' found in .env.example: '{line}'")
            env_lines.append(line)
    
    # Write .env file
    with open(env_file_path, "w") as f:
        f.write("\n".join(env_lines))
    
    print(f"✅ Generated {env_file_path}")
    return True

def setup_ngrok():
    """Check and help setup ngrok."""
    try:
        # Check if ngrok is installed
        subprocess.run(["ngrok", "version"], check=True, stdout=subprocess.PIPE)
        print("✅ ngrok is installed")
        
        # Check for ngrok auth token
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                env_content = f.read()
                if "NGROK_AUTHTOKEN=" in env_content and not "NGROK_AUTHTOKEN=\n" in env_content and not "NGROK_AUTHTOKEN=\"\"" in env_content:
                    print("✅ ngrok auth token is configured")
                else:
                    print("⚠️ ngrok auth token is not configured")
                    print("  You can still use ngrok, but with limitations.")
                    print("  To get an auth token, register at https://ngrok.com/")
                    print("  Then add NGROK_AUTHTOKEN=your_token to your .env file")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ngrok is not installed or not in PATH")
        print("  To install ngrok, visit https://ngrok.com/download")
        print("  For Mac users with Homebrew: brew install ngrok")
        print("  For Ubuntu: snap install ngrok")

def check_docker():
    """Check if Docker and Docker Compose are installed."""
    try:
        # Check Docker
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE)
        print("✅ Docker is installed")
        
        # Check Docker Compose
        subprocess.run(["docker-compose", "--version"], check=True, stdout=subprocess.PIPE)
        print("✅ Docker Compose is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker or Docker Compose is not installed or not in PATH")
        print("  To install Docker, visit https://docs.docker.com/get-docker/")
        print("  Docker Compose is usually included with Docker Desktop")
        return False

def create_storage_dirs():
    """Create necessary storage directories."""
    storage_dir = Path("storage")
    audio_dir = storage_dir / "audio"
    transcript_dir = storage_dir / "transcripts"
    
    for directory in [storage_dir, audio_dir, transcript_dir]:
        directory.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    parser = argparse.ArgumentParser(description="Setup environment for Voice AI Restaurant Agent")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .env file")
    args = parser.parse_args()
    
    print("================================================")
    print("Voice AI Restaurant Agent - Environment Setup")
    print("================================================")
    
    # Change to project root (assuming script is in infrastructure/local)
    os.chdir(Path(__file__).parent.parent.parent)
    
    # Generate .env file
    env_file_path = Path(".env")
    generated = generate_env_file(env_file_path, args.overwrite)
    
    if generated:
        # Check other requirements
        print("\nChecking requirements:")
        docker_ok = check_docker()
        setup_ngrok()
        
        # Create storage directories
        print("\nSetting up storage:")
        create_storage_dirs()
        
        # Final instructions
        print("\n================================================")
        if docker_ok:
            print("✅ Environment setup complete!")
            print("To deploy the application, run:")
            print("  ./infrastructure/local/local_deployment.sh")
        else:
            print("⚠️ Environment setup incomplete.")
            print("Please install Docker and Docker Compose, then run this script again.")
        print("================================================")
    
if __name__ == "__main__":
    main()