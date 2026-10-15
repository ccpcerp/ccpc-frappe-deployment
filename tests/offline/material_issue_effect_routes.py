"""OFFLINE ONLY: pinned-source route model, never a runtime interception guard.

Paths are review hypotheses with explicit evidence level. Claiming a hook is not
proof that the hook runs, observes all calls or contains any external effect.
"""
from dataclasses import dataclass


class RouteReviewError(ValueError):
    """Fail-closed input validation for synthetic review declarations."""


@dataclass(frozen=True)
class EffectRoute:
    name: str
    nodes: tuple[str, ...]
    sink: str
    evidence: str  # 'pinned_source' or 'requires_source_review'


# Each route is limited to the cited pinned source steps. Unverified extension
# paths are explicitly hypothetical, NOT assertions of installed-site behavior.
ROUTES = (
    EffectRoute("child_qb_delete", ("document.child_sync", "qb.run", "db.sql", "db.execute_query", "cursor.execute"), "sql", "pinned_source"),
    EffectRoute("series_counter", ("naming.getseries", "db.sql", "db.execute_query", "cursor.execute"), "sql", "pinned_source"),
    EffectRoute("search_redis_push", ("document.post_save", "global_search.update", "global_search.queue", "cache.lpush", "redis.lpush"), "external", "pinned_source"),
    EffectRoute("search_sql_fallback", ("global_search.queue", "global_search.sync", "db.multisql", "db.sql", "db.execute_query", "cursor.execute"), "sql", "pinned_source"),
    EffectRoute("savepoint_sql", ("db.rollback_savepoint", "db.sql", "db.execute_query", "cursor.execute"), "sql", "pinned_source"),
    EffectRoute("document_cache", ("document.post_save", "document.clear_cache", "cache.unverified_mutation"), "external", "requires_source_review"),
    EffectRoute("realtime_dispatch", ("document.notify_update", "realtime.publish", "realtime.unverified_dispatch"), "external", "requires_source_review"),
    EffectRoute("commit_callbacks", ("db.commit", "callback.before_commit", "callback.unknown_effect"), "external", "requires_source_review"),
    EffectRoute("rollback_callbacks", ("db.rollback", "callback.before_rollback", "callback.unknown_effect"), "external", "requires_source_review"),
    EffectRoute("possible_cursor_bypass", ("unknown.direct_cursor_call", "cursor.execute"), "sql", "requires_source_review"),
    EffectRoute("possible_redis_bypass", ("unknown.direct_redis_call", "redis.lpush"), "external", "requires_source_review"),
    EffectRoute("document_custom_hooks", ("document.post_save", "document.on_change", "hook.unreviewed_effect"), "external", "requires_source_review"),
)

# These nodes are candidate observation *claims*, never proof of coverage.
CANDIDATE_HOOKS = frozenset({
    "qb.run", "db.multisql", "db.sql", "db.execute_query", "cursor.execute",
    "cache.lpush", "redis.lpush", "cache.unverified_mutation",
    "realtime.publish", "realtime.unverified_dispatch",
    "callback.before_commit", "callback.before_rollback", "callback.unknown_effect",
    "hook.unreviewed_effect",
})


def analyze_route_claims(claimed_hooks: tuple[str, ...], routes: tuple[EffectRoute, ...] = ROUTES) -> dict:
    """Find *theoretical* missing cuts. Always refuse runtime safety claims."""
    if type(claimed_hooks) is not tuple or any(type(h) is not str for h in claimed_hooks):
        raise RouteReviewError("Claims require a tuple of names")
    if len(set(claimed_hooks)) != len(claimed_hooks) or set(claimed_hooks) - CANDIDATE_HOOKS:
        raise RouteReviewError("Duplicate or unknown candidate hook")
    if type(routes) is not tuple or not routes or any(type(r) is not EffectRoute for r in routes):
        raise RouteReviewError("Routes must be a nonempty tuple of typed immutable paths")
    names = [r.name for r in routes]
    if len(set(names)) != len(names):
        raise RouteReviewError("Duplicate route identity")
    for r in routes:
        if (not r.name or type(r.nodes) is not tuple or len(r.nodes) < 2
                or any(type(n) is not str or not n for n in r.nodes)
                or r.sink not in {"sql", "external"}
                or r.evidence not in {"pinned_source", "requires_source_review"}):
            raise RouteReviewError("Invalid route declaration")
    claimed = set(claimed_hooks)
    uncovered = tuple(sorted(r.name for r in routes if not claimed.intersection(r.nodes)))
    unverified = tuple(sorted(r.name for r in routes if r.evidence != "pinned_source"))
    external = tuple(sorted(r.name for r in routes if r.sink == "external"))
    return {
        "mode": "SYNTHETIC_SOURCE_ONLY",
        "route_count": len(routes),
        "theoretically_uncovered_routes": uncovered,
        "routes_needing_source_review": unverified,
        "external_effect_routes": external,
        "all_declared_routes_intersect_claimed_hooks": not uncovered,
        "source_graph_exhaustive": False,
        "runtime_hook_binding_verified": False,
        "sql_driver_coverage_verified": False,
        "redis_endpoint_isolation_verified": False,
        "child_delete_row_predicates_verified": False,
        "rollback_external_effects_verified": False,
        "safe_to_rehearse": False,
        "safe_to_commit": False,
        "decision": "NO_GO",
    }
