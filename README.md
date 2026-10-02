# Harborline dispatch copilot

Simulated forward deployed engagement for Harborline Freight, a regional carrier with about 400 trucks. Dispatch was losing half an hour on every late shipment because the answer lived in three places: a nightly TMS export, a ticket queue, and a binder of SOPs. The security rule that shaped the build: shipment data does not leave their environment, and the service makes no call to an external model.

This repo is the engagement artifact a hiring manager can run. The customer, the exports, and the baseline times are fictional. The engineering is real: a signed-off risk policy, cited answers, an eval gate, and an audit log that stores the decision without storing the ticket text.

## What dispatch gets

Ask about a shipment id and get four things:

- a risk score with every point explained
- the SOP the dispatch lead already approved for that case
- the first three steps to execute
- citations back to the export row, the open ticket, and the SOP

```text
Shipment SHP-1042 is high risk (score 76).
Why:
- Checkpoint is 8h past the 6h SLA (+26)
- Open P1 ticket TCK-19: Reefer temp alarm on Memphis dwell (+30)
- Reefer cargo has a temperature event: temp alarm acknowledged (+20)
Do this (Cold-chain exception):
1. Confirm the last temperature reading with the driver.
```

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
pytest
python -m harborline eval
python -m harborline SHP-1042 "Why is this reefer shipment late?"
uvicorn harborline.api:app --reload
```

`POST /ask` with `{"shipment_id": "SHP-1042", "question": "Why is this reefer shipment late?"}`. `GET /audit` returns shipment id, band, score, and citation count. It does not store the question or the ticket summary.

Docker, for the "land it in their VPC" conversation:

```bash
docker build -t harborline-copilot .
docker run --rm -p 8000:8000 harborline-copilot
```

## Engagement docs

| Doc | What it decides |
| --- | --- |
| [Discovery brief](docs/01-discovery-brief.md) | Who hurts, what is in scope, the constraint that changed the design |
| [Success metrics](docs/02-success-metrics.md) | What "done" means before any code |
| [Solution design](docs/03-solution-design.md) | Why the score is a policy, not a model |
| [Security and data](docs/04-security-and-data.md) | What stays local, what the audit log is allowed to keep |
| [Rollout plan](docs/05-rollout-plan.md) | Shadow week, then one desk, then the floor |
| [Customer readout](docs/06-customer-readout.md) | The note you would send the VP of operations |

The reusable templates behind these docs live in [fde-engagement-playbook](https://github.com/iarsingh/fde-engagement-playbook).

## Sample the policy was fit to

| Shipment | Situation | Score | Band | SOP |
| --- | --- | --- | --- | --- |
| SHP-1042 | Reefer, 8h past SLA, open P1 | 76 | high | Cold-chain exception |
| SHP-0988 | Medical, exception, open P2 | 74 | high | Medical priority |
| SHP-1310 | Reefer exception with a temp alarm | 87 | high | Cold-chain exception |
| SHP-1201 | Weather hold, open P2 | 41 | medium | Checkpoint delay |
| SHP-1108 | On time, no ticket | 0 | low | Checkpoint delay |
| SHP-0770 | Delivered, closed ticket | 0 | low | Checkpoint delay |

Delivered shipments leave the queue even if the last checkpoint looks stale. Closed tickets do not add points. Medical customers take the medical SOP even when the trailer is a reefer.
