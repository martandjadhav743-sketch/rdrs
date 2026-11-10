from pathlib import Path

from app.detectors.incident_response import IncidentResponder


def main():
    sandbox = Path("data/sandbox")
    sandbox.mkdir(parents=True, exist_ok=True)

    test_file = sandbox / "log-test.txt"
    test_file.write_text("This is a safe Phase 5 log test file.")

    responder = IncidentResponder(
        quarantine_folder="data/quarantine",
        simulation_mode=True,
    )

    incident = responder.create_incident(
        score=95,
        severity="Critical",
        affected_files=[str(test_file)],
    )

    if incident is None:
        print("FAIL: Critical incident was not created.")
        return

    responder.quarantine_files(incident)

    alert_log = Path("logs/alerts.log")
    audit_log = Path("logs/audit.log")
    quarantine_file = Path("data/quarantine/log-test.txt")

    if alert_log.exists():
        print("PASS: Alert log was created.")
    else:
        print("FAIL: Alert log was not created.")

    if audit_log.exists():
        print("PASS: Audit log was created.")
    else:
        print("FAIL: Audit log was not created.")

    if quarantine_file.exists():
        print("PASS: Quarantine copy was created.")
    else:
        print("FAIL: Quarantine copy was not created.")


if __name__ == "__main__":
    main()