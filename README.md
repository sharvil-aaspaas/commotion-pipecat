Commotion Interview System using Pipecat Flows.

Implemented a structured interview system for Commotion with the following stages:
1. Greeting - Assistant introduces itself as Commotion interviewer
2. Name Collection - Asks for candidate's name
3. Salary Expectations - Asks for salary expectations in LPA
4. Motivation Question - Asks why they want to join Commotion
5. Resolution - Provides feedback and next steps
6. Closing - Thanks candidate and ends interview

Special Logic: If salary expectation > 50 LPA, directly goes to rejection closing.

I have built it on top of the following Pipecat references :
https://github.com/pipecat-ai/pipecat/blob/main/examples/quickstart/bot.py
https://github.com/pipecat-ai/pipecat-flows/blob/main/examples/restaurant_reservation.py
https://github.com/pipecat-ai/pipecat-flows/blob/main/examples/food_ordering.py

Prerequisites : uv

Run the bot using:
   uv sync
   uv run bot.py

Required env :
DEEPGRAM_API_KEY=
OPENROUTER_API_KEY=
CARTESIA_API_KEY=
