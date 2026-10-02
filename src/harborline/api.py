from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from harborline.copilot import answer_question
from harborline.ingest import load_store
from harborline.models import ShipmentNotFound

app = FastAPI(title="Harborline Dispatch Copilot", version="0.1.0")
store = load_store()
audit_log: list[dict[str, object]] = []


class AskRequest(BaseModel):
    shipment_id: str = Field(min_length=1)
    question: str = Field(min_length=1)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "shipments": len(store.shipments)}


@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: str) -> dict[str, object]:
    try:
        shipment = store.shipment(shipment_id)
    except ShipmentNotFound as exc:
        raise HTTPException(status_code=404, detail=f"Unknown shipment {shipment_id}") from exc
    return {
        "shipment_id": shipment.shipment_id,
        "customer": shipment.customer,
        "lane": shipment.lane,
        "status": shipment.status,
        "checkpoint": shipment.checkpoint,
    }


@app.post("/ask")
def ask(body: AskRequest) -> dict[str, object]:
    try:
        answer = answer_question(store, body.shipment_id, body.question)
    except ShipmentNotFound as exc:
        raise HTTPException(status_code=404, detail=f"Unknown shipment {body.shipment_id}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    audit_log.append(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "shipment_id": answer.shipment_id,
            "band": answer.band,
            "score": answer.score,
            "citation_count": len(answer.citations),
        }
    )
    return {
        "shipment_id": answer.shipment_id,
        "band": answer.band,
        "score": answer.score,
        "reasons": list(answer.reasons),
        "sop_title": answer.sop_title,
        "steps": list(answer.steps),
        "citations": list(answer.citations),
        "text": answer.render(),
    }


@app.get("/audit")
def audit() -> dict[str, object]:
    return {"events": audit_log}
