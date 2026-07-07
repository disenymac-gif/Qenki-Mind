from OPERATORS.engine import CognitiveOperator

class Operator(CognitiveOperator):
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
    def inputs(self):
        return []
    def validate(self, *args, **kwargs):
        return True
    def execute(self, *args, **kwargs):
        return {}
    def persist(self, *args, **kwargs):
        return None
    def emit_events(self, *args, **kwargs):
        if self.event_bus:
            self.event_bus.emit('OperatorExecuted', {'operator': self.__class__.__name__})
