from OPERATORS.engine import CognitiveOperator
import entity_markdown as em
import prediction_representation as pr


class Operator(CognitiveOperator):
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def inputs(self):
        return ['expression_path', 'evidence']

    def validate(self, expression_path, evidence, **kwargs):
        if not evidence:
            return False
        sections = em.load_entity(expression_path)
        predictions = pr.parse_predictions(sections['Predictions'])
        pr.validate_predictions(predictions)
        return True

    def execute(self, expression_path, evidence, **kwargs):
        sections = em.load_entity(expression_path)
        predictions = pr.parse_predictions(sections['Predictions'])
        predictions, changed = pr.resolve_predictions(predictions, evidence)
        sections['Predictions'] = pr.serialize_predictions(predictions)
        date_str = kwargs.get('date', 'unknown')
        history_entry = '\n- ' + date_str + ': Resolved predictions ' + str(list(evidence.keys())) + ' via ExpressionToConsequence.'
        sections['Change History'] = sections.get('Change History', '') + history_entry
        return {'sections': sections, 'changed': changed, 'path': expression_path}

    def persist(self, result, **kwargs):
        if result['changed']:
            em.save_entity(result['path'], result['sections'])
        return result['path']

    def emit_events(self, result, **kwargs):
        if not self.event_bus:
            return []
        event = self.event_bus.emit(
            'OperatorExecuted',
            self.__class__.__name__,
            str(result['path']),
            payload={'changed': result['changed']},
        )
        return [event]
