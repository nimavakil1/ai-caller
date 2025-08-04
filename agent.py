from livekit import agents, rtc
from livekit.agents import AgentSession, AutoSubscribe, WorkerOptions, JobContext
from livekit.plugins import cartesia, deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
import asyncio
import logging

def prewarm(proc: agents.JobProcess):
    """Preload VAD model to avoid initialization delay"""
    proc.userdata["vad"] = silero.VAD.load(
        min_speech_duration=0.05,    # 50ms minimum speech (fastest detection)
        min_silence_duration=0.55,   # 550ms silence threshold (balanced)
        threshold=0.5,               # Optimal sensitivity
        sample_rate=16000,           # Best performance sample rate
        force_cpu=True               # Consistent performance
    )

async def entrypoint(ctx: JobContext):
    # Optimized system prompt for concise responses
    initial_chat_context = openai.ChatContext().append(
        role="system",
        text="You are a voice assistant. Respond concisely in 1-2 sentences. Avoid filler words."
    )
    
    await ctx.connect(
        auto_subscribe=AutoSubscribe.AUDIO_ONLY,
        rtc_config=rtc.RtcConfiguration(
            ice_transport_policy=rtc.IceTransportPolicy.RELAY,  # Force TURN for consistency
            continual_gathering_policy=rtc.ContinualGatheringPolicy.GATHER_CONTINUALLY
        )
    )
    
    participant = await ctx.wait_for_participant()
    
    # Ultra-optimized agent configuration
    agent = agents.VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        
        # Optimized Deepgram STT (Nova-3 recommended)
        stt=deepgram.STT(
            model="nova-3-conversationalai",  # Specialized for voice agents
            language="en-US",                 # Explicit language for speed
            sample_rate=16000,
            endpointing_ms=25,                # Minimal endpointing delay
            interim_results=True,             # Progressive transcription
            punctuate=True,                   # Better turn detection
            smart_format=False,               # Disable for lower latency
            no_delay=True,                    # Minimize processing delays
            filler_words=False,               # Reduce processing overhead
        ),
        
        # Fast LLM configuration
        llm=openai.LLM(
            model="gpt-4o-mini",              # Optimized for speed
            temperature=0.7,
            max_tokens=100,                   # Limit response length
            stream=True                       # Enable streaming
        ),
        
        # Cartesia TTS (faster than ElevenLabs)
        tts=cartesia.TTS(
            model="sonic-turbo",              # 40ms model latency
            voice="794f9389-aac1-45b6-b726-9d9369183238",  # Preset voice ID
            sample_rate=16000,                # Lower bandwidth
            encoding="pcm_s16le",             # Efficient encoding
            speed="fast",                     # Increase speech rate
            language="en"                     # Explicit language
        ),
        
        chat_ctx=initial_chat_context,
        
        # Advanced turn detection
        turn_detection=MultilingualModel(),   # Context-aware detection
        
        # Aggressive timing optimization
        min_endpointing_delay=0.3,            # Reduced from 0.5s default
        max_endpointing_delay=2.0,            # Maximum wait time
        min_interruption_duration=0.3,        # Quick interruption trigger
        min_interruption_words=0,             # Disable word-based delays
        
        # Performance optimizations
        allow_interruptions=True,
        preemptive_generation=True,           # Speculative response generation
        discard_audio_if_uninterruptible=True
    )
    
    agent.start(ctx.room, participant)
    
    # Optional: Immediate greeting with interruption support
    await agent.say("Hello! How can I help you?", allow_interruptions=True)

if __name__ == "__main__":
    # Production worker configuration
    agents.cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        load_threshold=0.75,              # Worker availability threshold
        max_concurrent_jobs=25,           # Optimize for resource usage
        graceful_shutdown_timeout=600,    # Allow conversations to complete
        health_check_port=8081
    ))
