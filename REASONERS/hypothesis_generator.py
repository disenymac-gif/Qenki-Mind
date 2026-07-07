from .base_reasoner import BaseReasoner

class HypothesisGenerator(BaseReasoner):
    def run(self, opportunity, evidence_set):
        if not evidence_set:
            return [f"The opportunity {opportunity} lacks sufficient evidence and should remain pending."]
        top = evidence_set[0]["summary"]
        return [
            f"Pursuing {opportunity} is justified because {top.lower()}",
            f"If selected, {opportunity} should improve alignment with current objectives.",
        ]
