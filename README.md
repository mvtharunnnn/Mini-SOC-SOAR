# Mini SOC-SOAR

**Automated Phishing Incident Response** â€” a small, local demonstration of how a security alert can move from SIEM-style detection through a SOAR-style investigation and simulated response into an incident record.

> Firewall blocking, email quarantine and SOC notification are simulated actions for demonstration purposes and do not modify real systems.

## Purpose

This portfolio project demonstrates core SOC workflow concepts in an application that is easy to run and explain:

- SIEM-style detection rules loaded from YAML
- Alert triage and simple IOC extraction
- Offline threat intelligence lookups
- Transparent risk scoring and severity assignment
- Branching playbook decisions and simulated containment
- JSON incident creation and a small Streamlit dashboard

It is intended for learning, interviews, and demonstrations. It is not a production security product.

## What it does

The dashboard loads three sample alerts from `alerts.json` and two simple detection rules from `detections.yaml`:

1. **Phishing alert:** finds indicators in the URL, sender domain, and source IP; checks the local threat intelligence list; calculates risk; simulates a response; and saves an incident.
2. **Clean email:** uses a legitimate Google domain. It is not blocked; with the demo scoring it is escalated for analyst review as a low risk phishing alert.
3. **Suspicious login:** demonstrates matching the multiple-failed-logins detection rule and displays the alert for analyst review. The demo does not create a brute-force incident or run a brute-force response playbook.

## Architecture

```text
Security Alert
      â†“
SIEM Detection Rule
      â†“
SOAR Playbook
      â†“
IOC Extraction
      â†“
Local Threat Intelligence
      â†“
Risk Scoring
      â†“
Simulated Response
      â†“
JSON Incident Creation
      â†“
SOC Dashboard
```

## How the phishing workflow works

1. The app loads an alert and matches its `type` to a rule in `detections.yaml`.
2. `extract_iocs()` reads the URL hostname, sender domain, and source IP.
3. `check_ioc()` looks each value up in the in-memory local dictionary in `threat_intel.py`. There are no threat-intelligence API calls.
4. `calculate_risk()` adds 20 points for a phishing alert and 40 for each malicious IOC, with a maximum score of 100.
5. A score of 80â€“100 is **CRITICAL**. Critical results simulate domain and IP blocking when the relevant IOC is malicious, plus email quarantine and SOC notification. Lower scores are escalated to an analyst.
6. `database.py` assigns an incident ID and writes the incident and its actions to `incidents.json`.
7. The dashboard displays the run trace, IOC results, risk, incident list, and selected incident details.

### Risk model

| Condition | Points |
| --- | ---: |
| Phishing alert | +20 |
| Malicious domain | +40 |
| Malicious IP | +40 |

| Score | Severity |
| ---: | --- |
| 0â€“29 | LOW |
| 30â€“59 | MEDIUM |
| 60â€“79 | HIGH |
| 80â€“100 | CRITICAL |

The sample phishing alert scores `20 + 40 + 40 = 100`, or **CRITICAL**.

## Project files

| File | Role |
| --- | --- |
| `app.py` | Streamlit dashboard, YAML rule loading, alert buttons, and incident views |
| `playbook.py` | IOC extraction, risk calculation, response decision, and phishing playbook |
| `threat_intel.py` | Small offline indicator reputation dictionary and lookup function |
| `database.py` | JSON incident read, create, and update functions |
| `detections.yaml` | SIEM-style phishing and brute-force rules |
| `alerts.json` | Three sample alerts for the dashboard |
| `incidents.json` | Local incident store; starts empty and is populated by running alerts |
| `requirements.txt` | Streamlit and PyYAML dependencies |
| `README.md` | Run instructions, design notes, limitations, and interview guide |

## Requirements and how to run

Use Python 3.9 or later. From this directory, install the dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`. Stop the app with **Ctrl+C** in the terminal.

The app's sample alerts, threat intelligence, and incident workflow use local files and do not call external services. Dependencies must be installed before the first run; after installation, the demo workflow can run without internet access.

## Two-minute interview walkthrough

> â€œI built Mini SOC-SOAR to demonstrate a small end-to-end phishing response workflow. The app loads sample alerts and detection rules from local JSON and YAML files. When I run the phishing alert, the rule matches, the playbook extracts the URL domain and source IP, and a local threat-intelligence list marks both as malicious. The scoring model gives 20 points for phishing and 40 per malicious indicator, so the score is 100 and the severity is critical. The playbook then simulates containment actions and saves an incident to JSON. The dashboard shows the run steps, indicators, risk, and incident details. All response actions are simulated; nothing is sent to a real firewall, mail system, or endpoint.â€

### Demo sequence

1. Start the app and point out the dashboard counters and three sample alerts.
2. Click **Run Phishing Alert**. Explain the matched rule, extracted indicators, local reputation checks, and score.
3. Point to the **SIMULATED RESPONSE** notice and the incident ID/status.
4. Click **Run Clean Alert** and show that `google.com` is CLEAN and no block action is taken.
5. Select the incident to show its persisted JSON-backed details.

### How to explain the phishing output

- **IOC table:** `evil-login.com` is a malicious domain with confidence 95; `185.10.20.30` is a malicious IP with confidence 98. These values come from the project's local demo data, not a live reputation service.
- **Risk 100 / CRITICAL:** 20 phishing points + 40 malicious-domain points + 40 malicious-IP points.
- **Response actions:** domain block, IP block, email quarantine, and SOC notification are labels describing simulated actions only.
- **Incident status `CONTAINED`:** the playbook's simulated critical-response branch completed. It is not evidence of real-world containment.
- **Clean alert:** its phishing type contributes 20 points, while its domain and IP are unknown/clean. The score is LOW and the workflow escalates it; it is not blocked.

## Scope and limitations

- Only the phishing alert has a full response playbook. The brute-force sample demonstrates rule matching and analyst visibility, not incident creation or an automated login response.
- Detection rules are intentionally simple: the app matches alert types, with a five-failed-attempt threshold for the login example. This is not a general SIEM query engine.
- The threat-intelligence list is tiny, hard-coded, and exact-match. Unknown values are treated as CLEAN for this demonstration; that must not be interpreted as proof that an indicator is safe.
- IOC extraction handles the hostname in the alert URL, the sender's domain, and a dotted-quad source IP. It does not parse email headers, attachments, redirects, encoded links, or full message bodies.
- Risk scoring is illustrative rather than calibrated. It does not use asset criticality, user context, confidence weighting, time decay, or business impact.
- Responses are simulated. There are no firewall, email, EDR, identity, ticketing, or notification integrations.
- `incidents.json` is suitable for a single-user demo, not concurrent production use. It has no locking, access controls, audit guarantees, or database transactions.
- The app has no authentication, authorization, production logging, or deployment hardening. Sample indicators and alerts are synthetic examples.

## Interview questions and suggested answers

**What problem does this solve?**  
It demonstrates the flow from an alert to detection, investigation, prioritization, a response decision, and a tracked incident. The point is to make that workflow concrete and reviewable.

**What is the difference between SIEM and SOAR here?**  
The YAML rule match represents a basic SIEM detection step. The playbook represents SOAR-style orchestration: enrich indicators, calculate a score, choose actions, and create an incident. Both are simplified demonstrations.

**How does the app decide the alert is phishing?**  
The sample alert has `type: phishing`. `app.py` finds a rule with the same type in `detections.yaml`. This is a small rule-selection example, not content inspection or machine learning.

**How are the indicators found?**  
The playbook parses the URL hostname, takes the domain after `@` in the sender, and reads a dotted-quad `source_ip`. It avoids adding the same domain twice.

**Where does threat intelligence come from?**  
`threat_intel.py` contains two hard-coded malicious sample indicators. Lookup happens locally with no paid or remote API. Unknown indicators return `CLEAN` with confidence 0 for demo purposes only.

**Why does the sample score 100?**  
The phishing alert contributes 20 points, the malicious domain adds 40, and the malicious IP adds 40. The score is capped at 100 and maps to CRITICAL.

**Why treat an unknown IOC as CLEAN?**  
That is the simple behavior specified for this demo. In a production workflow, unknown should be represented as unknown or unclassified, not safe, and the response should account for uncertainty.

**What happens for a low or medium score?**  
The phishing playbook records an `ESCALATED` incident with the action `Escalated to analyst`. It does not run containment actions.

**What happens to the suspicious login?**  
It matches the multiple-failed-logins rule when at least five failures are present. The UI displays it for analyst review. A full brute-force playbook and incident ticket are outside this project's scope.

**Does the app actually block or quarantine anything?**  
No. It only records simulated actions in a local incident JSON file. It does not modify the computer or contact security products.

**Where are incidents stored?**  
In `incidents.json`, next to the app. `database.py` reads and writes this file. The data remains after the app closes unless the file is manually reset.

**Why use JSON instead of SQLite?**  
The project has a handful of demo records and one local user, so JSON keeps the storage easy to inspect without adding infrastructure. SQLite would be more appropriate for querying, concurrent access, and stronger consistency.

**How do you verify the workflow?**  
Run the phishing button and confirm the two malicious indicators, score 100, CRITICAL severity, simulated actions, and a persisted contained incident. Then run the clean alert and confirm it escalates without a block action. The app was also exercised with Streamlit's `AppTest`.

**What would you improve next?**  
I would add structured unknown IOC states, unit tests for edge cases, more robust email parsing, analyst feedback, audit timestamps, and a transactional store. Any real response integration would need approval gates, least-privilege credentials, and safeguards against false positives.

**Why is this relevant to a SOC or security automation role?**  
It shows familiarity with the incident lifecycle, detection rules, IOC enrichment, prioritization, playbook branching, incident records, and the need to distinguish a simulated response from a real control action.

## Disclaimer

This is an educational portfolio project. Threat intelligence is synthetic and incomplete. Firewall blocking, email quarantine, and SOC notification are simulated actions for demonstration purposes and do not modify real systems.

