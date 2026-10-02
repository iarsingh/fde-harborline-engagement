from __future__ import annotations

import json
from pathlib import Path

from harborline.copilot import answer_question
from harborline.ingest import EVALS_PATH, load_store


def run(path: Path | None = None) -> int:
    store = load_store()
    failures: list[str] = []
    cases = 0
    for line in (path or EVALS_PATH).read_text().splitlines():
        if not line.strip():
            continue
        cases += 1
        case = json.loads(line)
        answer = answer_question(store, case["shipment_id"], case["question"])
        if answer.band != case["expected_band"]:
            failures.append(
                f"{case['shipment_id']}: band {answer.band}, expected {case['expected_band']}"
            )
        expected_citation = case["expected_citation"]
        if expected_citation not in answer.citations and not any(
            expected_citation in citation for citation in answer.citations
        ):
            failures.append(f"{case['shipment_id']}: missing citation {expected_citation}")
        if not answer.steps:
            failures.append(f"{case['shipment_id']}: answer has no SOP steps")
    if failures:
        print(f"{len(failures)} eval failure(s) out of {cases}")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"{cases} eval cases passed")
    return 0
