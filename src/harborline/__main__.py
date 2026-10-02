from __future__ import annotations

import sys

from harborline.copilot import answer_question
from harborline.eval import run
from harborline.ingest import load_store
from harborline.models import ShipmentNotFound


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "eval":
        return run()
    shipment_id = sys.argv[1] if len(sys.argv) > 1 else "SHP-1042"
    question = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "Why is this shipment late and what should dispatch do?"
    )
    try:
        answer = answer_question(load_store(), shipment_id, question)
    except ShipmentNotFound:
        print(f"Unknown shipment {shipment_id}", file=sys.stderr)
        return 1
    print(answer.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
