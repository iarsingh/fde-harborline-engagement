# Success metrics

Agree these before writing the scorer. A demo that "answers questions" is not the engagement.

## Customer-reported baseline

The night dispatch lead timed the current path, not a benchmark we invented after the fact:

- 25 to 40 minutes to answer "why is this late?" on a reefer or medical load
- The answer is verbal. Nothing records which SOP was used.
- Missed grocery and medical windows are the cost the VP tracks. This pilot does not pretend to move that number in week 1.

## Pilot metrics

| Metric | Target for the shadow week | How it is measured |
| --- | --- | --- |
| Time to a cited answer | Under 2 minutes on the sample questions, then on 20 real lookups | Dispatcher starts a timer, stops when the steps are on screen |
| Citation coverage | 100% of answers cite the shipment row and the SOP | Eval file plus a spot check of `/audit` |
| Policy agreement | Dispatch lead agrees with the band on 9 of 10 reviewed shipments | Side-by-side with the lead, disagreements become rule changes |
| Eval gate | `python -m harborline eval` exits 0 | CI on every change |
| Data leaving the environment | Zero outbound model or analytics calls | Design review, then a runtime network check in their VPC |

## What we will not claim

This sample does not prove a reduction in missed deliveries. The readout says that plainly. The number to earn in a real week 1 is time-to-cited-answer on their export, plus agreement with the lead.
