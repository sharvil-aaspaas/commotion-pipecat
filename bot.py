#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#


import os
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openrouter.llm import OpenRouterLLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams

from pipecat_flows import FlowArgs, FlowManager, FlowResult, FlowsFunctionSchema, NodeConfig

load_dotenv(override=True)

# Transport configuration
transport_params = {
    "daily": lambda: DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
    ),
    "webrtc": lambda: TransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
    ),
}


# Result types for structured data
class NameResult(FlowResult):
    name: str
    status: str

class SalaryResult(FlowResult):
    salary: float
    status: str
    too_high: bool

class MotivationResult(FlowResult):
    motivation: str
    status: str

# Function handlers
async def collect_name(args: FlowArgs, flow_manager: FlowManager) -> tuple[NameResult, NodeConfig]:
    """Handler for name collection."""
    name = str(args["name"]).strip()
    
    # Store in flow state
    flow_manager.state["name"] = name
    
    result = NameResult(name=name, status="success")
    logger.info(f"Collected name: {name}")
    return result, create_salary_node()

async def collect_salary(args: FlowArgs, flow_manager: FlowManager) -> tuple[SalaryResult, NodeConfig]:
    """Handler for salary expectation collection."""
    salary = float(args["salary"])
    
    # Store in flow state
    flow_manager.state["salary_expectation"] = salary
    
    too_high = salary > 50
    result = SalaryResult(salary=salary, status="success", too_high=too_high)
    
    if too_high:
        logger.info(f"Salary too high: {salary} LPA - going to rejection")
        return result, create_rejection_node()
    else:
        logger.info(f"Salary acceptable: {salary} LPA - continuing to motivation")
        return result, create_motivation_node()

async def collect_motivation(args: FlowArgs, flow_manager: FlowManager) -> tuple[MotivationResult, NodeConfig]:
    """Handler for motivation collection."""
    motivation = str(args["motivation"]).strip()
    
    # Store in flow state
    flow_manager.state["motivation"] = motivation
    
    result = MotivationResult(motivation=motivation, status="success")
    logger.info(f"Collected motivation: {motivation[:50]}...")
    return result, create_resolution_node()

async def end_interview(args: FlowArgs, flow_manager: FlowManager) -> None:
    """Handler to complete the interview."""
    logger.info("Interview completed")
    # No transition needed - the post_action will end the conversation


# Node creation functions
def create_initial_node() -> NodeConfig:
    """Create the initial greeting node."""
    
    collect_name_func = FlowsFunctionSchema(
        name="collect_name",
        handler=collect_name,
        description="Save the candidate's full name to state and move to salary discussion.",
        properties={
            "name": {
                "type": "string",
                "description": "The candidate's full name",
            }
        },
        required=["name"],
    )
    
    return NodeConfig(
        name="initial",
        role_messages=[
            {
                "role": "system",
                "content": "You're an HR interviewer at Commotion, a tech company. Speak naturally like you're having a real conversation—warm but professional. Keep your responses short (1-2 sentences max). Never use emojis, special characters, or markdown since this is voice. Always call the available function once you have the information needed.",
            }
        ],
        task_messages=[
            {
                "role": "user",
                "content": "[System] : Start with a friendly greeting. Say you're from Commotion's HR team and you'll be conducting a quick interview today. Ask for their full name. Once they tell you their name, immediately call collect_name with it.",
            }
        ],
        functions=[collect_name_func],
    )

def create_salary_node() -> NodeConfig:
    """Create salary expectation collection node."""
    
    collect_salary_func = FlowsFunctionSchema(
        name="collect_salary",
        handler=collect_salary,
        description="Save salary expectation in LPA. If over 50 LPA, route to rejection; otherwise continue to motivation question.",
        properties={
            "salary": {
                "type": "number",
                "description": "Salary expectation in LPA (Lakhs Per Annum)",
                "minimum": 1,
                "maximum": 200,
            }
        },
        required=["salary"],
    )
    
    return NodeConfig(
        name="salary_collection",
        task_messages=[
            {
                "role": "user",
                "content": "[System] : Thank them briefly for sharing their name. Then ask what salary they're expecting in LPA. Make it clear you need a number in Lakhs Per Annum. Once they give you a number, call collect_salary immediately.",
            }
        ],
        functions=[collect_salary_func],
        respond_immediately=True,
    )

def create_motivation_node() -> NodeConfig:
    """Create motivation question node."""
    
    collect_motivation_func = FlowsFunctionSchema(
        name="collect_motivation",
        handler=collect_motivation,
        description="Save the candidate's motivation for joining Commotion and proceed to positive resolution.",
        properties={
            "motivation": {
                "type": "string",
                "description": "The candidate's motivation for joining Commotion",
            }
        },
        required=["motivation"],
    )
    
    return NodeConfig(
        name="motivation_collection",
        task_messages=[
            {
                "role": "user",
                "content": "[System] : Acknowledge their salary expectation briefly. Then ask why they specifically want to join Commotion—what draws them to the company? Listen to their full answer, then call collect_motivation with what they said.",
            }
        ],
        functions=[collect_motivation_func],
        respond_immediately=True,
    )

def create_resolution_node() -> NodeConfig:
    """Create resolution node for successful candidates."""
    
    end_interview_func = FlowsFunctionSchema(
        name="end_interview",
        handler=end_interview,
        description="Complete the interview process.",
        properties={},
        required=[],
    )
    
    return NodeConfig(
        name="resolution",
        task_messages=[
            {
                "role": "user",
                "content": "[System] : Thank them for taking the time to interview. Say something positive about their motivation or background. Let them know the HR team will review their profile and reach out within 2-3 business days with next steps. Then call end_interview.",
            }
        ],
        functions=[end_interview_func],
        respond_immediately=True,
        post_actions=[{"type": "end_conversation"}],
    )

def create_rejection_node() -> NodeConfig:
    """Create rejection node for high salary expectations."""
    
    end_interview_func = FlowsFunctionSchema(
        name="end_interview",
        handler=end_interview,
        description="Complete the interview process.",
        properties={},
        required=[],
    )
    
    return NodeConfig(
        name="rejection",
        task_messages=[
            {
                "role": "user",
                "content": "[System] : Thank them for their interest in Commotion. Gently explain that their salary expectation is higher than what the role currently offers. Keep it respectful—mention you appreciate their time and wish them success in finding the right opportunity. Then call end_interview.",
            }
        ],
        functions=[end_interview_func],
        respond_immediately=True,
        post_actions=[{"type": "end_conversation"}],
    )


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    """Run the Commotion interview bot."""
    logger.info("Starting Commotion Interview Bot")

    # Validate all required API keys
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    cartesia_key = os.getenv("CARTESIA_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not deepgram_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable is required")
    if not cartesia_key:
        raise ValueError("CARTESIA_API_KEY environment variable is required")
    if not openrouter_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")

    stt = DeepgramSTTService(api_key=deepgram_key)
    
    tts = CartesiaTTSService(
        api_key=cartesia_key,
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Reading Lady - professional voice
    )
    logger.info("✅ Using Cartesia TTS with fastest configuration (sonic-2 model)")
    
    llm = OpenRouterLLMService(
        api_key=openrouter_key, 
        model="x-ai/grok-4-fast:free"
    )

    context = LLMContext()
    context_aggregator = LLMContextAggregatorPair(context)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            context_aggregator.user(),
            llm,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline, 
        params=PipelineParams(allow_interruptions=True)
    )

    # Initialize flow manager with all required components
    flow_manager = FlowManager(
        task=task,
        llm=llm,
        context_aggregator=context_aggregator,
        transport=transport,
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        # Start the conversation with the initial node
        await flow_manager.initialize(create_initial_node())

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point compatible with Pipecat Cloud."""
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
