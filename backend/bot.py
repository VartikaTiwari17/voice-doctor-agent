import os
from datetime import date

import aiohttp

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frameworks.rtvi import RTVIObserver, RTVIProcessor
from pipecat.services.elevenlabs.stt import ElevenLabsSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

import tools as T

SYSTEM_PROMPT = f"""You are Maya, a friendly phone receptionist for a clinic. Today is {date.today().isoformat()}.
You can check doctor availability, book, and cancel appointments.
Rules:
- Keep replies short and natural, this is a phone call. No lists, no markdown.
- Identify the caller ONLY by the phone number they speak. Ask for it.
- Always read the number back digit by digit and get a clear yes before booking or cancelling.
- Never call book_appointment or cancel_appointment before that confirmation.
- Offer at most 3 slots at a time. Say dates like 'tomorrow at 11 AM'.
- After a tool result, tell the caller clearly what happened.
- If a slot is taken or a doctor is not found, offer alternatives.
"""


async def run_bot(webrtc_connection):
    # ElevenLabs STT in Pipecat 1.17 needs an aiohttp session
    async with aiohttp.ClientSession() as session:
        await _run(webrtc_connection, session)


async def _run(webrtc_connection, session):
    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(audio_in_enabled=True, audio_out_enabled=True),
    )

    stt = ElevenLabsSTTService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        aiohttp_session=session,
    )
    tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    settings=ElevenLabsTTSService.Settings(voice=os.getenv("ELEVENLABS_VOICE_ID")),
)
    llm = GoogleLLMService(
    api_key=os.getenv("GOOGLE_API_KEY"),
    settings=GoogleLLMService.Settings(model="gemini-3.5-flash-lite"),
)

    llm.register_function("check_doctor_availability", T.check_doctor_availability)
    llm.register_function("book_appointment", T.book_appointment)
    llm.register_function("cancel_appointment", T.cancel_appointment)

    context = LLMContext(
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
        tools=T.tools,
    )
    pair = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),  # VAD
    )

    rtvi = RTVIProcessor()

    pipeline = Pipeline([
        transport.input(),
        stt,
        rtvi,
        pair.user(),
        llm,
        tts,
        transport.output(),
        pair.assistant(),
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(),
        observers=[RTVIObserver(rtvi)],
    )

    @rtvi.event_handler("on_client_ready")
    async def on_ready(rtvi):
        await rtvi.set_bot_ready()
        context.add_message(
            {"role": "user", "content": "Greet the caller briefly and ask how you can help."}
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_disconnect(transport, client):
        await task.cancel()

    await PipelineRunner(handle_sigint=False).run(task)