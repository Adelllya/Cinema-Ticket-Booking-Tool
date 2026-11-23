import json

from src.booking import BookingSystem


def test_list_sessions_returns_default_sessions():
    system = BookingSystem()
    sessions = system.list_sessions()
    assert len(sessions) == 4
    assert sessions[0]["movie"] == "Interstellar"


def test_calculate_price_for_each_ticket_type():
    system = BookingSystem()
    # Matinee (no evening surcharge)
    assert system.calculate_price("standard", 2, "2026-12-01 14:00") == 24.0
    assert system.calculate_price("student", 1, "2026-12-01 14:00") == 9.6
    assert system.calculate_price("child", 1, "2026-12-01 14:00") == 6.0
    # Evening session adds a surcharge per ticket
    assert system.calculate_price("standard", 2, "2026-12-01 19:30") == 28.0


def test_book_tickets_reserves_seats():
    system = BookingSystem()
    before = len(system.available_seats("S1"))
    booking = system.book("S1", "Alice", "student", seats=["A1", "A2"])
    assert booking["status"] == "confirmed"
    assert booking["total"] == 19.2
    assert "A1" not in system.available_seats("S1")
    assert len(system.available_seats("S1")) == before - 2


def test_cancel_booking_releases_seats():
    system = BookingSystem()
    booking = system.book("S2", "Bob", "standard", quantity=3)
    assert system.cancel(booking["id"]) is True
    assert system.bookings[booking["id"]]["status"] == "cancelled"
    for seat in booking["seats"]:
        assert seat in system.available_seats("S2")


def test_export_receipt_json(tmp_path):
    system = BookingSystem()
    booking = system.book("S3", "Carol", "child", quantity=2)
    out = tmp_path / "receipt.json"
    system.export_receipt(booking["id"], "json", str(out))
    data = json.loads(out.read_text())
    assert data["customer"] == "Carol"
    assert data["total"] == 12.0

