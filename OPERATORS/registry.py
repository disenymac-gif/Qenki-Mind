class OperatorRegistry:
    def __init__(self):
        self._ops = {}

    def register(self, name, operator_cls):
        self._ops[name] = operator_cls

    def get(self, name):
        return self._ops[name]

    def available(self):
        return sorted(self._ops.keys())
