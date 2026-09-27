class DecisionEngine:
    def decide(self, mode, safety_ok, found, person_confirmed, has_path, at_base):
        if not safety_ok: return "STOP"
        if mode == "PATROL": return "PATROL" if has_path else "PLAN_PATROL"
        if mode in ("RESCUE", "AUTONOMOUS"):
            if found: return "RETURN_HOME" if not at_base else "COMPLETE"
            if person_confirmed: return "CONFIRM_TARGET"
            return "SEARCH" if has_path else "PLAN_SEARCH"
        if mode == "OSINT": return "PUBLIC_DATA_SCAN"
        return "IDLE"
