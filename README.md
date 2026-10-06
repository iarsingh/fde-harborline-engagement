# Harborline dispatch copilot

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/harborline/api.py`](src/harborline/api.py) | HTTP handlers: `GET /health`, `GET /shipments/{shipment_id}`, `POST /ask`, `GET /audit` |
| [`src/harborline/risk.py`](src/harborline/risk.py) | Functions: `score_shipment` |
| [`src/harborline/eval.py`](src/harborline/eval.py) | Functions: `run` |
| [`src/harborline/copilot.py`](src/harborline/copilot.py) | Functions: `select_sop`, `answer_question` |
| [`src/harborline/models.py`](src/harborline/models.py) | Functions: `shipment`, `tickets_for`, `sop`, `render` |
| [`src/harborline/ingest.py`](src/harborline/ingest.py) | Functions: `load_store`, `_load_shipments`, `_load_tickets`, `_load_sops` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/harborline/__init__.py`](src/harborline/__init__.py) | Implementation or supporting configuration |
| [`src/harborline/__main__.py`](src/harborline/__main__.py) | Functions: `main` |
| [`Dockerfile`](Dockerfile) | Container build/service configuration |
| [`tests/test_api.py`](tests/test_api.py) | Executable checks and regression examples |
| [`tests/test_copilot.py`](tests/test_copilot.py) | Executable checks and regression examples |
| [`tests/test_eval.py`](tests/test_eval.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |
| [`data/sops/checkpoint-delay.md`](data/sops/checkpoint-delay.md) | Project explanations or operating notes |
| [`data/sops/cold-chain-exception.md`](data/sops/cold-chain-exception.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn harborline.api:app --reload
```

<!-- project-guide:end -->

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

## Documentation checks

Project architecture, interview guides, and local source links are checked automatically on pushes and pull requests. Run the same check locally:

```bash
python3 .github/scripts/validate_project_docs.py
```
