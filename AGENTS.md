# AGENTS.md

## Project Overview
Cinema Ticket Booking Tool is a Python application for managing cinema sessions, seat availability, ticket pricing, bookings, cancellations, and JSON/CSV exports.

## Architecture
- `src/booking.py`: Core `BookingSystem` class and JSON persistence (`bookings.json`).
- `app/server.py`: FastAPI REST API and static UI (`app/static/index.html`).
- `src/cli.py`: Command-line interface (`argparse`).
- `tests/test_booking.py`: Pytest unit test suite.

## Setup and Verification Commands
- Install dependencies: `pip install -r requirements.txt`
- Run unit tests: `python3 -m pytest -v`
- Check CLI: `python3 -m src.cli sessions`
- Start local server: `python3 -m uvicorn app.server:app --reload`

## Coding Conventions and Test Expectations
- Keep changes minimal and backwards-compatible with existing CLI and API endpoints.
- Preserve pricing rules: `standard` ($12.0), `student` ($9.6), `child` ($6.0), plus `$2.0` surcharge at or after 18:00.
- All baseline tests in `tests/test_booking.py` must continue to pass (`pytest -v`), and every bug fix requires a new unit test.

## Forbidden Actions
- Never commit secrets, tokens, API keys, or personal data.
- Never run destructive shell or git commands (`rm -rf`, `git reset --hard`, `git push --force`).
- Never modify `requirements.txt` without explicit approval.
- Never deploy to production or change external services.