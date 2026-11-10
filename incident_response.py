import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Incident:
    incident_id: str
    created_at: datetime
    score: int
    severity: str
    affected_files: list[str] = field(default_factory=list)
    quarantine_files: list[str] = field(default_factory=list)


class IncidentResponder:
    def __init__(self, quarantine_folder: str, simulation_mode: bool = True) -> None:
        self.quarantine_folder = Path(quarantine_folder)
        self.simulation_mode = simulation_mode
        self.incidents: list[Incident] = []
        self.alert_log_path = Path("logs/alerts.log")
        self.audit_log_path = Path("logs/audit.log")

    def _write_log(self, log_path: Path, message: str) -> None:
        """Append one line to a log file."""
        log_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).isoformat()

        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp} | {message}\n")

    def create_incident(
        self,
        score: int,
        severity: str,
        affected_files: list[str],
    ) -> Incident | None:
        if severity != "Critical":
            return None

        incident_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        created_at = datetime.now(timezone.utc)

        incident = Incident(
            incident_id=incident_id,
            created_at=created_at,
            score=score,
            severity=severity,
            affected_files=affected_files,
        )

        self.incidents.append(incident)

        print("CRITICAL INCIDENT CREATED")
        print(f"Incident ID: {incident_id}")
        print(f"Score: {score}")
        print(f"Affected files: {len(affected_files)}")

        self._write_log(
            self.alert_log_path,
            f"CRITICAL INCIDENT | incident_id={incident_id} | score={score} | affected_files={len(affected_files)}",
        )

        return incident

    def quarantine_files(self, incident: Incident) -> None:
        if self.simulation_mode:
            print("Simulation mode: quarantine copying is enabled for evidence copies.")
        else:
            print("Simulation mode is disabled. No automatic response will be performed.")

        self.quarantine_folder.mkdir(parents=True, exist_ok=True)

        for source_path in incident.affected_files:
            source = Path(source_path)

            if not source.exists():
                continue

            destination = self.quarantine_folder / source.name
            shutil.copy2(source, destination)

            incident.quarantine_files.append(str(destination))
            print(f"Evidence copied: {source} -> {destination}")

            self._write_log(
                self.audit_log_path,
                f"QUARANTINE COPY | incident_id={incident.incident_id} | source={source} | destination={destination}",
            )