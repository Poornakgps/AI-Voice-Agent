# Voice AI Restaurant Agent

A conversational AI voice agent powered by OpenAI Agent SDK, integrated with Twilio for voice interactions, and deployed on Google Cloud Platform.

## Project Overview

This project implements a restaurant voice assistant that allows customers to:
- Inquire about menu items and pricing
- Check for vegetarian, vegan, and other dietary options
- View current specials and promotions
- Make and manage restaurant reservations
- Get general information about the restaurant

## Completed Components

### ✅ FastAPI Backend Pipeline
- Built the core FastAPI application structure with middleware and routes
- Set up health/status endpoints for monitoring
- Created admin endpoints for system management
- Implemented Twilio webhook handlers for voice interactions

### ✅ Database & Tool Setup Pipeline
- Designed SQLAlchemy schema for restaurant entities
- Implemented ORM models with relationships (menus, reservations, etc.)
- Created the repository pattern for database access
- Built tool functions for menu queries, pricing calculations, and reservation management
- Added mock data generation for testing

### ✅ Agent Building Pipeline
- Implemented the RestaurantAgent class for orchestrating conversations
- Created a flexible prompt management system with Jinja2 templates
- Built conversation state management
- Integrated with OpenAI API (with mock fallbacks for development)
- Implemented voice processing components:
  - TwiML generator for Twilio
  - STT module using OpenAI Whisper API (with mock fallbacks)
  - TTS module using OpenAI TTS API (with mock fallbacks)

### ✅ Deployment Pipeline (Local Testing)
- Created Docker configuration (Dockerfile and docker-compose.yml)
- Set up ngrok integration for exposing local webhooks
- Implemented deployment scripts for local development
- Added environment setup utilities
- Created verification scripts for deployment testing

## Key Files Added

| File | Purpose |
|------|---------|
| `app/core/agent.py` | Main agent implementation with conversation management |
| `app/routes/twilio_webhook.py` | Twilio webhook handlers for voice interactions |
| `app/tools/*.py` | Database tool functions for menu, pricing, and reservations |
| `database/models.py` | SQLAlchemy ORM models for restaurant entities |
| `database/repository.py` | Repository pattern implementation for database access |
| `app/voice/twiml_generator.py` | TwiML response generator for Twilio |
| `app/voice/stt.py` | Speech-to-Text module using OpenAI Whisper API |
| `app/voice/tts.py` | Text-to-Speech module using OpenAI TTS API |
| `infrastructure/local/docker-compose.yml` | Docker Compose configuration for local deployment |
| `infrastructure/local/setup_env.py` | Environment setup script |
| Various test scripts | Scripts for testing database, API, and Twilio integration |

## Setup Instructions

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Ngrok account (for local Twilio webhook testing)
- Twilio account and API credentials (for real voice interaction)
- OpenAI API key (for TTS, STT, and agent functionality)

### Local Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd voice-ai-restaurant-agent
   ```

2. Set up environment variables:
   ```bash
   python infrastructure/local/setup_env.py
   ```
   This will create a `.env` file with necessary configuration. Add your API keys for full functionality.

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python setup_db.py
   ```

5. Deploy locally with Docker:
   ```bash
   bash infrastructure/local/local_deployment.sh
   ```

6. Verify the deployment:
   ```bash
   python infrastructure/local/check_deployment.py
   ```

## Testing Commands

### Database Testing
```bash
# Test database setup and queries
python db_test.py

# Interactive database explorer
python db_explorer.py
```

### Agent Testing
```bash
# Interactive CLI for the agent (uses OpenAI API if key is provided)
python interact_agent.py
```

### Audio API Testing
```bash
# Test the TTS functionality (uses OpenAI TTS API if key is provided)
python test_audio_api.py tts "Welcome to Taste of India"

# Test STT functionality (requires audio URL)
python test_audio_api.py stt "https://example.com/audio.mp3"

# Test complete TTS -> STT pipeline (requires OpenAI API key)
python test_audio_api.py full_loop "Welcome to Taste of India"
```

The full loop test:
- Converts text to speech using the TTS endpoint
- Saves the generated audio to a file
- Uses OpenAI Whisper API to transcribe the audio back to text
- Compares the original text with the transcription

### Twilio Integration Testing
```bash
# Test Twilio credentials (uses real Twilio client if credentials are provided)
python test_twilio_credentials.py

# Test webhooks locally
python test_local_webhook.py --url=http://localhost:8000 --message="What's on your menu?"
```

### End-to-End Testing
```bash
python infrastructure/local/e2e_test.py
```

## API Workflow

The voice interaction follows these steps:

1. **Call Initiation**:
   - Customer calls the Twilio phone number
   - Twilio sends a webhook request to `/webhook/voice`
   - The application generates a welcome TwiML response

2. **Voice Processing**:
   - Customer speaks after the welcome message
   - Twilio records the speech and sends it to `/webhook/transcribe`
   - The STT module converts speech to text using OpenAI Whisper (or mock)

3. **Agent Processing**:
   - The transcribed text is sent to the RestaurantAgent
   - Agent processes the message using OpenAI (or mock)
   - If needed, agent calls database tools to retrieve information
   - Agent generates a response based on the tool results

4. **Response Generation**:
   - TwiML generator creates a response with the agent's message
   - Response is sent back to Twilio
   - Twilio converts text to speech and plays it to the caller

5. **Call Completion**:
   - When call ends, Twilio sends a status callback to `/webhook/status`
   - Application cleans up resources and stores conversation data

## Remaining Tasks

The following components are still pending:

1. **Environment Setup Pipeline (GCP)**:
   - Cloud Run service configuration
   - GCS bucket setup for audio and transcript storage
   - Secret Manager configuration
   - CI/CD pipeline with Cloud Build