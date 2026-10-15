"""OFFLINE ONLY — narrow SQL effect witness, not a posting safety guard.

No Frappe, Docker, database, Redis, I/O or executable hook integration.
It models ONE exact tabSeries statement observed in a synthetic trace.
A matching observation NEVER authorizes a live statement or a COMMIT.
"""

from dataclasses import dataclass
import re


FIRST_SERIES_INSERT = (
    "INSERT INTO `tabSeries` (`name`, `current`) VALUES (%s, 1)"
)
EXISTING_SERIES_INCREMENT = (
    "UPDATE `tabSeries` SET `current` = `current` + 1 WHERE `name`=%s"
)
SITE = "ccpc-integration2.localhost"
SERIES_KEY_PATTERN = re.compile(r"MAT-STE-[0-9]{4}-\Z", re.ASCII)


class UnreviewedEffect(ValueError):
    """The observed statement or external effect was not exactly reviewed."""


@dataclass(frozen=True)
class IsolatedSeriesBaseline:
    """Hypothetical fixture supplied by a reviewer; not measured by this module."""

    site: str
    key: str
    current: int | None  # None means an independently verified absent row.

    def __post_init__(self):
        if self.site != SITE:
            raise UnreviewedEffect("Wrong or unspecified isolated site")
        if not isinstance(self.key, str) or not SERIES_KEY_PATTERN.fullmatch(self.key):
            raise UnreviewedEffect("Unexpected naming-series key")
        if self.current is not None and (
            type(self.current) is not int or self.current < 0
        ):
            raise UnreviewedEffect("Invalid expected counter baseline")

    def expected_sql(self):
        """Exact pinned Frappe naming.py getseries DML template and key."""
        if self.current is None:
            return FIRST_SERIES_INSERT, (self.key,)
        return EXISTING_SERIES_INCREMENT, (self.key,)


class OfflineEffectWitness:
    """Fail-closed *review* of one expected series DML; no execution paths."""

    def __init__(self, baseline: IsolatedSeriesBaseline):
        if not isinstance(baseline, IsolatedSeriesBaseline):
            raise UnreviewedEffect("Baseline must be explicit and typed")
        self._baseline = baseline
        self._seen = False

    def observe_sql(self, statement: str, params: tuple):
        """Compare a captured statement and bind args byte-for-byte; never run it."""
        expected_sql, expected_params = self._baseline.expected_sql()
        if (
            self._seen
            or type(statement) is not str
            or type(params) is not tuple
            or statement != expected_sql
            or params != expected_params
        ):
            raise UnreviewedEffect("Unexpected, repeated or unscoped SQL effect")
        self._seen = True
        return "MATCHED_EXPECTED_SERIES_SQL_ONLY"

    def observe_external_effect(self, kind: str):
        """Always reject Redis/cache, realtime, enqueue and any unknown effect."""
        raise UnreviewedEffect("External side effect is not isolated")

    def outcome(self):
        """Intentionally NEVER signals rollback rehearsal or COMMIT readiness."""
        return {
            "series_statement_matched": self._seen,
            "child_delete_reviewed": False,
            "global_search_redis_contained": False,
            "database_rollback_verified": False,
            "safe_to_execute": False,
            "safe_to_commit": False,
        }
