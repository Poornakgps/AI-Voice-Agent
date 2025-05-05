# Voice AI Restaurant Agent - Complete Documentation

## Project Overview

The Voice AI Restaurant Agent is a conversational AI system that handles phone interactions for a restaurant. It allows customers to inquire about the menu, check for dietary options, view specials, make reservations, and get general information about the restaurant. The agent is powered by OpenAI Agent SDK, integrated with Twilio for voice interactions, and deployed on Google Cloud Platform.

## System Architecture

The system follows a clean architecture with these components:

1. **API Layer**: FastAPI endpoints for Twilio integration
2. **Agent Core**: Conversation management and prompt handling
3. **Tools Layer**: Functions for menu, pricing, and reservation operations
4. **Data Layer**: SQLAlchemy models and repositories
5. **Voice Processing**: TwiML, STT, and TTS components
6. **Deployment**: Docker-based containerization with ngrok

## Requirements

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Ngrok account (for local Twilio webhook testing)
- Twilio account and API credentials (optional for real voice interaction)
- OpenAI API key (optional for TTS, STT, and agent functionality)

### Dependencies
All required packages are listed in `requirements.txt` and include:
- fastapi, uvicorn, pydantic
- twilio, openai
- sqlalchemy, alembic
- google-cloud-storage (for production)
- pytest (for testing)
- gtts (for mock TTS when OpenAI API is unavailable)

## Installation and Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd voice-ai-restaurant-agent
   ```

2. **Set up environment variables**:
   ```bash
   python infrastructure/local/setup_env.py
   ```
   This script will:
   - Create a `.env` file based on `.env.example`
   - Prompt for API keys (OpenAI, Twilio, ngrok)
   - Check for Docker and ngrok installations
   - Create necessary storage directories

3. **Initialize the database**:
   ```bash
   python setup_db.py
   ```
   This script creates the SQLite database, schema, and loads mock data including an Indian restaurant menu.

4. **Build and deploy locally with Docker**:
   ```bash
   bash infrastructure/local/local_deployment.py
   ```
   This script:
   - Builds the Docker container
   - Starts the application
   - Launches ngrok to expose local endpoints
   - Displays the ngrok URL for Twilio webhook configuration

5. **Verify the deployment**:
   ```bash
   python infrastructure/local/check_deployment.py
   ```
   This checks if all components are working correctly.

## Project Structure

### Core Components

1. **FastAPI Application (`app/main.py`)**
   - The main application entry point
   - Configures middleware and routes
   - Sets up error handling and request logging

2. **Agent Implementation (`app/core/agent.py`)**
   - Handles conversation state management
   - Integrates with OpenAI API (with mock fallbacks)
   - Processes user messages and executes tools

3. **Database Models (`database/models.py`)**
   - SQLAlchemy ORM models for restaurant entities
   - Includes menu categories, items, ingredients, dietary restrictions, reservations

4. **Tool Functions**
   - Menu query tools (`app/tools/menu_query.py`)
   - Pricing tools (`app/tools/pricing.py`)
   - Reservation tools (`app/tools/reservations.py`)

5. **Voice Processing**
   - TwiML generator (`app/voice/twiml_generator.py`)
   - Speech-to-Text module (`app/voice/stt.py`)
   - Text-to-Speech module (`app/voice/tts.py`)

## API Endpoints

### Twilio Webhook Endpoints

1. **Voice Webhook (`/webhook/voice`, POST)**
   - Handles initial incoming calls
   - Returns a TwiML welcome response with recording instructions
   - Creates a new agent instance for the call

2. **Transcribe Webhook (`/webhook/transcribe`, POST)**
   - Processes recorded user speech
   - Transcribes audio using OpenAI Whisper (or mock)
   - Sends text to agent for processing
   - Returns TwiML with agent's response

3. **Status Webhook (`/webhook/status`, POST)**
   - Handles call status updates from Twilio
   - Cleans up resources when a call ends

4. **Fallback Webhook (`/webhook/fallback`, POST)**
   - Handles errors in Twilio processing
   - Returns a friendly error message to the user

5. **DTMF Webhook (`/webhook/dtmf`, POST)**
   - Processes touch-tone input from the user

### Status and Admin Endpoints

1. **Health Check (`/health`, GET)**
   - Returns application status and version
   - Used for monitoring and deployment verification

2. **Readiness Check (`/readiness`, GET)**
   - Verifies the application is ready to accept requests

3. **Metrics (`/metrics`, GET)**
   - Returns application metrics (uptime, memory, CPU)

4. **Admin Config (`/admin/config`, GET)**
   - Returns application configuration (in debug mode)
   - Used for system administration

5. **Admin Logs (`/admin/logs`, GET)**
   - Returns recent application logs
   - Supports filtering by level and limit

6. **Admin Restart (`/admin/restart`, POST)**
   - Triggers a service restart (mock in dev)

### Testing Endpoints

1. **Test TTS (`/test/tts`, POST)**
   - Tests text-to-speech conversion
   - Returns base64-encoded audio

2. **Test STT (`/test/stt`, POST)**
   - Tests speech-to-text transcription
   - Processes audio from a URL

3. **Test OpenAI (`/test-openai`, GET)**
   - Tests OpenAI API connectivity
   - Verifies API key and settings

4. **Test Twilio (`/test-twilio`, GET)**
   - Tests Twilio API credentials
   - Verifies account access

## Conversation Flow

The voice interaction follows this sequence:

1. **Call Initiation**:
   - Customer calls the Twilio phone number
   - Twilio sends a webhook request to `/webhook/voice`
   - Application generates a welcome TwiML response

2. **Voice Processing**:
   - Customer speaks after the welcome message
   - Twilio records the speech and sends it to `/webhook/transcribe`
   - STT module converts speech to text using OpenAI Whisper (or mock)

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

## Testing Tools

### Database Testing
```bash
# Test database setup and queries
python db_test.py

# Interactive database explorer
python db_explorer.py
```

### Agent Testing
```bash
# Interactive CLI for the agent
python interact_agent.py
```

### Audio API Testing
```bash
# Test TTS functionality
python test_audio_api.py tts "Welcome to Taste of India"

# Test STT functionality
python test_audio_api.py stt "https://example.com/audio.mp3"

# Test complete TTS -> STT pipeline
python test_audio_api.py full_loop "Welcome to Taste of India"
```

### Twilio Integration Testing
```bash
# Test Twilio credentials
python test_twilio_credentials.py

# Test webhooks locally
python test_local_webhook.py --url=http://localhost:8000 --message="What's on your menu?"
```

### End-to-End Testing
```bash
# Simulate complete conversations
python infrastructure/local/e2e_test.py
```

## Local Deployment

### Using Docker Compose

The easiest way to run the application locally is with Docker Compose:

```bash
# Build and start the application
docker-compose -f infrastructure/local/docker-compose.yml up --build -d

# View logs
docker-compose -f infrastructure/local/docker-compose.yml logs -f

# Stop the application
docker-compose -f infrastructure/local/docker-compose.yml down
```

### Using the Deployment Script

For a streamlined experience, use the deployment script:

```bash
bash infrastructure/local/local_deployment.sh
```

This script:
1. Checks for required dependencies
2. Builds and starts the Docker containers
3. Retrieves the ngrok URL
4. Displays instructions for Twilio webhook configuration

### Configuring Twilio

To connect Twilio to your local instance:

1. Create a Twilio account and get a phone number
2. Use the ngrok URL from the deployment script
3. Set the Voice webhook to `{ngrok_url}/webhook/voice`
4. Set the Status webhook to `{ngrok_url}/webhook/status`

You can use `test_twilio_credentials.py` to configure these automatically:

```bash
python test_twilio_credentials.py --configure https://your-ngrok-url.ngrok.io --phone YOUR_PHONE_SID
```

## Development Workflow

The project supports different development modes:

1. **Mock Mode**: No API keys required, uses mock implementations
   - Suitable for backend development and testing
   - Set `USE_REAL_APIS=False` in `.env`

2. **Hybrid Mode**: Only OpenAI API key required
   - Agent uses real OpenAI API, but Twilio interactions are mocked
   - Set `OPENAI_API_KEY` but leave Twilio keys empty

3. **Full Mode**: All API keys required
   - Uses real OpenAI and Twilio APIs
   - Set both `OPENAI_API_KEY` and Twilio credentials

## Database Schema

The database includes these main entities:

1. **MenuCategory**: Restaurant menu categories
2. **MenuItem**: Individual menu items with prices
3. **Ingredient**: Food ingredients (with allergen flags)
4. **DietaryRestriction**: Dietary types (vegetarian, vegan, etc.)
5. **SpecialPricing**: Discounts and special offers
6. **Reservation**: Customer reservations
7. **RestaurantTable**: Physical tables in the restaurant

## Troubleshooting

### Common Issues

1. **TTS/STT not working**: Check OpenAI API key in `.env`
2. **Twilio connection failing**: Verify Twilio credentials and webhook URLs
3. **Database errors**: Run `python setup_db.py` to reinitialize the database
4. **Docker issues**: Check Docker and Docker Compose installation
5. **Ngrok not starting**: Verify ngrok installation and auth token

### Logs and Debugging

- Application logs: Docker container logs
- Database explorer: `python db_explorer.py`
- API testing: Use Swagger UI at `/docs` endpoint
- Webhook testing: `python test_local_webhook.py`

## Additional Information

### Key Features

- **Mocked Services**: Development without paid API keys
- **Comprehensive Testing**: Unit, integration, and e2e tests
- **Realistic Restaurant Scenario**: Complete Indian restaurant data
- **Containerized Deployment**: Easy local testing with Docker
- **Conversation Management**: Multi-turn dialogue capabilities