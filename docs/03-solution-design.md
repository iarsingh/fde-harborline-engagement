# Solution design

## Decision

Ship a small HTTP service that reads the customer's files from disk and applies a written policy. Do not call a model.

The night lead has to defend the score. A hidden ranker fails that test even when it is often right. The policy lives in `src/harborline/risk.py` and `select_sop` in `src/harborline/copilot.py`.

## Score

Only shipments that are not `delivered` can earn lateness points.

| Signal | Points | Cap |
| --- | --- | --- |
| Hours past checkpoint SLA | `10 + 2 per overdue hour` | 40 |
| TMS status `exception` | 25 | |
| Any open P1 ticket | 30 | |
| Any other open ticket, if there is no P1 | 15 | |
| Reefer cargo whose last event mentions `temp` | 20 | |

The total is capped at 100.

| Score | Band |
| --- | --- |
| 70-100 | high |
| 40-69 | medium |
| 0-39 | low |

Closed tickets add nothing. A delivered shipment with a stale checkpoint adds nothing.

## SOP choice

Checked in this order:

1. Customer name or question contains "medical" → Medical priority
2. Reefer cargo and the last event contains "temp" → Cold-chain exception
3. Otherwise → Checkpoint delay

The answer returns the first three numbered steps and a citation of `path#title`.

## Request path

`POST /ask` loads nothing from the network. It scores the shipment, selects the SOP, appends an audit event, and returns the text a dispatcher can read aloud.

The audit event stores time, shipment id, band, score, and citation count. It does not store the question text or the ticket summary.

## Why this is the FDE cut

A platform team would generalize the scorer. The engagement cut is the opposite: encode Harborline's three playbooks, refuse the model API they will not approve, and put an eval file in the rollout gate so a later "smarter" version cannot ship a wrong band.
