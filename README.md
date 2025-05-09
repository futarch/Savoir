# Savoir - WhatsApp Knowledge Garden Bot

A WhatsApp bot that helps you create and grow your personal knowledge garden through natural conversations.

## Overview

Savoir is an intelligent WhatsApp bot that transforms your daily conversations into a structured knowledge garden. It helps you capture, organize, and connect information through natural chat interactions, making knowledge management effortless and enjoyable. Share and collaborate on knowledge gardens with friends, colleagues, or the broader community.

## Project Status

⚠️ **Work in Progress**

This project is currently in active development and has several areas that need improvement:

- Not all R2R API calls are working properly
- Some features are incomplete or in development
- The knowledge garden structure needs refinement
- WhatsApp integration requires additional testing
- Performance optimizations are needed
- Documentation needs expansion
- Currently limited to single-user mode (multi-user support coming soon)

We are actively working on these improvements and will update the project regularly. Your feedback and contributions are welcome!

## Technical Architecture

### Message Flow

1. **WhatsApp Integration**
   - Receives messages through WhatsApp Cloud API webhook
   - Validates incoming webhook requests
   - Extracts message content and sender information

2. **OpenAI Assistant Processing**
   - Forwards message to OpenAI Assistant API
   - Assistant processes natural language using GPT-4.1
   - Determines intent and required actions (tools calling)
   - Generates contextual responses

3. **R2RIntegration**
   - Stores and retrieves information
   - Creates connections between related concepts
   - User management

4. **Response Generation**
   - OpenAI Assistant use R2R knowledge
   - Formats response for WhatsApp
   - Sends response back through WhatsApp Cloud API

### Key Components

- **FastAPI Backend**: Handles webhook endpoints and message routing
- **OpenAI Assistant**: Manages conversation context and natural language understanding
- **R2R Service**: Manages knowledge storage and retrieval
- **WhatsApp Cloud API**: Handles message delivery and reception
- **PostgreSQL Database**: Stores user data and conversation history

## Features

- 🤖 WhatsApp Integration: Interact with your knowledge garden through familiar WhatsApp chats
- 🌱 Knowledge Garden Creation: Automatically structure and organize information from conversations
- 🔄 Natural Language Processing: Understand and process information from casual chat messages
- 🔗 Smart Connections: Automatically link related concepts and ideas
- 📚 Knowledge Growth: Learn from interactions to improve organization and suggestions
- 🤝 Garden Sharing: Share your knowledge gardens with others and collaborate on growing them together

## How It Works

1. Chat with Savoir on WhatsApp just like you would with a friend
2. Share ideas, notes, or questions naturally
3. Savoir automatically:
   - Captures important information
   - Organizes it into your knowledge garden
   - Creates connections between related concepts
   - Suggests relevant existing knowledge
4. Access your growing knowledge garden anytime through WhatsApp
5. Share and collaborate on knowledge gardens with others

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- WhatsApp Business API access
- OpenAI API key
- R2R API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/futarch/Savoir.git
cd Savoir
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env
```

5. Configure your environment variables in `.env`:
```
R2R_API_KEY=your_r2r_api_key_here
WHATSAPP_API_KEY=your_whatsapp_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
WHATSAPP_VERIFICATION_TOKEN=your_whatsapp_verification_token_here
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id_here
OPENAI_ASSISTANT_ID=your_openai_assistant_id_here
```

## Documentation & Resources

### WhatsApp Cloud API
- [Getting Started Guide](https://developers.facebook.com/docs/whatsapp/getting-started/signing-up)
- [Sample App Endpoints](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/sample-app-endpoints)
- [Webhook Setup](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started-for-tech-providers)

### OpenAI
- [API Reference](https://platform.openai.com/docs/api-reference/introduction)
- [Assistants API](https://platform.openai.com/docs/api-reference/assistants)

### R2R
- [Documentation](https://r2r-docs.sciphi.ai/documentation)

## Development

The bot is built with:
- FastAPI for the backend framework
- OpenAI for natural language processing
- WhatsApp Business API for messaging
- R2R for AI Retrieval-Augmented Generation (RAG)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT

## Contact

admin@savoir.garden