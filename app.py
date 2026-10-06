"""Local Streamlit dashboard for the Mini SOC-SOAR portfolio project."""

import json
from pathlib import Path

import streamlit as st
import yaml

from database import get_incidents
from playbook import run_phishing_playbook

BASE_DIR = Path(__file__).parent


@st.cache_data
def load_alerts():
    return json.loads((BASE_DIR / "alerts.json").read_text(encoding="utf-8"))


@st.cache_data
def load_rules():
    with (BASE_DIR / "detections.yaml").open(encoding="utf-8") as handle:
        return yaml.safe_load(handle).get("rules", [])


def match_rule(alert):
    for rule in load_rules():
        if rule.get("type") == alert.get("type"):
            if alert.get("type") != "brute_force" or alert.get("failed_attempts", 0) >= 5:
                return rule
    return None


st.set_page_config(page_title="Mini SOC-SOAR", page_icon="ðŸ›¡ï¸", layout="wide")
st.title("ðŸ›¡ï¸ Mini SOC-SOAR")
st.caption("Automated phishing incident response Â· Local-only demonstration")

alerts = load_alerts()
incidents = get_incidents()
critical = sum(item.get("severity") == "CRITICAL" for item in incidents)
contained = sum(item.get("status") == "CONTAINED" for item in incidents)
escalated = sum(item.get("status") == "ESCALATED" for item in incidents)

st.header("Dashboard")
columns = st.columns(5)
for column, label, value in zip(columns, ["Total alerts", "Incidents", "Critical", "Contained", "Escalated"], [len(alerts), len(incidents), critical, contained, escalated]):
    column.metric(label, value)

st.header("Alert Simulator")
alert_by_id = {alert["id"]: alert for alert in alerts}
buttons = st.columns(3)
run_alert = None
for column, alert_id, label in zip(buttons, ["ALERT-001", "ALERT-002", "ALERT-003"], ["Run Phishing Alert", "Run Clean Alert", "Run Suspicious Login"]):
    if column.button(label, width="stretch"):
        run_alert = alert_by_id[alert_id]

if run_alert:
    rule = match_rule(run_alert)
    if not rule:
        st.session_state["last_run"] = {"alert_id": run_alert["id"], "kind": "none"}
    elif run_alert.get("type") == "phishing":
        result = run_phishing_playbook(run_alert)
        st.session_state["last_run"] = {"alert_id": run_alert["id"], "kind": "phishing", "rule": rule, "result": result}
    else:
        st.session_state["last_run"] = {"alert_id": run_alert["id"], "kind": "login", "rule": rule, "alert": run_alert}

last_run = st.session_state.get("last_run")
if last_run:
    st.subheader(f"Execution: {last_run['alert_id']}")
    if last_run["kind"] == "none":
        st.info("No detection rule matched this alert.")
    elif last_run["kind"] == "phishing":
        result = last_run["result"]
        for step in result["steps"]:
            st.write(f"âœ… {step}")
        rule = last_run["rule"]
        st.caption(f"Matched {rule['id']} Â· {rule['name']} ({rule['severity']})")
        st.info("SIMULATED RESPONSE â€” no real systems were changed.")
        st.write(f"Risk: **{result['risk_score']} / 100 Â· {result['severity']}**")
        st.write("IOC results")
        st.dataframe(result["iocs"], width="stretch", hide_index=True)
        st.success(f"{result['incident']['id']} created Â· {result['incident']['status']}")
    else:
        alert = last_run["alert"]
        rule = last_run["rule"]
        st.success(f"âœ… Detection rule matched: {rule['id']} Â· {rule['name']}")
        st.write(f"Failed attempts: **{alert.get('failed_attempts')}** in {alert.get('window_minutes')} minutes.")
        st.info("SIMULATED RESPONSE â€” login alert surfaced for analyst review; this demo playbook handles phishing incidents.")

st.header("Incident List")
incidents = get_incidents()
if incidents:
    rows = [{"Incident": i["id"], "Type": i["type"].replace("_", " ").title(), "Severity": i["severity"], "Risk": i["risk_score"], "Status": i["status"]} for i in incidents]
    st.dataframe(rows, width="stretch", hide_index=True)
    selected_id = st.selectbox("View incident details", [item["id"] for item in incidents])
    selected = next(item for item in incidents if item["id"] == selected_id)
    with st.expander(f"{selected_id} details", expanded=True):
        st.json(selected)
else:
    st.info("No incidents yet. Run an alert above to start the demo.")

with st.expander("Detection rules"):
    st.dataframe(load_rules(), width="stretch", hide_index=True)

