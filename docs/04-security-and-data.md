# Security and data

## Rule from IT

Shipment and ticket data stay in the customer environment. The service must run with no dependency on a third-party model endpoint.

## What the process is allowed to read

- `data/shipments.csv`
- `data/tickets.csv`
- `data/sops/*.md`

On a real deployment those paths become a mounted bucket or a nightly drop on a VM in their VPC. The code does not take a URL for the model and does not embed an API client.

## What the audit log keeps

| Field | Kept | Reason |
| --- | --- | --- |
| Time | yes | Reconstruct a lookup during a missed-delivery review |
| Shipment id | yes | Join back to the TMS, which is already their system of record |
| Band and score | yes | Show what the desk was told |
| Citation count | yes | Catch empty answers |
| Question text | no | Free text can contain a customer name beyond the id |
| Ticket summary | no | The summary can describe a medical load |

`GET /audit` is the whole trail. There is no separate analytics sink.

## Access

This sample has no login. Before a second desk uses it, put it behind their SSO and restrict medical shipments to the medical desk. That is called out in the rollout plan because the sample data already includes Harbor Medical.

## Deployment shape

One container. No sidecar that phones home. The Dockerfile copies the app and the sample data so a reviewer can run it. In their environment, sample data is replaced by the mounted export and is not baked into the image.
