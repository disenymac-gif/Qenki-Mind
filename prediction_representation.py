import re


class DuplicatePredictionIdError(Exception):
    def __init__(self, duplicate_ids):
        self.duplicate_ids = duplicate_ids
        super().__init__('Duplicate prediction ids found: ' + str(sorted(duplicate_ids)))


PREDICTION_PATTERN = re.compile(
    r'^-\s*\[(?P<id>[\w-]+)\]\s*(?P<statement>.*?)\s*\(state:\s*(?P<state>\w+)\)\s*$'
)


def parse_predictions(predictions_text):
    results = []
    for line in predictions_text.splitlines():
        line = line.strip()
        if not line.startswith('-'):
            continue
        m = PREDICTION_PATTERN.match(line)
        if m:
            results.append(m.groupdict())
        else:
            results.append({'id': None, 'statement': line.lstrip('- ').strip(), 'state': None})
    return results


def serialize_predictions(predictions):
    lines = []
    for p in predictions:
        if p.get('id') and p.get('state'):
            lines.append('- [' + p['id'] + '] ' + p['statement'] + ' (state: ' + p['state'] + ')')
        else:
            lines.append('- ' + p['statement'])
    return '\n'.join(lines)


def find_duplicate_ids(predictions):
    seen = set()
    duplicates = set()
    for p in predictions:
        pid = p.get('id')
        if pid is None:
            continue
        if pid in seen:
            duplicates.add(pid)
        else:
            seen.add(pid)
    return duplicates


def validate_predictions(predictions):
    duplicates = find_duplicate_ids(predictions)
    if duplicates:
        raise DuplicatePredictionIdError(duplicates)
    return True


def resolve_predictions(predictions, evidence):
    validate_predictions(predictions)
    changed = False
    for p in predictions:
        if p.get('id') in evidence:
            p['state'] = evidence[p['id']]
            changed = True
    return predictions, changed


def resolved_predictions(predictions):
    return [p for p in predictions if p.get('state') and p['state'] != 'pending']


def has_resolved_predictions(predictions):
    return len(resolved_predictions(predictions)) > 0
