from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MissionEvent:
    timestamp: str
    event: str
    details: dict = field(default_factory=dict)


class MissionManager:
    def __init__(self):
        self.active = False
        self.name = "DEMO SEARCH"
        self.events = []

    def start(self, name="DEMO SEARCH"):
        self.active = True
        self.name = name
        self.add("MISSION_STARTED", {"name": name})

    def stop(self):
        self.active = False
        self.add("MISSION_STOPPED", {"name": self.name})

    def add(self, event, details=None):
        self.events.insert(0, MissionEvent(
            datetime.now().isoformat(timespec="seconds"),
            event,
            details or {},
        ))
        self.events = self.events[:50]

    def export(self):
        return [
            {"timestamp": e.timestamp, "event": e.event, "details": e.details}
            for e in self.events
        ]
