"""OFFLINE ONLY: model why SQL rollback cannot erase external effect attempts.

This is not an event tracer, Frappe hook, Redis/SQL client, or execution guard.
All inputs are synthetic review fixtures, never observed transaction records.
"""
from dataclasses import dataclass


SITE = "ccpc-integration2.localhost"
KINDS = frozenset({
    "sql_dml", "sql_rollback", "redis_queue_push", "redis_unlink",
    "redis_pubsub", "process_cache_invalidation", "callback_registration",
    "callback_invocation", "unknown_effect",
})
PHASES = frozenset({"precommit", "after_commit", "full_rollback", "savepoint", "unknown"})
EXTERNAL_KINDS = frozenset({
    "redis_queue_push", "redis_unlink", "redis_pubsub",
    "process_cache_invalidation", "callback_invocation", "unknown_effect",
})


class InvalidSyntheticTimeline(ValueError):
    """Reject ambiguous or malformed hypothetical event evidence."""


@dataclass(frozen=True)
class HypotheticalEffect:
    sequence: int
    site: str
    kind: str
    phase: str
    label: str

    def __post_init__(self):
        if type(self.sequence) is not int or self.sequence < 1:
            raise InvalidSyntheticTimeline("Sequence must be a positive integer")
        if self.site != SITE:
            raise InvalidSyntheticTimeline("Not the specified isolated site")
        if self.kind not in KINDS or self.phase not in PHASES:
            raise InvalidSyntheticTimeline("Unknown effect kind or phase")
        if type(self.label) is not str or not self.label or len(self.label) > 100:
            raise InvalidSyntheticTimeline("Missing or oversized symbolic effect label")
        if self.kind == "callback_registration" and self.phase not in {"precommit", "unknown"}:
            raise InvalidSyntheticTimeline("Callback registration should not be labeled as invocation")
        if self.kind == "sql_rollback" and self.phase not in {"full_rollback", "savepoint"}:
            raise InvalidSyntheticTimeline("Rollback marker has wrong phase")


def inspect_synthetic_timeline(effects: tuple[HypotheticalEffect, ...]) -> dict:
    """Expose risks without ever approving a live operation or COMMIT."""
    if type(effects) is not tuple or any(type(e) is not HypotheticalEffect for e in effects):
        raise InvalidSyntheticTimeline("Effects must be a tuple of exact immutable event types")
    sequences = [e.sequence for e in effects]
    if sequences != sorted(set(sequences)):
        raise InvalidSyntheticTimeline("Sequence missing monotonic uniqueness")
    rollback_positions = [i for i, e in enumerate(effects) if e.kind == "sql_rollback"]
    pre_rollback = effects[:rollback_positions[0]] if rollback_positions else effects
    # An earlier external effect remains a risk even if a later SQL rollback exists.
    external_before_rollback = tuple(e.label for e in pre_rollback if e.kind in EXTERNAL_KINDS)
    all_external = tuple(e.label for e in effects if e.kind in EXTERNAL_KINDS)
    registered = tuple(e.label for e in effects if e.kind == "callback_registration")
    unknown = tuple(e.label for e in effects if e.kind == "unknown_effect" or e.phase == "unknown")
    return {
        "synthetic_only": True,
        "site": SITE,
        "event_count": len(effects),
        "sql_rollback_markers": len(rollback_positions),
        "external_effects_before_first_rollback": external_before_rollback,
        "all_external_effects": all_external,
        "registered_callbacks_not_proof_of_invocation": registered,
        "unresolved_unknown_events": unknown,
        "sql_rollback_cannot_reverse_external_effects": bool(all_external),
        "actual_effect_capture_verified": False,
        "isolated_redis_endpoint_verified": False,
        "process_and_shared_cache_contained": False,
        "all_runtime_hooks_verified": False,
        "rollback_delta_verified": False,
        "safe_to_stage": False,
        "safe_to_rehearse": False,
        "safe_to_commit": False,
        "decision": "NO_GO_SOURCE_ONLY",
    }
