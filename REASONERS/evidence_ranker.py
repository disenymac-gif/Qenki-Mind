from .base_reasoner import BaseReasoner

class EvidenceRanker(BaseReasoner):
    def run(self, opportunity, world_state, objectives, memory):
        evidence = []
        if world_state:
            evidence.append({
                "evidence_id": "ev-world-state",
                "source": "WorldState",
                "summary": f"Opportunity evaluated against world state: {world_state}",
                "weight": 0.4,
            })
        if objectives:
            evidence.append({
                "evidence_id": "ev-objectives",
                "source": "Objectives",
                "summary": f"Opportunity alignment checked against objectives: {objectives}",
                "weight": 0.35,
            })
        for i, item in enumerate(memory or [], start=1):
            evidence.append({
                "evidence_id": f"ev-memory-{i:03d}",
                "source": "Memory",
                "summary": f"Relevant memory considered: {item}",
                "weight": 0.25 / max(len(memory), 1),
            })
        return sorted(evidence, key=lambda x: x["weight"], reverse=True)
