from .base_reasoner import BaseReasoner

class DecisionSelector(BaseReasoner):
    def run(self, opportunity, confidence):
        selected = confidence >= 0.5
        rationale = (
            f"Selected {opportunity} because confidence {confidence:.2f} met the decision threshold."
            if selected else
            f"Did not select {opportunity} because confidence {confidence:.2f} was below the decision threshold."
        )
        predictions = [
            f"If pursued, {opportunity} will produce observable downstream consequences for later learning.",
            f"If pursued, {opportunity} should remain explainable through its evidence set and linked objectives.",
        ] if selected else []
        return {
            "selected": selected,
            "rationale": rationale,
            "predictions": predictions,
        }
