"""Small JSON-backed incident store. All data stays beside the application."""

import json
from pathlib import Path

INCIDENTS_FILE = Path(__file__).with_name("incidents.json")


def get_incidents():
    if not INCIDENTS_FILE.exists():
        return []
    try:
        data = json.loads(INCIDENTS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def create_incident(incident):
    incidents = get_incidents()
    incident = dict(incident)
    incident["id"] = f"INC-{len(incidents) + 1:04d}"
    incidents.append(incident)
    INCIDENTS_FILE.write_text(json.dumps(incidents, indent=2), encoding="utf-8")
    return incident


def update_incident(incident_id, updates):
    incidents = get_incidents()
    for incident in incidents:
        if incident.get("id") == incident_id:
            incident.update(updates)
            INCIDENTS_FILE.write_text(json.dumps(incidents, indent=2), encoding="utf-8")
            return incident
    return None

