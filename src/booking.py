"""Core booking logic for the Cinema Ticket Booking Tool."""

import csv
import json
import os
import uuid
from datetime import datetime

BASE_PRICE = 12.0
STUDENT_DISCOUNT = 0.2
CHILD_DISCOUNT = 0.5
EVENING_SURCHARGE = 2.0
EVENING_START_HOUR = 18

DEFAULT_SESSIONS = [
    {"id": "S1", "movie": "Interstellar", "time": "2026-12-01 14:00",
     "hall": "Hall 1", "rows": 5, "seats_per_row": 8},
    {"id": "S2", "movie": "Interstellar", "time": "2026-12-01 19:30",
     "hall": "Hall 1", "rows": 5, "seats_per_row": 8},
    {"id": "S3", "movie": "Spirited Away", "time": "2026-12-02 11:00",
     "hall": "Hall 2", "rows": 4, "seats_per_row": 6},
    {"id": "S4", "movie": "Dune: Part Two", "time": "2026-12-02 20:00",
     "hall": "Hall 3", "rows": 6, "seats_per_row": 10},
]


class BookingSystem:
    def __init__(self, data_file=None):
        self.data_file = data_file
        self.sessions = {}
        self.bookings = {}
        self._load()

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def _load(self):
        if self.data_file and os.path.exists(self.data_file):
            with open(self.data_file) as f:
                data = json.load(f)
            self.sessions = {s["id"]: s for s in data["sessions"]}
            self.bookings = data["bookings"]
        else:
            self.sessions = {s["id"]: dict(s, booked=[]) for s in DEFAULT_SESSIONS}
            self.bookings = {}

    def save(self):
        if not self.data_file:
            return
        with open(self.data_file, "w") as f:
            json.dump(
                {"sessions": list(self.sessions.values()), "bookings": self.bookings},
                f,
                indent=2,
            )

    # ------------------------------------------------------------------ #
    # Sessions and seats
    # ------------------------------------------------------------------ #
    def list_sessions(self):
        return list(self.sessions.values())

    def get_session(self, session_id):
        if session_id not in self.sessions:
            raise KeyError(f"Unknown session: {session_id}")
        return self.sessions[session_id]

    def _all_seats(self, session):
        seats = []
        for r in range(session["rows"]):
            row_letter = chr(ord("A") + r)
            for n in range(1, session["seats_per_row"] + 1):
                seats.append(f"{row_letter}{n}")
        return seats

    def available_seats(self, session_id):
        session = self.get_session(session_id)
        return [s for s in self._all_seats(session) if s not in session["booked"]]

    # ------------------------------------------------------------------ #
    # Pricing
    # ------------------------------------------------------------------ #
    def calculate_price(self, ticket_type, quantity, show_time):
        hour = int(show_time.split(" ")[1].split(":")[0])
        if ticket_type == "standard":
            price = BASE_PRICE
            if hour >= EVENING_START_HOUR:
                price = price + EVENING_SURCHARGE
            total = price * quantity
            total = round(total, 2)
        elif ticket_type == "student":
            price = BASE_PRICE - BASE_PRICE * STUDENT_DISCOUNT
            if hour >= EVENING_START_HOUR:
                price = price + EVENING_SURCHARGE
            total = price * quantity
            total = round(total, 2)
        elif ticket_type == "child":
            price = BASE_PRICE - BASE_PRICE * CHILD_DISCOUNT
            if hour >= EVENING_START_HOUR:
                price = price + EVENING_SURCHARGE
            total = price * quantity
            total = round(total, 2)
        else:
            raise ValueError(f"Unknown ticket type: {ticket_type}")
        return total

    # ------------------------------------------------------------------ #
    # Booking / cancelling
    # ------------------------------------------------------------------ #
    def book(self, session_id, customer, ticket_type="standard", quantity=1, seats=None):
        session = self.get_session(session_id)

        if seats is None:
            seats = self.available_seats(session_id)[:quantity]
        else:
            quantity = len(seats)

        total = self.calculate_price(ticket_type, quantity, session["time"])

        booking_id = uuid.uuid4().hex[:8].upper()
        booking = {
            "id": booking_id,
            "session_id": session_id,
            "movie": session["movie"],
            "time": session["time"],
            "customer": customer,
            "ticket_type": ticket_type,
            "quantity": quantity,
            "seats": list(seats),
            "total": total,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        session["booked"].extend(seats)
        self.bookings[booking_id] = booking
        print(f"Booking {booking_id} created for {customer}")
        self.save()
        return booking

    def cancel(self, booking_id):
        booking = self.bookings.get(booking_id)
        if booking is None:
            print(f"Booking {booking_id} not found")
            return False
        session = self.sessions[booking["session_id"]]
        for seat in booking["seats"]:
            if seat in session["booked"]:
                session["booked"].remove(seat)
        booking["status"] = "cancelled"
        print(f"Booking {booking_id} cancelled")
        self.save()
        return True

    # ------------------------------------------------------------------ #
    # Export
    # ------------------------------------------------------------------ #
    def export_receipt(self, booking_id, fmt, path):
        booking = self.bookings[booking_id]
        if fmt == "json":
            with open(path, "w") as f:
                json.dump(booking, f, indent=2)
            print(f"Receipt written to {path}")
        elif fmt == "csv":
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "movie", "time", "customer", "ticket_type",
                                 "quantity", "seats", "total", "status"])
                writer.writerow([booking["id"], booking["movie"], booking["time"],
                                 booking["customer"], booking["ticket_type"],
                                 booking["quantity"], " ".join(booking["seats"]),
                                 booking["total"], booking["status"]])
            print(f"Receipt written to {path}")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return path

    def export_report(self, fmt, path):
        bookings = list(self.bookings.values())
        if fmt == "json":
            with open(path, "w") as f:
                json.dump(bookings, f, indent=2)
            print(f"Report written to {path}")
        elif fmt == "csv":
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "movie", "time", "customer", "ticket_type",
                                 "quantity", "seats", "total", "status"])
                for b in bookings:
                    writer.writerow([b["id"], b["movie"], b["time"], b["customer"],
                                     b["ticket_type"], b["quantity"], " ".join(b["seats"]),
                                     b["total"], b["status"]])
            print(f"Report written to {path}")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return path

