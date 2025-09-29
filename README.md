# Commotion Interview System

An AI-powered voice interview bot built with Pipecat Flows for conducting structured candidate interviews.

## Overview

This bot conducts automated interviews with the following stages:

1. **Greeting** - Introduces itself as a Commotion HR representative
2. **Name Collection** - Asks for and records the candidate's name
3. **Salary Expectations** - Collects salary expectations in LPA (Lakhs Per Annum)
4. **Motivation Question** - Asks why the candidate wants to join Commotion
5. **Resolution** - Provides positive feedback and next steps
6. **Closing** - Thanks the candidate and ends the interview

### Special Logic

- If salary expectation **> 50 LPA**: Routes to polite rejection
- If salary expectation **≤ 50 LPA**: Continues to motivation question and positive resolution

## Prerequisites

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** package manager

### Required API Keys

You'll need accounts and API keys from:

- [Deepgram](https://console.deepgram.com/signup) - Speech-to-Text
- [OpenRouter](https://openrouter.ai/) - LLM (using Grok-4-Fast)
- [Cartesia](https://play.cartesia.ai/sign-up) - Text-to-Speech

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/sharvil-aaspaas/commotion-pipecat.git
   cd commotion-pipecat
   ```

2. **Configure environment variables**

   Create a `.env` file from the example:

   ```bash
   cp env.example .env
   ```

   Add your API keys to `.env`:

   ```ini
   DEEPGRAM_API_KEY=your_deepgram_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   CARTESIA_API_KEY=your_cartesia_key_here
   ```

3. **Install dependencies**

   ```bash
   uv sync
   ```

## Running the Bot

Start the interview bot:

```bash
uv run bot.py
```

Open **http://localhost:7860** in your browser and click **Connect** to start the interview.

> **Note**: First run may take ~20 seconds as Pipecat downloads required models.

## Technical Details

### Built With

- **[Pipecat](https://github.com/pipecat-ai/pipecat)** - Voice AI framework
- **[Pipecat Flows](https://github.com/pipecat-ai/pipecat-flows)** - Structured conversation flows
- **Deepgram** - Real-time speech recognition
- **OpenRouter (Grok-4-Fast)** - Fast LLM inference
- **Cartesia** - High-quality text-to-speech

### Architecture

The bot uses Pipecat Flows' direct functions pattern for state management and conversation routing. Each interview stage is a separate flow node with:

- Specific prompts optimized for natural voice conversation
- Function handlers for data collection and state management
- Conditional routing based on candidate responses

### References

Built using patterns from:
- [Pipecat Quickstart](https://github.com/pipecat-ai/pipecat/blob/main/examples/quickstart/bot.py)
- [Restaurant Reservation Example](https://github.com/pipecat-ai/pipecat-flows/blob/main/examples/restaurant_reservation.py)
- [Food Ordering Example](https://github.com/pipecat-ai/pipecat-flows/blob/main/examples/food_ordering.py)

## Project Structure

```
.
├── bot.py              # Main bot implementation
├── env.example         # Environment variables template
├── pyproject.toml      # Python dependencies
├── pcc-deploy.toml     # Pipecat Cloud deployment config
└── README.md           # This file
```

## Troubleshooting

- **Microphone not working**: Allow microphone permissions in your browser
- **Connection issues**: Check that port 7860 is available
- **API errors**: Verify all API keys are correctly set in `.env`
- **Slow responses**: First run downloads models; subsequent runs are faster

## License

BSD 2-Clause License - Copyright (c) 2024–2025, Daily
