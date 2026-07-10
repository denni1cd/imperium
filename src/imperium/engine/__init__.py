"""Controlled lifecycle and information-boundary helpers."""

from imperium.engine.context import ContextBuilder, artifact_reference
from imperium.engine.lifecycle import InvalidTransition, LifecycleState

__all__ = [
    "ContextBuilder",
    "InvalidTransition",
    "LifecycleState",
    "artifact_reference",
]
