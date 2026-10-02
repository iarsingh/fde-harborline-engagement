# Customer readout

**To:** VP of operations, Harborline Freight
**Subject:** Night-desk pilot is ready to shadow, not to replace the TMS

## What we heard

Dispatchers spend 25 to 40 minutes answering why a reefer or medical shipment is late. The time goes to finding the TMS row, the ticket, and the SOP. IT will not send that data to an outside model.

## What is running

A small service in your environment reads the nightly export and the ticket file. For a shipment id it returns a score, the reason for every point, the SOP your night lead already uses, and the first three steps. Every answer cites the row it used.

On the sample set your lead walked through:

| Shipment | Score | What it told the desk |
| --- | --- | --- |
| SHP-1042 Northwind reefer | 76 high | Cold-chain exception, because of the temp alarm and P1 |
| SHP-0988 Harbor Medical | 74 high | Medical priority, even though the trailer is a reefer |
| SHP-1201 PeakOutfit weather hold | 41 medium | Checkpoint delay |
| SHP-0770 MetroParts delivered | 0 low | Closed ticket and delivered status add no risk |

## What we are not claiming

We have not reduced missed deliveries. We have a shadow-week test: 20 real lookups, under 2 minutes each, and your lead agrees with the band on at least 9 of 10. If that holds, week 2 is the night desk only, reefer and medical loads.

## What we need from you

- The real column names on the nightly extract
- Confirmation that medical shipments stay on the medical desk
- One IT owner for the file drop after we leave

Rollback is turning the service off. It does not write to the TMS.
