"""Configuration components."""

from leakshield.config.merger import build_runtime_config
from leakshield.config.schema import LeakshieldConfig

__all__ = ["LeakshieldConfig", "build_runtime_config"]
