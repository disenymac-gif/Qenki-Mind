"""
pytest configuration for Qenki-Mind test suite.

Ensures the repository root is on sys.path so that
`import entity_markdown`, `import prediction_representation`,
and `from OPERATORS import ...` all resolve correctly regardless
of how pytest is invoked.
"""
import sys
from pathlib import Path

# Repository root = parent of this file's parent directory
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))