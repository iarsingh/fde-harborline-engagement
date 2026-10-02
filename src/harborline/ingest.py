from __future__ import annotations

import csv
import re
from pathlib import Path

from harborline.models import Shipment, SopSection, Store, Ticket

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
EVALS_PATH = ROOT / "evals" / "questions.jsonl"
STEP_RE = re.compile(r"^\d+\.\s+(.*\S)\s*$")


def load_store(data_dir: Path | None = None) -> Store:
    data_dir = data_dir or DATA_DIR
    return Store(
        shipments=_load_shipments(data_dir / "shipments.csv"),
        tickets=_load_tickets(data_dir / "tickets.csv"),
        sops=_load_sops(data_dir / "sops"),
    )


def _load_shipments(path: Path) -> dict[str, Shipment]:
    shipments: dict[str, Shipment] = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            shipment = Shipment(
                shipment_id=row["shipment_id"],
                customer=row["customer"],
                lane=row["lane"],
                status=row["status"],
                checkpoint=row["checkpoint"],
                hours_since_checkpoint=int(row["hours_since_checkpoint"]),
                checkpoint_sla_hours=int(row["checkpoint_sla_hours"]),
                cargo_type=row["cargo_type"],
                last_event=row["last_event"],
            )
            shipments[shipment.shipment_id] = shipment
    return shipments


def _load_tickets(path: Path) -> list[Ticket]:
    with path.open(newline="") as handle:
        return [
            Ticket(
                ticket_id=row["ticket_id"],
                shipment_id=row["shipment_id"],
                priority=row["priority"],
                status=row["status"],
                summary=row["summary"],
            )
            for row in csv.DictReader(handle)
        ]


def _load_sops(directory: Path) -> list[SopSection]:
    sections: list[SopSection] = []
    for path in sorted(directory.glob("*.md")):
        title = ""
        steps: list[str] = []
        for raw_line in path.read_text().splitlines():
            line = raw_line.strip()
            if line.startswith("## "):
                title = line[3:].strip()
                continue
            match = STEP_RE.match(line)
            if match:
                steps.append(match.group(1))
        if not title or not steps:
            raise ValueError(f"{path} needs a heading and numbered steps")
        relative = path.relative_to(directory.parents[1]).as_posix()
        sections.append(SopSection(path=relative, title=title, steps=tuple(steps)))
    return sections
