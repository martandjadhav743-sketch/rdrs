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
