from pathlib import Path
from datetime import datetime, timezone
from collections import OrderedDict
from .registry import OperatorRegistry
from entity_markdown import save_entity

class EventBus:
    def __init__(self):
        self.events = []

    def emit(self, event_type, operator, source_entity, target_entity=None, payload=None):
        event = {
            "event_id": f"evt-{len(self.events)+1:06d}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "operator": operator,
            "source_entity": source_entity,
            "target_entity": target_entity,
            "payload": payload or {},
        }
        self.events.append(event)
        return event

class CognitiveSession:
    def __init__(self, trigger, root_entity, world_state_snapshot=None, objectives_snapshot=None, memory_loaded=None):
        self.session_id = f"ses-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        self.trigger = trigger
        self.root_entity = root_entity
        self.world_state_snapshot = world_state_snapshot
        self.objectives_snapshot = objectives_snapshot
        self.memory_loaded = memory_loaded or []
        self.operators_executed = []
        self.events_emitted = []
        self.artifacts_created = []
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.final_state = "Running"

    def close(self, final_state="Completed"):
        self.end_time = datetime.now(timezone.utc)
        self.final_state = final_state

class CognitiveOperator:
    def inputs(self):
        raise NotImplementedError
    def validate(self, *args, **kwargs):
        raise NotImplementedError
    def execute(self, *args, **kwargs):
        raise NotImplementedError
    def persist(self, *args, **kwargs):
        raise NotImplementedError
    def emit_events(self, *args, **kwargs):
        raise NotImplementedError

class OperatorRunResult:
    def __init__(self, result, artifact, events):
        self.result = result
        self.artifact = artifact
        self.events = events

class CognitiveEngine:
    def __init__(self, registry=None, event_bus=None, base=None):
        self.registry = registry or OperatorRegistry()
        self.event_bus = event_bus or EventBus()
        self.base = Path(base) if base is not None else Path(__file__).resolve().parents[1]

    def start_session(self, trigger, root_entity, world_state_snapshot=None, objectives_snapshot=None, memory_loaded=None):
        return CognitiveSession(trigger, root_entity, world_state_snapshot, objectives_snapshot, memory_loaded)

    def _persist_session(self, session):
        sessions_dir = self.base / "SESSIONS"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        path = sessions_dir / f"{session.session_id}.md"
        sections = OrderedDict([
            ("Session ID", session.session_id),
            ("Trigger", str(session.trigger)),
            ("Root Entity", str(session.root_entity)),
            ("World State Snapshot", "" if session.world_state_snapshot is None else str(session.world_state_snapshot)),
            ("Objectives Snapshot", "" if session.objectives_snapshot is None else str(session.objectives_snapshot)),
            ("Memory Loaded", "\n".join(f"- {item}" for item in session.memory_loaded)),
            ("Operators Executed", "\n".join(f"- {item}" for item in session.operators_executed)),
            ("Events Emitted", "\n".join(f"- {item}" for item in session.events_emitted)),
            ("Artifacts Created", "\n".join(f"- {item}" for item in session.artifacts_created)),
            ("Start Time", session.start_time.isoformat()),
            ("End Time", "" if session.end_time is None else session.end_time.isoformat()),
            ("Final State", session.final_state),
        ])
        save_entity(path, sections, section_order=list(sections.keys()))
        return path

    def _run_operator(self, operator, entity, session=None, **kwargs):
        op_cls = self.registry.get(operator)
        op = op_cls(self.event_bus)
        op.validate(entity, session=session, **kwargs)
        result = op.execute(entity, session=session, **kwargs)
        artifact = op.persist(result, session=session, **kwargs)
        emitted = op.emit_events(result, session=session, **kwargs)
        emitted = emitted if isinstance(emitted, list) else ([emitted] if emitted else [])
        if session is not None:
            session.operators_executed.append(operator)
            if artifact is not None:
                session.artifacts_created.append(str(artifact))
            if emitted:
                session.events_emitted.extend(emitted)
        return OperatorRunResult(result=result, artifact=artifact, events=emitted)

    def run(self, operator, entity, session=None, **kwargs):
        run_result = self._run_operator(operator, entity, session=session, **kwargs)
        return run_result.artifact

    def run_pipeline(self, entity, pipeline, session=None, **kwargs):
        current = entity
        for operator in pipeline:
            run_result = self._run_operator(operator, current, session=session, **kwargs)
            current = run_result.artifact
        if session is not None:
            session.close("Completed")
            self._persist_session(session)
        return current