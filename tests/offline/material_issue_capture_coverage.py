"""OFFLINE ONLY: negative-evidence model for hypothetical effect-capture traces.

This module never instruments Frappe, connects to a service, executes SQL,
claims runtime interception coverage, or grants rollback/COMMIT authorization.
Surface names are REVIEW TARGETS, not proof that all paths were intercepted.
"""

from dataclasses import dataclass


ISOLATED_SITE = "ccpc-integration2.localhost"
SQL_SURFACES = frozenset(
    {
        "frappe.db.sql",
        "frappe.db.multisql",
        "frappe.qb.run",
        "db.cursor.execute",
        "db.cursor.executemany",
    }
)
NON_SQL_SURFACES = frozenset(
    {
        "frappe.cache.lpush",
        "frappe.clear_document_cache",
        "redis.raw_client",
        "frappe.publish_realtime",
        "frappe.enqueue",
        "frappe.db.before_commit",
        "frappe.db.after_commit",
        "frappe.db.before_rollback",
        "frappe.db.after_rollback",
        "frappe.document_hooks",
        "filesystem.write",
    }
)
REVIEW_SURFACES = SQL_SURFACES | NON_SQL_SURFACES
PHASES = frozenset({"before_commit", "after_commit", "before_rollback", "after_rollback", "unknown"})


class UnreviewedCapture(ValueError):
    """Invalid or unreviewed hypothetical event or coverage declaration."""


@dataclass(frozen=True)
class SyntheticCaptureEvent:
    """Inert fixture, not an actual database/Redis observation."""

    site: str
    surface: str
    phase: str
    sql: str | None = None
    binds: tuple | None = None

    def __post_init__(self):
        if self.site != ISOLATED_SITE:
            raise UnreviewedCapture("Site does not match isolated test identity")
        if self.surface not in REVIEW_SURFACES:
            raise UnreviewedCapture("Unknown effect surface is not silently ignored")
        if self.phase not in PHASES:
            raise UnreviewedCapture("Unknown event ordering/phase")
        if self.surface in SQL_SURFACES:
            if type(self.sql) is not str or not self.sql.strip() or type(self.binds) is not tuple:
                raise UnreviewedCapture("SQL observation lacks exact text and tuple binds")
        elif self.sql is not None or self.binds is not None:
            raise UnreviewedCapture("Non-SQL event must not be disguised as SQL")


def review_synthetic_coverage(claimed_surfaces: tuple, events: tuple) -> dict:
    """Characterize missing claims/effects, NEVER certify instrumentation or safety.

    A claim is untrusted reviewer input; even claiming every path cannot show
    that monkeypatch targets, lower-level clients or callbacks were covered.
    """
    if type(claimed_surfaces) is not tuple or any(type(x) is not str for x in claimed_surfaces):
        raise UnreviewedCapture("Capture declarations must be a tuple of names")
    if len(claimed_surfaces) != len(set(claimed_surfaces)):
        raise UnreviewedCapture("Duplicated capture claims")
    if set(claimed_surfaces) - REVIEW_SURFACES:
        raise UnreviewedCapture("Unknown capture declaration")
    if type(events) is not tuple or any(type(x) is not SyntheticCaptureEvent for x in events):
        raise UnreviewedCapture("Events must be explicitly typed, immutable fixtures")

    missing = tuple(sorted(REVIEW_SURFACES - set(claimed_surfaces)))
    undeclared = tuple(sorted({e.surface for e in events} - set(claimed_surfaces)))
    sql_count = sum(e.surface in SQL_SURFACES for e in events)
    non_sql_count = len(events) - sql_count
    # These are model observations, not independently validated instrumented paths.
    return {
        "site": ISOLATED_SITE,
        "candidate_surface_count": len(REVIEW_SURFACES),
        "missing_capture_claims": missing,
        "events_on_unclaimed_surfaces": undeclared,
        "hypothetical_sql_event_count": sql_count,
        "hypothetical_non_sql_event_count": non_sql_count,
        "real_capture_coverage_verified": False,
        "child_sql_predicates_verified": False,
        "redis_cache_containment_verified": False,
        "before_after_rollback_delta_verified": False,
        "safe_to_rehearse": False,
        "safe_to_commit": False,
        "status": "NO_GO_SOURCE_ONLY",
    }
