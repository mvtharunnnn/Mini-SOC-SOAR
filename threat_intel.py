"""Offline threat intelligence lookups for the Mini SOC-SOAR demo."""

MALICIOUS_IOCS = {
    "evil-login.com": {"type": "domain", "reputation": "MALICIOUS", "confidence": 95},
    "185.10.20.30": {"type": "ip", "reputation": "MALICIOUS", "confidence": 98},
}


def check_ioc(ioc):
    """Return a local reputation record; unknown indicators are CLEAN."""
    value = str(ioc or "").strip().lower()
    record = MALICIOUS_IOCS.get(value)
    if record:
        return {"ioc": ioc, **record}
    kind = "ip" if value.count(".") == 3 and all(part.isdigit() for part in value.split(".")) else "domain"
    return {"ioc": ioc, "type": kind, "reputation": "CLEAN", "confidence": 0}

