from __future__ import annotations

from dataclasses import dataclass, field


class ShipmentNotFound(KeyError):
    """Raised when a shipment id is not in the customer export."""


@dataclass(frozen=True)
class Shipment:
    shipment_id: str
    customer: str
    lane: str
    status: str
    checkpoint: str
    hours_since_checkpoint: int
    checkpoint_sla_hours: int
    cargo_type: str
    last_event: str


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    shipment_id: str
    priority: str
    status: str
    summary: str


@dataclass(frozen=True)
class SopSection:
    path: str
    title: str
    steps: tuple[str, ...]


@dataclass
class Store:
    shipments: dict[str, Shipment]
    tickets: list[Ticket]
    sops: list[SopSection]

    def shipment(self, shipment_id: str) -> Shipment:
        try:
            return self.shipments[shipment_id]
        except KeyError as exc:
            raise ShipmentNotFound(shipment_id) from exc

    def tickets_for(self, shipment_id: str) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.shipment_id == shipment_id]

    def sop(self, title: str) -> SopSection:
        for section in self.sops:
            if section.title == title:
                return section
        raise KeyError(title)


@dataclass(frozen=True)
class Risk:
    score: int
    band: str
    reasons: tuple[str, ...]
    open_tickets: tuple[Ticket, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Answer:
    shipment_id: str
    customer: str
    lane: str
    checkpoint: str
    hours_since_checkpoint: int
    checkpoint_sla_hours: int
    score: int
    band: str
    reasons: tuple[str, ...]
    sop_title: str
    steps: tuple[str, ...]
    citations: tuple[str, ...]

    def render(self) -> str:
        reason_lines = "\n".join(f"- {reason}" for reason in self.reasons) or "- No risk signals fired."
        step_lines = "\n".join(f"{index}. {step}" for index, step in enumerate(self.steps, start=1))
        citation_lines = "\n".join(f"- {citation}" for citation in self.citations)
        return (
            f"Shipment {self.shipment_id} is {self.band} risk (score {self.score}).\n"
            f"Customer {self.customer}, lane {self.lane}, last checkpoint {self.checkpoint}, "
            f"{self.hours_since_checkpoint}h since checkpoint (SLA {self.checkpoint_sla_hours}h).\n\n"
            f"Why:\n{reason_lines}\n\n"
            f"Do this ({self.sop_title}):\n{step_lines}\n\n"
            f"Citations:\n{citation_lines}\n"
        )
