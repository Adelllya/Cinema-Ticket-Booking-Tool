"""Command-line interface for the Cinema Ticket Booking Tool."""

import argparse
import sys

from src.booking import BookingSystem

DEFAULT_DATA_FILE = "bookings.json"


def build_parser():
    parser = argparse.ArgumentParser(prog="cinema", description="Cinema Ticket Booking Tool")
    parser.add_argument("--data", default=DEFAULT_DATA_FILE,
                        help="Path to the JSON data file (default: bookings.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sessions", help="List all movie sessions")

    p_seats = sub.add_parser("seats", help="Show available seats for a session")
    p_seats.add_argument("session_id")

    p_book = sub.add_parser("book", help="Book tickets for a session")
    p_book.add_argument("session_id")
    p_book.add_argument("--name", required=True, help="Customer name")
    p_book.add_argument("--type", default="standard", dest="ticket_type",
                        choices=["standard", "student", "child"])
    p_book.add_argument("--quantity", type=int, default=1)
    p_book.add_argument("--seats", help="Comma-separated seat list, e.g. A1,A2")

    p_cancel = sub.add_parser("cancel", help="Cancel a booking")
    p_cancel.add_argument("booking_id")

    p_receipt = sub.add_parser("receipt", help="Export a booking receipt")
    p_receipt.add_argument("booking_id")
    p_receipt.add_argument("--format", default="json", choices=["json", "csv"])
    p_receipt.add_argument("--output", required=True)

    p_report = sub.add_parser("report", help="Export a report of all bookings")
    p_report.add_argument("--format", default="json", choices=["json", "csv"])
    p_report.add_argument("--output", required=True)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    system = BookingSystem(data_file=args.data)

    if args.command == "sessions":
        for s in system.list_sessions():
            free = len(system.available_seats(s["id"]))
            print(f"{s['id']:<4} {s['movie']:<20} {s['time']}  {s['hall']:<7} free seats: {free}")
    elif args.command == "seats":
        seats = system.available_seats(args.session_id)
        print(f"{len(seats)} seats available: {' '.join(seats)}")
    elif args.command == "book":
        seats = args.seats.split(",") if args.seats else None
        booking = system.book(args.session_id, args.name, args.ticket_type,
                              args.quantity, seats)
        print(f"Seats: {' '.join(booking['seats'])}  Total: ${booking['total']:.2f}")
    elif args.command == "cancel":
        if not system.cancel(args.booking_id):
            return 1
    elif args.command == "receipt":
        system.export_receipt(args.booking_id, args.format, args.output)
    elif args.command == "report":
        system.export_report(args.format, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

