import asyncio, json
from dotenv import load_dotenv
load_dotenv()

from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
import data
from bot import run_bot

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
connections: dict[str, SmallWebRTCConnection] = {}


@app.post("/api/offer")
async def offer(req: dict, bg: BackgroundTasks):
    pc_id = req.get("pc_id")
    if pc_id and pc_id in connections:
        conn = connections[pc_id]
        await conn.renegotiate(sdp=req["sdp"], type=req["type"],
                               restart_pc=req.get("restart_pc", False))
    else:
        conn = SmallWebRTCConnection()
        await conn.initialize(sdp=req["sdp"], type=req["type"])

        @conn.event_handler("closed")
        async def _closed(c):
            connections.pop(c.pc_id, None)

        bg.add_task(run_bot, conn)
    answer = conn.get_answer()
    connections[answer["pc_id"]] = conn
    return answer


# Browser sends ICE candidates here. Not needed on localhost, so just acknowledge.
@app.patch("/api/offer")
async def ice_patch(req: dict):
    return {"status": "success"}


@app.get("/api/doctors")
def doctors():
    return [{**d, "slots": {day: [t for t, w in ts.items() if w is None]
                            for day, ts in data.SLOTS[d["id"]].items()}}
            for d in data.DOCTORS]


@app.get("/api/appointments")
def appointments():
    return data.APPOINTMENTS


@app.get("/api/events")
async def events():
    q: asyncio.Queue = asyncio.Queue()
    data.subscribers.add(q)

    async def gen():
        try:
            while True:
                yield f"data: {json.dumps(await q.get())}\n\n"
        finally:
            data.subscribers.discard(q)

    return StreamingResponse(gen(), media_type="text/event-stream")