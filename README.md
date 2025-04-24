# Savoir - WhatsApp Knowledge Garden Bot

A WhatsApp bot that helps you create and grow your personal knowledge garden through natural conversations.

## Overview

Savoir is an intelligent WhatsApp bot that transforms your daily conversations into a structured knowledge garden. It helps you capture, organize, and connect information through natural chat interactions, making knowledge management effortless and enjoyable. Share and collaborate on knowledge gardens with friends, colleagues, or the broader community.

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