# Rollout plan

## Week 0 — fit the policy to their lead

- Walk five historical shipments with the night lead.
- Change a point value only when the lead disagrees, and add that shipment to `evals/questions.jsonl`.
- `pytest` and `python -m harborline eval` stay green.

## Week 1 — shadow

- Run the service beside the current workflow. Dispatchers still use the binder.
- Time 20 lookups. Target is under 2 minutes to a cited answer.
- Review disagreements daily. A disagreement updates the policy, not a prompt.

## Week 2 — one desk

- Night desk uses the service for reefer and medical loads only.
- Dry vans stay on the old path until the lead asks to expand.
- Rollback is stopping the container. Nothing has been written back to the TMS, so rollback does not unwind customer data.

## Stop conditions

Stop the desk rollout if any of these happen:

- An answer has no SOP citation
- The eval file fails
- The lead overturns the band on more than 1 in 10 reviewed shipments
- Anyone finds the service calling out of the VPC

## Handoff

Leave them with the run command, the eval command, the score table, and a named owner on their IT team for the export drop. The engagement is finished when that owner can add a shipment to the eval file without us.
