from fastapi.testclient import TestClient

from harborline.api import app, audit_log

client = TestClient(app)


def setup_function():
    audit_log.clear()


def test_health_reports_the_export_size():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["shipments"] == 6


def test_ask_returns_cited_steps_and_writes_a_thin_audit_event():
    response = client.post(
        "/ask",
        json={"shipment_id": "SHP-1042", "question": "Why is this reefer shipment late?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["band"] == "high"
    assert body["score"] == 76
    assert body["steps"]
    assert body["citations"]
    events = client.get("/audit").json()["events"]
    assert len(events) == 1
    assert events[0]["shipment_id"] == "SHP-1042"
    assert "question" not in events[0]
    assert "summary" not in events[0]


def test_unknown_shipment_is_404():
    response = client.post("/ask", json={"shipment_id": "SHP-0000", "question": "Where is it?"})
    assert response.status_code == 404


def test_blank_question_is_rejected():
    response = client.post("/ask", json={"shipment_id": "SHP-1108", "question": ""})
    assert response.status_code == 422
