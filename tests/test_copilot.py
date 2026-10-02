from harborline.copilot import answer_question, select_sop
from harborline.ingest import load_store
from harborline.models import ShipmentNotFound
from harborline.risk import score_shipment

STORE = load_store()


def test_high_risk_reefer_breaks_down_every_point():
    shipment = STORE.shipment("SHP-1042")
    risk = score_shipment(shipment, STORE.tickets_for("SHP-1042"))
    assert risk.score == 76
    assert risk.band == "high"
    assert any("+26" in reason for reason in risk.reasons)
    assert any("TCK-19" in reason for reason in risk.reasons)
    assert any("+20" in reason for reason in risk.reasons)


def test_on_time_dry_van_is_low_risk():
    shipment = STORE.shipment("SHP-1108")
    risk = score_shipment(shipment, STORE.tickets_for("SHP-1108"))
    assert risk.score == 0
    assert risk.band == "low"
    assert risk.reasons == ()


def test_weather_hold_is_medium_risk():
    risk = score_shipment(STORE.shipment("SHP-1201"), STORE.tickets_for("SHP-1201"))
    assert risk.score == 41
    assert risk.band == "medium"


def test_delivered_shipment_ignores_stale_checkpoint_and_closed_ticket():
    risk = score_shipment(STORE.shipment("SHP-0770"), STORE.tickets_for("SHP-0770"))
    assert risk.score == 0
    assert risk.band == "low"


def test_medical_customer_selects_medical_sop_ahead_of_reefer():
    assert select_sop(STORE.shipment("SHP-0988"), "what should we do?") == "Medical priority"


def test_answer_cites_shipment_ticket_and_sop():
    answer = answer_question(STORE, "SHP-1042", "Why is this reefer shipment late?")
    assert answer.sop_title == "Cold-chain exception"
    assert answer.steps[0].startswith("Confirm the last temperature")
    assert "data/shipments.csv#SHP-1042" in answer.citations
    assert "data/tickets.csv#TCK-19" in answer.citations
    assert any(citation.startswith("data/sops/cold-chain-exception.md") for citation in answer.citations)
    assert "score 76" in answer.render()


def test_unknown_shipment_is_rejected():
    try:
        answer_question(STORE, "SHP-0000", "Where is it?")
    except ShipmentNotFound as exc:
        assert "SHP-0000" in str(exc)
    else:
        raise AssertionError("expected ShipmentNotFound")
