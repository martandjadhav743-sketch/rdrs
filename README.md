# RDRS — Ransomware Detection and Response System

RDRS is a defensive Python project that monitors folders for ransomware-like
file activity. It calculates file entropy, records events, and will later
generate alerts, incidents, reports, and a dashboard.

This project is for educational and defensive-security purposes only.
It does not create, download, or execute malware.

## Phase 1 completed

- Created the project structure
- Created and activated a Python virtual environment
- Installed required Python libraries
- Created `requirements.txt`
- Implemented Shannon entropy calculation
- Created a YAML configuration loader using Pydantic
- Added rotating log files using Loguru
- Tested entropy calculation and configuration loading

## Project structure

```text
rdrs/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── entropy.py
│   │   └── logging_setup.py
├── tests/
├── logs/
├── data/
├── config.yaml
├── requirements.txt
└── README.md
```

## How to run

1. Install Python 3.12 or newer.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the program:

```bash
python -m app.main
```

## Current status

Phase 1 is complete. The next phase will add real-time file monitoring using
the `watchdog` library.

## Phase 2: Real-Time File Monitoring

RDRS can monitor configured folders in real time.

### Monitoring features

- Detects file creation.
- Detects file modification.
- Detects file deletion.
- Detects file renaming and movement.
- Displays live event messages in the terminal.
- Counts the total number of detected events.

### Files added

```text
app/core/events.py
app/detectors/file_monitor.py
```

### Phase 2 screenshot

![Phase 2 file monitoring](screenshots/phase2-monitor.png)
## Phase 3: SQLite Database and Process Snapshots

RDRS now stores file events and process snapshots in an SQLite database.

### Database features

- Stores detected file events in the `file_events` table.
- Stores process snapshots in the `process_snapshots` table.
- Saves process information when RDRS starts.
- Uses SQLAlchemy and SQLite.
- Uses `psutil` to collect process information.

### Files added

```text
app/database/models.py
app/database/database.py
app/database/event_repository.py
app/database/process_repository.py
```

### Phase 3 screenshots

![Phase 3 database test](screenshots/phase3-database-test.png)

![Phase 3 database events](screenshots/phase3-database-events.png)

![Phase 3 process snapshot](screenshots/phase3-process-snapshot.png)

![Phase 3 startup process snapshot](screenshots/phase3-startup-process-snapshot.png)