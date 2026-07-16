from engine import CognitiveEngine
from entity_markdown import load_entity


class DummyRegistry:
    def get(self, operator):
        raise KeyError(operator)


def test_session_is_persisted(tmp_path):
    engine = CognitiveEngine(registry=DummyRegistry(), base=tmp_path)
    session = engine.start_session(
        "trigger-x",
        "root-entity",
        world_state_snapshot="world",
        objectives_snapshot="goal",
        memory_loaded=["mem-1", "mem-2"],
    )
    session.operators_executed.extend(["LearningToMemory", "MemoryToReasoning"])
    session.events_emitted.extend(["evt-001", "evt-002"])
    session.artifacts_created.extend(["/tmp/a.md", "/tmp/b.md"])
    session.close("Completed")

    path = engine._persist_session(session)

    assert path == tmp_path / "SESSIONS" / f"{session.session_id}.md"
    assert path.exists()

    parsed = load_entity(path)
    assert parsed["Session ID"] == session.session_id
    assert parsed["Trigger"] == "trigger-x"
    assert parsed["Root Entity"] == "root-entity"
    assert parsed["World State Snapshot"] == "world"
    assert parsed["Objectives Snapshot"] == "goal"
    assert "- mem-1" in parsed["Memory Loaded"]
    assert "- mem-2" in parsed["Memory Loaded"]
    assert "- LearningToMemory" in parsed["Operators Executed"]
    assert "- MemoryToReasoning" in parsed["Operators Executed"]
    assert "- evt-001" in parsed["Events Emitted"]
    assert "- evt-002" in parsed["Events Emitted"]
    assert "- /tmp/a.md" in parsed["Artifacts Created"]
    assert "- /tmp/b.md" in parsed["Artifacts Created"]
    assert parsed["Final State"] == "Completed"