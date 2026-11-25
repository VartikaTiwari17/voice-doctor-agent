from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.services.llm_service import FunctionCallParams
import data

check_schema = FunctionSchema(
    name="check_doctor_availability",
    description="Get free slots for a doctor (by name or speciality), optionally for one date.",
    properties={
        "doctor": {"type": "string", "description": "Doctor name or speciality"},
        "date": {"type": "string", "description": "YYYY-MM-DD, optional"},
    },
    required=["doctor"],
)

book_schema = FunctionSchema(
    name="book_appointment",
    description="Book a slot. Call ONLY after the caller confirmed the phone number read back to them.",
    properties={
        "doctor": {"type": "string"},
        "date": {"type": "string", "description": "YYYY-MM-DD"},
        "time": {"type": "string", "description": "HH:MM, 24h"},
        "phone": {"type": "string", "description": "Digits only, as confirmed by caller"},
        "patient_name": {"type": "string"},
    },
    required=["doctor", "date", "time", "phone"],
)

cancel_schema = FunctionSchema(
    name="cancel_appointment",
    description="Cancel the caller's appointment. Call ONLY after phone number is confirmed.",
    properties={"phone": {"type": "string", "description": "Digits only"}},
    required=["phone"],
)

tools = ToolsSchema(standard_tools=[check_schema, book_schema, cancel_schema])


async def check_doctor_availability(params: FunctionCallParams):
    a = params.arguments
    await params.result_callback(data.get_availability(a["doctor"], a.get("date")))

async def book_appointment(params: FunctionCallParams):
    a = params.arguments
    await params.result_callback(
        data.book(a["doctor"], a["date"], a["time"], a["phone"], a.get("patient_name", "")))

async def cancel_appointment(params: FunctionCallParams):
    await params.result_callback(data.cancel(params.arguments["phone"]))