from __future__ import annotations

from harborline.models import Answer, Shipment, Store
from harborline.risk import score_shipment

COLD_CHAIN = "Cold-chain exception"
MEDICAL = "Medical priority"
CHECKPOINT = "Checkpoint delay"


def select_sop(shipment: Shipment, question: str) -> str:
    """Pick the playbook with the rule the dispatch lead approved.

    A ranked search was rejected in discovery because the night desk could not
    explain why one SOP won. Medical cargo outranks a temperature event.
    """
    question_text = question.lower()
    if "medical" in shipment.customer.lower() or "medical" in question_text:
        return MEDICAL
    if shipment.cargo_type == "reefer" and "temp" in shipment.last_event.lower():
        return COLD_CHAIN
    return CHECKPOINT


def answer_question(store: Store, shipment_id: str, question: str) -> Answer:
    if not question.strip():
        raise ValueError("question is required")
    shipment = store.shipment(shipment_id)
    risk = score_shipment(shipment, store.tickets_for(shipment_id))
    sop = store.sop(select_sop(shipment, question))
    citations = [f"data/shipments.csv#{shipment.shipment_id}"]
    citations.extend(f"data/tickets.csv#{ticket.ticket_id}" for ticket in risk.open_tickets)
    citations.append(f"{sop.path}#{sop.title}")
    return Answer(
        shipment_id=shipment.shipment_id,
        customer=shipment.customer,
        lane=shipment.lane,
        checkpoint=shipment.checkpoint,
        hours_since_checkpoint=shipment.hours_since_checkpoint,
        checkpoint_sla_hours=shipment.checkpoint_sla_hours,
        score=risk.score,
        band=risk.band,
        reasons=risk.reasons,
        sop_title=sop.title,
        steps=sop.steps[:3],
        citations=tuple(citations),
    )
