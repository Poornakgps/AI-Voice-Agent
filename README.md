## API Workflow

The local API workflow follows these steps:

1. **Call Initiation**:
   - Customer calls the Twilio phone number
   - Twilio sends a webhook request to `/webhook/voice`
   - The application generates a welcome TwiML response

2. **Voice Processing**:
   - Customer speaks after the welcome message
   - Twilio records the speech and sends it to `/webhook/transcribe`
   - The STT module converts speech to text (mocked in development)

3. **Agent Processing**:
   - The transcribed text is sent to the RestaurantAgent
   - Agent adds the message to conversation history
   - Agent processes the message using OpenAI (mocked in development)
   - If needed, agent calls database tools to retrieve information
   - Agent generates a response based on the tool results

4. **Response Generation**:
   - TwiML generator creates a response with the agent's message
   - Response is sent back to Twilio
   - Twilio converts text to speech and plays it to the caller
   - Conversation continues with more recordings or ends with a goodbye

5. **Call Completion**:
   - When call ends, Twilio sends a status callback to `/webhook/status`
   - Application cleans up resources and stores conversation data

This cycle repeats for multi-turn conversations, maintaining state throughout the call.## Development Pipelines

The project has been developed through several implementation pipelines, each focusing on different aspects of the system:

### ✅ FastAPI Backend Pipeline
- Built the core FastAPI application structure with middleware and routes
- Set up health/status endpoints for monitoring
- Created admin endpoints for system management
- Implemented Twilio webhook handlers for voice interactions
- Added testing infrastructure for the API endpoints

### ✅ Database & Tool Setup Pipeline
- Designed SQLAlchemy schema for restaurant entities
- Implemented ORM models with relationships (menus, reservations, etc.)
- Created the repository pattern for database access
- Built tool functions for menu queries, pricing calculations, and reservation management
- Added mock data generation for testing
- Developed comprehensive unit tests for models and tools

### ✅ Agent Building Pipeline with Mocks
- Implemented the RestaurantAgent class for orchestrating conversations
- Created a flexible prompt management system with Jinja2 templates
- Built conversation state management
- Developed a mock OpenAI client for testing without API keys
- Integrated the agent with database tools
- Implemented voice processing components:
  - TwiML generator for Twilio responses
  - STT module (Speech-to-Text) with mocks
  - TTS module (Text-to-Speech) with mocks

### ✅ Deployment Pipeline (Local Testing)
- Created Docker configuration (Dockerfile and docker-compose.yml)
- Set up ngrok integration for exposing local webhooks
- Implemented deployment scripts for local development
- Added environment setup utilities
- Created verification scripts for deployment testing
- Developed end-to-end testing for conversation simulation

### ⬜ Environment Setup Pipeline (Partial)
- This pipeline is not yet complete and would include:
  - Finalizing cloud infrastructure setup for GCP
  - Setting up Cloud Run configuration
  - Configuring monitoring and alerts
  - Implementing CI/CD workflows for production deployment# AI-Voice-Agent

A conversational AI voice agent powered by OpenAI Agent SDK, integrated with Twilio for voice interactions, and deployed on Google Cloud Platform.

## Project Overview

This project creates a restaurant voice assistant that allows customers to:
- Inquire about menu items and pricing
- Check for vegetarian, vegan, and other dietary options
- View current specials and promotions
- Make and manage restaurant reservations
- Get general information about the restaurant

The system uses Twilio to handle phone calls, converts speech to text, processes requests with the OpenAI Agent SDK, and responds with natural voice interactions.

## Current Functionality

The following functionality has been implemented:

### FastAPI Backend
- Complete REST API with health and monitoring endpoints
- Admin endpoints for system management
- Twilio webhook handlers for voice interactions
- Middleware for request logging and error handling

### Database & Tools
- SQLAlchemy ORM models for restaurant entities (menus, reservations, etc.)
- Repository pattern implementation for database access
- Tool functions for menu queries, pricing calculations, and reservation management
- Comprehensive mock data for an Indian restaurant

### Agent Components
- RestaurantAgent class for conversation orchestration
- Flexible prompt management with Jinja2 templates
- Mock OpenAI client for development without API keys
- Integration between agent and database tools

### Voice Processing
- TwiML generator for Twilio responses
- Speech-to-Text module with mock implementation
- Text-to-Speech module with mock implementation

### Deployment
- Docker configuration for containerization
- Docker Compose setup for local development
- Ngrok integration for exposing local webhooks
- Environment setup utilities

## Remaining Tasks

The following tasks are still pending:

1. **GCP Environment Setup**:
   - Cloud Run service configuration
   - GCS bucket setup for audio and transcript storage
   - Secret Manager configuration
   - CI/CD pipeline with Cloud Build

2. **Storage Implementation**:
   - `app/storage/audio.py` - Implement audio file storage in GCS
   - `app/storage/transcript.py` - Implement transcript storage in GCS

3. **Documentation**:
   - Complete `docs/API.md` with API endpoint documentation
   - Complete `docs/ARCHITECTURE.md` with system architecture diagrams
   - Complete `docs/DEPLOYMENT.md` with deployment instructions
   - Complete `docs/README.md` with project overview
   - Complete `docs/TESTING.md` with testing procedures

4. **Integration with Real APIs**:
   - Replace mock OpenAI client with actual implementation
   - Replace mock TTS/STT with actual Google Cloud services

## Setup Instructions

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Ngrok account (for local Twilio webhook testing)
- Twilio account (optional for full testing)
- OpenAI API key (optional for development)

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
   This will create a `.env` file with all necessary configuration.

3. Deploy the application locally:
   ```bash
   bash infrastructure/local/local_deployment.sh
   ```
   This will build and start the Docker containers.

4. Verify the deployment:
   ```bash
   python infrastructure/local/check_deployment.py
   ```

### Twilio Configuration (Optional)

If you want to test with actual phone calls:

1. Create a Twilio account and purchase a phone number
2. Set up your Twilio number to point to your ngrok URL:
   - Voice Webhook: `https://<your-ngrok-url>/webhook/voice`
   - Status Callback URL: `https://<your-ngrok-url>/webhook/status`

3. Update your `.env` file with your Twilio credentials

## API Workflow

The local API workflow follows these steps:

1. **Call Initiation**:
   - Customer calls the Twilio phone number
   - Twilio sends a webhook request to `/webhook/voice`
   - The application generates a welcome TwiML response

2. **Voice Processing**:
   - Customer speaks after the welcome message
   - Twilio records the speech and sends it to `/webhook/transcribe`
   - The STT module converts speech to text (mocked in development)

3. **Agent Processing**:
   - The transcribed text is sent to the RestaurantAgent
   - Agent adds the message to conversation history
   - Agent processes the message using OpenAI (mocked in development)
   - If needed, agent calls database tools to retrieve information
   - Agent generates a response based on the tool results

4. **Response Generation**:
   - TwiML generator creates a response with the agent's message
   - Response is sent back to Twilio
   - Twilio converts text to speech and plays it to the caller
   - Conversation continues with more recordings or ends with a goodbye

5. **Call Completion**:
   - When call ends, Twilio sends a status callback to `/webhook/status`
   - Application cleans up resources and stores conversation data

This cycle repeats for multi-turn conversations, maintaining state throughout the call.

## Testing the Application

### Manual Testing with CLI Tools

1. Run the database explorer to interact with the restaurant database:
   ```bash
   python db_explorer.py
   ```

2. Test the agent manually:
   ```bash
   python test_agent_manually.py
   ```

3. Test the database with sample queries:
   ```bash
   python db_test.py
   ```

### Automated Testing

1. Run unit tests:
   ```bash
   pytest tests/unit/
   ```

2. Run integration tests:
   ```bash
   pytest tests/integration/
   ```

3. Run end-to-end tests:
   ```bash
   python infrastructure/local/e2e_test.py
   ```