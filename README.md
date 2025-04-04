# OpenAIDY - LLM Chat Application

A simple chat application that supports multiple LLM providers.

## Features

- Support for multiple LLM providers:
  - OpenAI (GPT models)
  - Google Gemini
  - DeepSeek
  - Ollama (local models)
- Configurable via environment variables
- Simple chat interface

## Setup

### Backend

1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

3. Edit the `.env` file with your LLM provider details:

```
# For OpenAI
LLM_API_PROVIDER=openai
LLM_API_KEY=your_openai_api_key
LLM_MODEL=gpt-3.5-turbo

# For Google Gemini
# LLM_API_PROVIDER=google-genai
# LLM_API_KEY=your_google_api_key
# LLM_MODEL=gemini-pro

# For DeepSeek
# LLM_API_PROVIDER=deepseek
# LLM_API_KEY=your_deepseek_api_key
# LLM_MODEL=deepseek-chat
# LLM_API_URL=https://api.deepseek.com/v1

# For Ollama (local)
# LLM_API_PROVIDER=ollama
# LLM_API_KEY=  # Can be empty for local Ollama
# LLM_MODEL=llama2
# LLM_API_URL=http://localhost:11434/v1
```

4. Start the backend server:

```bash
python main.py
```

### Frontend

1. Install dependencies:

```bash
cd frontend
bun install
```

2. Start the development server:

```bash
bun run dev
```

3. Open your browser and navigate to the URL shown in the terminal (usually http://localhost:5173)

## Architecture

The application is built with:

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite

### LLM Provider Architecture

The backend uses a modular architecture for LLM providers:

- `LLMProvider` - Abstract base class that defines the interface for all providers
- Provider implementations:
  - `OpenAIProvider` - For OpenAI, DeepSeek, and Ollama (OpenAI-compatible API)
  - `GoogleProvider` - For Google Gemini

The factory pattern is used to create the appropriate provider based on configuration.

## Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| LLM_API_PROVIDER | The LLM provider to use | Yes | openai, google-genai, deepseek, ollama |
| LLM_API_KEY | API key for the provider | Yes | sk-... |
| LLM_MODEL | Model name to use | Yes | gpt-3.5-turbo, gemini-pro |
| LLM_API_URL | Base URL for the API (required for DeepSeek and Ollama) | For some providers | http://localhost:11434/v1 |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
