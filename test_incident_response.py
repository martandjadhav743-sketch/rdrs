from pathlib import Path

from app.detectors.incident_response import IncidentResponder


def main():
    sandbox = Path("data/sandbox")
    sandbox.mkdir(parents=True, exist_ok=True)

    test_file = sandbox / "incident-test.txt"
    test_file.write_text("This is a safe test file for RDRS.")

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

    quarantine_file = Path("data/quarantine/incident-test.txt")

    if quarantine_file.exists():
        print("PASS: Critical incident was created.")
        print("PASS: Evidence file was copied to quarantine.")
        print(f"Incident ID: {incident.incident_id}")
        print(f"Quarantine file: {quarantine_file}")
    else:
        print("FAIL: Evidence file was not copied to quarantine.")


if __name__ == "__main__":
    main()