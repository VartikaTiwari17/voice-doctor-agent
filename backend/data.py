import asyncio, uuid
from datetime import date, timedelta

DOCTORS = [
    {"id": "d1", "name": "Dr. Ananya Rao",  "speciality": "Cardiologist"},
    {"id": "d2", "name": "Dr. Rohan Mehta", "speciality": "Dermatologist"},
    {"id": "d3", "name": "Dr. Sana Khan",   "speciality": "General Physician"},
]

TIMES = ["10:00", "11:00", "12:00", "15:00", "16:00"]
DAYS = [(date.today() + timedelta(days=i)).isoformat() for i in range(1, 4)]

# SLOTS[doctor_id][date][time] = phone number or None
SLOTS = {d["id"]: {day: {t: None for t in TIMES} for day in DAYS} for d in DOCTORS}
APPOINTMENTS = []
subscribers: set[asyncio.Queue] = set()


def publish(event: dict):
    for q in subscribers:
        q.put_nowait(event)


def find_doctor(query: str):
    q = query.lower()
    for d in DOCTORS:
        if q in d["name"].lower() or q in d["speciality"].lower():
            return d
    return None


def get_availability(doctor_query: str, day: str | None = None):
    doc = find_doctor(doctor_query)
    if not doc:
        return {"error": "Doctor not found", "doctors": [d["name"] for d in DOCTORS]}
    out = {}
    for d, times in SLOTS[doc["id"]].items():
        if day and d != day:
            continue
        free = [t for t, who in times.items() if who is None]
        if free:
            out[d] = free
    return {"doctor": doc["name"], "speciality": doc["speciality"], "available": out}


def book(doctor_query, day, time, phone, patient_name=""):
    doc = find_doctor(doctor_query)
    if not doc:
        return {"success": False, "error": "Doctor not found"}
    if any(a["phone"] == phone for a in APPOINTMENTS):
        return {"success": False, "error": "This number already has an appointment. Cancel it first."}
    slot = SLOTS[doc["id"]].get(day, {})
    if time not in slot:
        return {"success": False, "error": "Invalid slot"}
    if slot[time] is not None:
        return {"success": False, "error": "Slot already taken"}
    slot[time] = phone
    appt = {"id": str(uuid.uuid4())[:8], "doctor": doc["name"], "doctor_id": doc["id"],
            "date": day, "time": time, "phone": phone, "patient": patient_name}
    APPOINTMENTS.append(appt)
    publish({"type": "booked", "appointment": appt})
    return {"success": True, "appointment": appt}


def cancel(phone):
    for a in APPOINTMENTS:
        if a["phone"] == phone:
            APPOINTMENTS.remove(a)
            SLOTS[a["doctor_id"]][a["date"]][a["time"]] = None
            publish({"type": "cancelled", "appointment": a})
            return {"success": True, "cancelled": a}
    return {"success": False, "error": "No appointment found for this number"}