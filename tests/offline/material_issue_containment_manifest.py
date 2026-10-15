"""OFFLINE ONLY: review synthetic isolation declarations for Material Issue risks.

This is not a tracer, patch, device, network check, or authorization gate.
Even an apparently complete manifest is UNTRUSTED and never authorizes a test.
"""
from dataclasses import dataclass


ISOLATED_SITE = "ccpc-integration2.localhost"
SURFACES = frozenset({
    "sql.driver", "sql.transaction", "sql.child_delete", "sql.series",
    "redis.cache_keys", "redis.cache_pubsub", "redis.queue_pubsub",
    "redis.background_jobs", "redis.search_queue", "process.cache",
    "document.hooks", "transaction.callbacks", "filesystem.external",
    "backup.recovery",
})
MODES = frozenset({"unknown", "shared", "site_prefix_only", "proposed_isolation", "proposed_capture"})
EVIDENCE = frozenset({"source_only", "synthetic", "asserted_runtime"})
REDIS_SURFACES = frozenset(s for s in SURFACES if s.startswith("redis."))


class InvalidManifest(ValueError):
    """Invalid synthetic declaration: NEVER silently ignore a route."""


@dataclass(frozen=True)
class BoundaryClaim:
    site: str
    surface: str
    mode: str
    evidence: str
    endpoint_alias: str | None = None

    def __post_init__(self):
        if self.site != ISOLATED_SITE:
            raise InvalidManifest("Site identity mismatch")
        if self.surface not in SURFACES or self.mode not in MODES:
            raise InvalidManifest("Unknown effect surface or isolation mode")
        if self.evidence not in EVIDENCE:
            raise InvalidManifest("Unknown evidence category")
        if self.endpoint_alias is not None and (
            type(self.endpoint_alias) is not str or
            not self.endpoint_alias or len(self.endpoint_alias) > 100
        ):
            raise InvalidManifest("Endpoint alias must be an opaque nonempty label")
        if self.surface not in REDIS_SURFACES and self.endpoint_alias is not None:
            raise InvalidManifest("Endpoint alias only applicable to Redis review paths")


def review_containment_manifest(claims: tuple[BoundaryClaim, ...]) -> dict:
    """Describe unproven boundaries without certifying the submitted claims.

    Even a perfectly complete set of 'asserted_runtime' declarations is NOT
    independent evidence of installed-site sink capture or physical isolation.
    """
    if type(claims) is not tuple or any(type(c) is not BoundaryClaim for c in claims):
        raise InvalidManifest("Claims must be a tuple of typed immutable declarations")
    surfaces = [c.surface for c in claims]
    if len(surfaces) != len(set(surfaces)):
        raise InvalidManifest("Duplicate surface declarations")
    by_surface = {c.surface: c for c in claims}
    missing = tuple(sorted(SURFACES.difference(by_surface)))
    unreviewed = tuple(sorted(
        c.surface for c in claims if c.mode in {"unknown", "shared", "site_prefix_only"}
    ))
    # Explicitly detect merely *declared* overlap. Distinct aliases prove nothing
    # about real endpoints, Docker networks, ACLs or worker consumer isolation.
    alias_groups: dict[str, set[str]] = {}
    for c in claims:
        if c.surface in REDIS_SURFACES and c.endpoint_alias is not None:
            alias_groups.setdefault(c.endpoint_alias, set()).add(c.surface)
    declared_endpoint_overlap = tuple(sorted(
        (alias, tuple(sorted(names))) for alias, names in alias_groups.items()
        if len(names) > 1
    ))
    claimed_isolated = tuple(sorted(
        c.surface for c in claims if c.mode == "proposed_isolation"
    ))
    claimed_captured = tuple(sorted(
        c.surface for c in claims if c.mode == "proposed_capture"
    ))
    return {
        "site": ISOLATED_SITE,
        "surface_count": len(SURFACES),
        "missing_surfaces": missing,
        "shared_or_unknown_surfaces": unreviewed,
        "proposed_isolation_claims": claimed_isolated,
        "proposed_capture_claims": claimed_captured,
        "declared_redis_endpoint_overlap": declared_endpoint_overlap,
        "all_named_surfaces_declared": not missing,
        "actual_runtime_sinks_exhaustively_known": False,
        "actual_hook_binding_and_order_verified": False,
        "physical_redis_and_worker_isolation_verified": False,
        "no_implicit_commit_or_ddl_verified": False,
        "child_delete_and_series_concurrency_verified": False,
        "external_effect_compensation_verified": False,
        "backups_and_rollback_recovery_verified": False,
        "owner_authorized_live_stage": False,
        "safe_to_stage": False,
        "safe_to_rehearse": False,
        "safe_to_commit": False,
        "decision": "NO_GO_SOURCE_ONLY",
    }
