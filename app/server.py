"""Web interface (FastAPI) for the Cinema Ticket Booking Tool.

Run from the project root:
    python3 -m uvicorn app.server:app --reload
Then open http://127.0.0.1:8000  (API docs: http://127.0.0.1:8000/docs)
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.booking import BookingSystem

STATIC_DIR = Path(__file__).parent / "static"
DATA_FILE = os.environ.get("CINEMA_DATA", "bookings.json")

app = FastAPI(
    title="CineBook API",
    description="REST API over the Cinema Ticket Booking core (src/booking.py).",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def system() -> BookingSystem:
    # Reload from disk on each request so the CLI and the web UI share state.
    return BookingSystem(data_file=DATA_FILE)


class BookingRequest(BaseModel):
    session_id: str
    customer: str
    ticket_type: str = "standard"
    quantity: int = 1
    seats: Optional[List[str]] = None


def _session_or_404(bs: BookingSystem, session_id: str) -> dict:
    try:
        return bs.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown session {session_id}")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/sessions", tags=["sessions"])
def list_sessions():
    bs = system()
    result = []
    for s in bs.list_sessions():
        total = s["rows"] * s["seats_per_row"]
        free = len(bs.available_seats(s["id"]))
        result.append({**s, "total_seats": total, "free_seats": free})
    return result


@app.get("/api/sessions/{session_id}/seats", tags=["sessions"])
def session_seats(session_id: str):
    bs = system()
    s = _session_or_404(bs, session_id)
    return {
        "session": s,
        "rows": s["rows"],
        "seats_per_row": s["seats_per_row"],
        "booked": s["booked"],
        "available": bs.available_seats(session_id),
    }


@app.get("/api/price", tags=["pricing"])
def price(session_id: str, ticket_type: str = "standard", quantity: int = 1):
    bs = system()
    s = _session_or_404(bs, session_id)
    try:
        total = bs.calculate_price(ticket_type, quantity, s["time"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"total": total, "per_ticket": round(total / quantity, 2) if quantity else 0}


@app.get("/api/bookings", tags=["bookings"])
def list_bookings():
    bookings = list(system().bookings.values())
    return sorted(bookings, key=lambda b: b["created_at"], reverse=True)


@app.post("/api/bookings", tags=["bookings"], status_code=201)
def create_booking(req: BookingRequest):
    bs = system()
    _session_or_404(bs, req.session_id)
    try:
        return bs.book(req.session_id, req.customer, req.ticket_type, req.quantity, req.seats)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/bookings/{booking_id}", tags=["bookings"])
def cancel_booking(booking_id: str):
    if not system().cancel(booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"cancelled": booking_id}


def _tmp_path(suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


@app.get("/api/bookings/{booking_id}/receipt", tags=["export"])
def receipt(booking_id: str, format: str = "json"):
    bs = system()
    if booking_id not in bs.bookings:
        raise HTTPException(status_code=404, detail="Booking not found")
    path = _tmp_path("." + format)
    try:
        bs.export_receipt(booking_id, format, path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FileResponse(path, filename=f"receipt_{booking_id}.{format}")


@app.get("/api/report", tags=["export"])
def report(format: str = "json"):
    path = _tmp_path("." + format)
    try:
        system().export_report(format, path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FileResponse(path, filename=f"bookings_report.{format}")

