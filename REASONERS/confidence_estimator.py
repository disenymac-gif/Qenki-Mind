from .base_reasoner import BaseReasoner

class ConfidenceEstimator(BaseReasoner):
    def run(self, evidence_set):
        score = sum(item.get("weight", 0.0) for item in evidence_set)
        return round(min(score, 1.0), 2)
