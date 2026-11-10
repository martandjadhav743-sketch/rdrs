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
