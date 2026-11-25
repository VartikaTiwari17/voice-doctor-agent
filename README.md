# Clinic Line: Voice AI Doctor Appointment Assistant

A voice agent (Maya) that checks doctor availability, books and cancels
appointments over a browser call. The caller is identified only by the
phone number they speak. A dashboard shows the live transcript, doctors,
slots and appointments.

## Stack
- Voice pipeline: Pipecat 1.17.0 (Python), SmallWebRTC transport
- VAD: Silero VAD (+ Pipecat smart-turn)
- STT / TTS: ElevenLabs
- LLM: Google Gemini (`gemini-3.5-flash-lite`)
- Backend: FastAPI (REST + SSE for live dashboard updates)
- Frontend: React + Vite

## Run

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # then fill in the 3 keys
python -m uvicorn server:app --host 127.0.0.1 --port 7860
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 and press Call (allow the microphone).

## Tools (function calling)
- `check_doctor_availability`
- `book_appointment`
- `cancel_appointment`

The agent reads the phone number back and waits for a "yes" before booking
or cancelling. Phone numbers must be 10 digits (validated in the tool).

## Notes
- Data is in-memory mock data and resets when the server restarts.
- One appointment per phone number.