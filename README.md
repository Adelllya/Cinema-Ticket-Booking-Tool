# Cinema Ticket Booking Tool

A small command-line tool for listing movie sessions, booking and cancelling
tickets, and exporting receipts and reports as JSON or CSV.

## Setup

Requires Python 3.9+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run commands from the project root. Booking data is saved to `bookings.json`
(change this with `--data PATH`).

```bash
python -m src.cli sessions
python -m src.cli seats S2
python -m src.cli book S2 --name "Alice" --type student --seats C4,C5
python -m src.cli book S1 --name "Bob" --type child --quantity 2
python -m src.cli cancel <BOOKING_ID>
python -m src.cli receipt <BOOKING_ID> --format csv --output receipt.csv
python -m src.cli report --format json --output report.json
```

Ticket types: `standard`, `student` (20% off), `child` (50% off).
Sessions starting at 18:00 or later add an evening surcharge per ticket.

## Tests

```bash
python -m pytest -v
```

## Web UI

Start the interactive web application:

```bash
python3 -m uvicorn app.server:app --reload
```

Then open http://127.0.0.1:8000 in your browser (API docs at http://127.0.0.1:8000/docs).

