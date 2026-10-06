"""A compact phishing response playbook with explicitly simulated actions."""

import re
from urllib.parse import urlparse

from database import create_incident
from threat_intel import check_ioc


def extract_iocs(alert):
    indicators = []
    url = alert.get("url", "")
    if url:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        host = (parsed.hostname or "").lower()
        if host:
            indicators.append(host)
    sender_domain = alert.get("sender", "").rsplit("@", 1)[-1].lower()
    if sender_domain and sender_domain not in indicators:
        indicators.append(sender_domain)
    ip = alert.get("source_ip", "")
    if ip and re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", ip):
        indicators.append(ip)
    return indicators


def calculate_risk(alert, ioc_results):
    score = 20 if alert.get("type") == "phishing" else 0
    for result in ioc_results:
        if result["reputation"] == "MALICIOUS":
            score += 40
    score = min(score, 100)
    severity = "LOW" if score < 30 else "MEDIUM" if score < 60 else "HIGH" if score < 80 else "CRITICAL"
    return score, severity


def run_phishing_playbook(alert):
    steps = ["Alert received", "Detection rule matched"]
    indicators = extract_iocs(alert)
    steps.append("IOC extracted")
    results = [check_ioc(ioc) for ioc in indicators]
    steps.append("Threat intelligence checked")
    score, severity = calculate_risk(alert, results)
    steps.append("Risk calculated")
    malicious = [item for item in results if item["reputation"] == "MALICIOUS"]
    actions = []
    if severity == "CRITICAL":
        if any(item["type"] == "domain" for item in malicious):
            actions.append("Domain blocked")
        if any(item["type"] == "ip" for item in malicious):
            actions.append("IP blocked")
        actions.extend(["Email quarantined", "SOC notified"])
        status = "CONTAINED"
    else:
        actions.append("Escalated to analyst")
        status = "ESCALATED"
    steps.append("Simulated response executed")
    incident = create_incident({
        "alert_id": alert.get("id", "UNKNOWN"),
        "type": alert.get("type", "unknown"),
        "severity": severity,
        "risk_score": score,
        "user": alert.get("user", "unknown"),
        "status": status,
        "actions": actions,
        "iocs": results,
        "subject": alert.get("subject", ""),
    })
    steps.append("Incident created")
    return {"incident": incident, "steps": steps, "iocs": results, "risk_score": score, "severity": severity}

