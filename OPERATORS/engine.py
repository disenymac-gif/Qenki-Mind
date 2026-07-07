from pathlib import Path
from datetime import datetime, timezone
from .registry import OperatorRegistry

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

class CognitiveEngine:
    def __init__(self, registry=None, event_bus=None):
        self.registry = registry or OperatorRegistry()
        self.event_bus = event_bus or EventBus()

    def start_session(self, trigger, root_entity, world_state_snapshot=None, objectives_snapshot=None, memory_loaded=None):
        return CognitiveSession(trigger, root_entity, world_state_snapshot, objectives_snapshot, memory_loaded)

    def run(self, operator, entity, session=None, **kwargs):
        op_cls = self.registry.get(operator)
        op = op_cls(self.event_bus)
        op.validate(entity, session=session, **kwargs)
        result = op.execute(entity, session=session, **kwargs)
        artifact = op.persist(result, session=session, **kwargs)
        emitted = op.emit_events(result, session=session, **kwargs)
        if session is not None:
            session.operators_executed.append(operator)
            if artifact is not None:
                session.artifacts_created.append(str(artifact))
            if emitted:
                session.events_emitted.extend(emitted if isinstance(emitted, list) else [emitted])
        return result

    def run_pipeline(self, entity, pipeline, session=None, **kwargs):
        current = entity
        for operator in pipeline:
            current = self.run(operator, current, session=session, **kwargs)
        if session is not None:
            session.close("Completed")
        return current
