"""JSON output renderer."""

from __future__ import annotations

import json

from leakshield.models import ScanResult
from leakshield.reporting.schema import result_to_dict


def render_json(result: ScanResult) -> str:
    return json.dumps(result_to_dict(result), indent=2, sort_keys=False)

