# Discovery brief — Harborline Freight

**Engagement:** dispatch copilot for late shipments
**Sponsor:** VP of operations
**Day-to-day owner:** night dispatch lead
**Length proposed:** 2 weeks to a shadow desk, not a platform rewrite

## The job to be done

When a checkpoint goes quiet, a dispatcher opens the TMS export, searches the ticket queue, and flips to a printed SOP. The night lead timed this at 25 to 40 minutes for a reefer or medical load. Most of that time is finding the row, not deciding.

They do not want a chatbot for the whole company. They want one question answered on the night desk: why is this shipment late, and what do we do next?

## Who was in the room

| Person | Cares about |
| --- | --- |
| VP of operations | Fewer missed delivery windows on medical and grocery |
| Night dispatch lead | A rule the desk can explain at 2am |
| IT manager | No new vendor that receives shipment data |
| Driver supervisor | Not another app the driver has to tap |

## Constraint that changed the design

IT will not approve a third-party model API. The nightly export and the ticket file stay on their side of the network. A ranked "AI search" over the SOP binder was also rejected: the night lead could not explain why one playbook would win.

So the first release is a deterministic policy plus the SOP they already use. Citations are mandatory. If a future phase adds a model, it still has to quote the same sources and pass the same eval file.

## In scope

- Nightly shipment CSV and ticket CSV, the columns in `data/`
- Risk score the dispatch lead can recompute by hand
- SOP choice: medical, cold-chain, or checkpoint delay
- First three steps, with citations
- Audit event: who looked up which shipment and what band came back

## Out of scope

- Replacing the TMS
- Driver mobile workflow
- Writing back into the ticket system
- Training a model on their history
- Promising a revised ETA to the shipper

## Open questions for week 1 on a real export

- Is `hours_since_checkpoint` already on the extract, or do we compute it from event time?
- Which ticket statuses count as open besides `open`?
- Who is allowed to see medical shipments?
