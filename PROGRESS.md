# RDRS Progress

## Phase 1 — Completed

- Project setup completed
- Virtual environment created
- Dependencies installed
- Shannon entropy function implemented
- YAML configuration loader implemented
- Loguru logging setup implemented
- Basic project entry point created
- Entropy and configuration tests passed

## Next phase

Phase 2: Real-time file monitoring using watchdog.
## Phase 2: Real-time file monitoring

- Added `app/core/events.py` to create structured file-event records.
- Added `app/detectors/file_monitor.py` to monitor configured folders.
- Updated `app/main.py` to start real-time monitoring.
- Tested file creation, modification, renaming, and deletion in `data/sandbox`.
- Added a Phase 2 monitoring screenshot.
- 
## Phase 3: SQLite database and process snapshots

- Added SQLAlchemy database models for file events and process snapshots.
- Created SQLite database storage in `data/rdrs.db`.
- Added event repository to save live file-monitor events.
- Added process repository to save process snapshots using psutil.
- Updated `app/main.py` to save process snapshots during startup.
- Tested database creation, file-event storage, and process snapshots.
- Added Phase 3 screenshots.

## Phase 4: Sliding-Window Detection — Complete

Phase 4 added sliding-window analysis for recent file activity.

### What was completed

- Created `app/detectors/window_detector.py`.
- Added a `SlidingWindowDetector` class.
- Configured the detector to analyse activity from the last 60 seconds.
- Removed events older than 60 seconds.
- Counted created, modified, deleted, and moved events.
- Detected file extension changes.
- Connected the detector to the live file monitor.
- Added a sliding-window summary every 10 seconds.
- Fixed moved-file events so the destination extension is used.
- Added `test_window_detector.py` to verify old events are removed and event counts are correct.
- Added a Phase 4 screenshot.
- Updated the README with Phase 4 documentation.

### Files added or updated

```text
app/detectors/window_detector.py
app/detectors/file_monitor.py
test_window_detector.py
README.md
screenshots/phase4-extension-change.png
```

### Test result

The sliding-window test passed:

```text
PASS: Old event was removed correctly.
PASS: Modified event count is correct.
PASS: Extension change count is correct.
```

### Live monitoring result

The live monitor successfully detected:

- File creation.
- File modification.
- File renaming from `.txt` to `.locked`.
- Extension change from `.txt` to `.locked`.

The sliding-window summary correctly showed:

```text
'extension_changes': 1
```

### Next phase

## Phase 5: Incident Response — Complete

Phase 5 added a basic incident-response workflow.

### What was completed

- Created an `Incident` dataclass
- Created `IncidentResponder`
- Added Critical incident creation
- Added alert logging
- Added audit logging
- Added safe quarantine copying
- Connected incident response to the live monitor
- Created and ran incident-response tests

### Safety behaviour

RDRS copies affected files into quarantine. It does not delete, encrypt, or modify original files.

### Files added or updated

- `app/detectors/incident_response.py`
- `app/detectors/file_monitor.py`
- `test_incident_response.py`
- `test_incident_logs.py`

### Status

Phase 5 is complete.
## Phase 6: FastAPI Backend — Complete

Phase 6 added a FastAPI backend for RDRS.

### What was completed

- Installed FastAPI and Uvicorn
- Created the `app/api` folder
- Created API routes
- Added `/health`
- Added `/status`
- Added `/alerts`
- Added `/events`
- Added `/reports`
- Added `/scan`
- Added `/settings`
- Tested all endpoints through FastAPI documentation

### Safety behaviour

The POST endpoints accept requests and return responses. They do not delete, encrypt, or modify files.

### Files added or updated

- `app/api/__init__.py`
- `app/api/routes.py`
- `app/main.py`
- `requirements.txt`

### Status

Phase 6 is complete.

## Phase 7: Dark Dashboard

Phase 7 is complete.

Created a dark-themed dashboard in `frontend/index.html`.

The dashboard includes:

- System Status card
- Alerts card
- File Events card
- Reports card

The dashboard connects to the RDRS API and displays:

- API status, monitoring status, and simulation mode
- Alert records
- Recent file events
- Report summaries

Added CORS support to the FastAPI application so the dashboard can communicate with the API.

Screenshot: `screenshots/phase7-dashboard.png`

## Phase 8: Reports

Phase 8 is complete.

Created a report generator in `app/reports/report_generator.py`.

The report generator can:

- Create the `data/reports` folder
- Create a unique report filename
- Create a readable report summary
- Save the report as a text file

Added a `/generate-report` API endpoint in `app/main.py`.

The endpoint counts real file events from the database and creates a report containing:

- Total events
- Created events
- Modified events
- Deleted events
- Moved events
- Total alerts

Added a **Generate Report** button to the dashboard.

The dashboard can now generate and display a report through the API.

Created and tested:

- `test_report_generator.py`
- `test_generate_report.py`

Screenshot: `screenshots/phase8-report.png`

## Phase 9 — Automated Testing (In Progress)

### Completed

- Configured pytest.ini to run the verified automated test suite.
- Added pytest and pytest-cov to the project dependencies.
- Confirmed 33 tests pass together:
  - Incident response: 8 tests.
  - Risk scoring: 11 tests.
  - Sliding-window detection: 12 tests.
  - Detection-to-response integration: 2 tests.
- Tested event and entropy expiration without waiting in real time.
- Verified Critical activity creates an incident, evidence copy,
  and response logs while preserving the original test file.
- Verified Normal activity creates no incident or response artifacts.
- Isolated incident-response and integration test files in temporary
  directories.

### Coverage Recorded

- Risk scorer: 100% statement coverage.
- Sliding-window detector: 100% statement coverage.
- Incident responder: 98% statement coverage.
- Last recorded application-wide coverage: 47%, including the
  earlier configuration and entropy script runs.

### Remaining

- Add isolated API and database tests.
- Add logging and application-startup tests.
- Review known incident-response limitations:
  - Simulation-disabled behavior.
  - Quarantine filename collisions.
- Reach and verify the approximately 90% application-wide
  coverage target.

### Run the Verified Suite

python -m pytest


