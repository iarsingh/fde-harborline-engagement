from __future__ import annotations

from harborline.models import Risk, Shipment, Ticket

HIGH_BAND = 70
MEDIUM_BAND = 40


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
        reasons.append("TMS status is exception (+25)")

    p1 = [ticket for ticket in open_tickets if ticket.priority == "P1"]
    if p1:
        score += 30
        listed = ", ".join(f"{ticket.ticket_id}: {ticket.summary}" for ticket in p1)
        reasons.append(f"Open P1 ticket {listed} (+30)")
    elif open_tickets:
        score += 15
        listed = ", ".join(ticket.ticket_id for ticket in open_tickets)
        reasons.append(f"Open ticket {listed} (+15)")

    if shipment.cargo_type == "reefer" and "temp" in shipment.last_event.lower():
        score += 20
        reasons.append(f"Reefer cargo has a temperature event: {shipment.last_event} (+20)")

    score = min(score, 100)
    if score >= HIGH_BAND:
        band = "high"
    elif score >= MEDIUM_BAND:
        band = "medium"
    else:
        band = "low"
    return Risk(score=score, band=band, reasons=tuple(reasons), open_tickets=open_tickets)
