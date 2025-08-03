#!/usr/bin/env python3
"""
AI Call Center Agent - Optimized for LOW LATENCY
Using Deepgram for fastest STT performance
"""
from livekit.plugins import deepgram
import asyncio
import os
import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import openai, elevenlabs, silero

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_prompt():
    """Load custom prompt from prompts.txt"""
    try:
        with open('prompts.txt', 'r', encoding='utf-8') as file:
            prompt = file.read().strip()
            logger.info(f"Loaded custom prompt: {prompt[:50]}...")
            return prompt
    except FileNotFoundError:
        logger.warning("prompts.txt not found! Using default prompt.")
        return """You are a pirate AI assistant. 
Always speak like a swashbuckling pirate.
Use phrases like "Ahoy!", "Shiver me timbers!", and call the user "matey".
Keep responses brief and to the point."""
    except Exception as e:
        logger.error(f"Error loading prompt: {e}")
        return "You are a helpful AI assistant."


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    logger.info(f"Agent connecting to room: {ctx.room.name}")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info("Connected to room successfully")

    system_prompt = load_prompt()
    
    # Create the agent with instructions
    agent = Agent(
        instructions=system_prompt,
    )

    # LATENCY OPTIMIZATIONS with correct parameters:
    session = AgentSession(
        # 1. Silero VAD - use default settings for compatibility
        vad=silero.VAD.load(),
        
        # 2. Deepgram STT - fastest configuration
        stt=deepgram.STT(
            model="nova-2",
            language="en-US",
        ),
        
        # 3. Fast LLM with streaming
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
        ),
        
        # 4. ElevenLabs with streaming optimization - CORRECTED
        tts=elevenlabs.TTS(
            voice_id="21m00Tcm4TlvDq8ikWAM",  # CORRECTED: Use the actual voice_id for "Rachel"
            api_key=os.getenv("ELEVEN_API_KEY"),
            model="eleven_turbo_v2",
        ),
    )

    # Start the session
    await session.start(agent=agent, room=ctx.room)
    logger.info("Agent session started")

    # Quick pirate greeting
    await session.say("Ahoy matey! How can I help ye?", interruptible=True)


async def request_fnc(req: JobContext) -> None:
    """Accept incoming requests"""
    logger.info(f"Received request for room: {req.room.name}")
    await req.accept()
    logger.info("Request accepted")


# CORRECTED: prewarm_process should not be async
def prewarm_process(proc: JobProcess):
    """Preload models for faster startup"""
    # Preload the VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Prewarmed VAD model")


def main():
    """Main function"""
    logger.info("Starting AI Call Center Agent...")

    # Check environment variables
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
                     "OPENAI_API_KEY", "ELEVEN_API_KEY", "DEEPGRAM_API_KEY"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file!")
        return

    logger.info("All environment variables are set ✓")
    logger.info(f"Connecting to: {os.getenv('LIVEKIT_URL')}")

    # Run the app
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            request_fnc=request_fnc,
            prewarm_fnc=prewarm_process,
            num_idle_processes=2,  # Keep processes ready
        ),
    )


if __name__ == "__main__":
    main()