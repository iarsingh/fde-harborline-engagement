# fde-harborline-engagement — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does fde-harborline-engagement address, and what can you demonstrate?

Simulated forward deployed engagement for Harborline Freight, a regional carrier with about 400 trucks. Dispatch was losing half an hour on every late shipment because the answer lived in three places: a nightly TMS export, a ticket queue, and a binder of SOPs. The security rule that shaped the build: shipment data does not leave their environment, and the service makes no call to an external model.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/harborline/api.py`](src/harborline/api.py): Implementation or supporting configuration.
- [`src/harborline/risk.py`](src/harborline/risk.py): Implementation or supporting configuration.
- [`src/harborline/eval.py`](src/harborline/eval.py): Implementation or supporting configuration.
- [`src/harborline/copilot.py`](src/harborline/copilot.py): Implementation or supporting configuration.
- [`src/harborline/models.py`](src/harborline/models.py): Implementation or supporting configuration.
- [`src/harborline/ingest.py`](src/harborline/ingest.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/harborline/__init__.py`](src/harborline/__init__.py): Implementation or supporting configuration.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `score_shipment` and explain the decision it makes?

The main walkthrough here is `score_shipment(shipment: Shipment, tickets: list[Ticket])` in [`src/harborline/risk.py`](src/harborline/risk.py#L9). Score one shipment with the policy Harborline's dispatch lead signed off.

Delivered shipments are out of the queue. Closed tickets do not add risk.
Points are capped so one signal cannot hide the others in the readout.

```python
def score_shipment(shipment: Shipment, tickets: list[Ticket]) -> Risk:
    """Score one shipment with the policy Harborline's dispatch lead signed off.

    Delivered shipments are out of the queue. Closed tickets do not add risk.
    Points are capped so one signal cannot hide the others in the readout.
    """
    score = 0
    reasons: list[str] = []
    open_tickets = tuple(ticket for ticket in tickets if ticket.status == "open")

    overdue = shipment.hours_since_checkpoint - shipment.checkpoint_sla_hours
    if shipment.status != "delivered" and overdue > 0:
        points = min(40, 10 + overdue * 2)
        score += points
        reasons.append(
            f"Checkpoint is {overdue}h past the {shipment.checkpoint_sla_hours}h SLA (+{points})"
        )

    if shipment.status == "exception":
        score += 25
```

This is an excerpt; follow the source link for the rest of the branches.

The implementation calls `', '.join`, `Risk`, `min`, `reasons.append`, `shipment.last_event.lower`, `tuple`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `run` have?

`run(path: Path | None=None)` is defined in [`src/harborline/eval.py`](src/harborline/eval.py#L10).

Its return expressions include:

- `0`
- `1`

It uses `(path or EVALS_PATH).read_text`, `(path or EVALS_PATH).read_text().splitlines`, `answer_question`, `any`, `failures.append`, `json.loads`, `len`, `line.strip`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `SystemExit(main())` in [`src/harborline/__main__.py`](src/harborline/__main__.py#L30).
- `HTTPException(status_code=404, detail=f'Unknown shipment {shipment_id}')` in [`src/harborline/api.py`](src/harborline/api.py#L32).
- `HTTPException(status_code=404, detail=f'Unknown shipment {body.shipment_id}')` in [`src/harborline/api.py`](src/harborline/api.py#L47).
- `HTTPException(status_code=400, detail=str(exc))` in [`src/harborline/api.py`](src/harborline/api.py#L49).
- `ValueError('question is required')` in [`src/harborline/copilot.py`](src/harborline/copilot.py#L27).
- `ValueError(f'{path} needs a heading and numbered steps')` in [`src/harborline/ingest.py`](src/harborline/ingest.py#L71).
- `KeyError(title)` in [`src/harborline/models.py`](src/harborline/models.py#L58).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_api.py`](tests/test_api.py#L12) contains `test_health_reports_the_export_size`:

```python
def test_health_reports_the_export_size():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["shipments"] == 6
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /health` → `health` in [`src/harborline/api.py`](src/harborline/api.py#L23).
- `GET /shipments/{shipment_id}` → `get_shipment` in [`src/harborline/api.py`](src/harborline/api.py#L28).
- `POST /ask` → `ask` in [`src/harborline/api.py`](src/harborline/api.py#L43).
- `GET /audit` → `audit` in [`src/harborline/api.py`](src/harborline/api.py#L72).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `audit_log` in [`src/harborline/api.py`](src/harborline/api.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `score_shipment`?

In [`src/harborline/risk.py`](src/harborline/risk.py#L9), `score_shipment(shipment: Shipment, tickets: list[Ticket])` receives the inputs. The function computes these intermediate values:

- `score = 0`
- `reasons: list[str] = []`
- `open_tickets = tuple((ticket for ticket in tickets if ticket.status == 'open'))`
- `overdue = shipment.hours_since_checkpoint - shipment.checkpoint_sla_hours`
- `p1 = [ticket for ticket in open_tickets if ticket.priority == 'P1']`
- `score = min(score, 100)`

Its result is defined by:

- `Risk(score=score, band=band, reasons=tuple(reasons), open_tickets=open_tickets)`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/harborline/risk.py`](src/harborline/risk.py#L9) branches on:

- `shipment.status != 'delivered' and overdue > 0`
- `shipment.status == 'exception'`
- `p1`
- `shipment.cargo_type == 'reefer' and 'temp' in shipment.last_event.lower()`
- `score >= HIGH_BAND`
- `open_tickets`
- `score >= MEDIUM_BAND`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
