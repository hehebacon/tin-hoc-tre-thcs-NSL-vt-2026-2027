from dataclasses import dataclass, field

@dataclass
class TaskStep:
    name: str
    action: str
    target: tuple | None = None
    completed: bool = False

@dataclass
class TaskProfile:
    name: str
    steps: list[TaskStep] = field(default_factory=list)

class TaskEngine:
    def __init__(self):
        self.profile = TaskProfile("IDLE")
        self.index = 0
        self.active = False

    def load_rescue(self, base, victim):
        self.profile = TaskProfile("RESCUE_DEMO", [
            TaskStep("LEAVE_BASE", "NAVIGATE", base),
            TaskStep("SEARCH_TARGET", "SEARCH", victim),
            TaskStep("CONFIRM_TARGET", "CONFIRM", victim),
            TaskStep("RETURN_BASE", "RETURN", base),
            TaskStep("FINISH", "FINISH", base),
        ])
        self.index = 0
        self.active = True

    def current(self):
        return self.profile.steps[self.index] if self.active and self.index < len(self.profile.steps) else None

    def complete_current(self):
        step = self.current()
        if step is None: return False
        step.completed = True
        self.index += 1
        if self.index >= len(self.profile.steps): self.active = False
        return True

    def snapshot(self):
        current = self.current()
        return {
            "profile": self.profile.name, "active": self.active,
            "index": self.index, "total": len(self.profile.steps),
            "current": current.name if current else "COMPLETE",
            "steps": [{"name": s.name, "action": s.action, "completed": s.completed} for s in self.profile.steps],
        }
