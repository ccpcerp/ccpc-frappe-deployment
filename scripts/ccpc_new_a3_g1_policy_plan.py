"""G1 exact-ID restart policy planning and compensation, PURE/REVIEW ONLY.

No Docker imports, subprocess, filesystem, CLI, or mutation of arguments. The
running host must be separately verified against R0 before future execution.
"""
from dataclasses import dataclass
import re

PREFIX = 'ccpc_prod_erpnext'
CANDIDATE = tuple(f'{PREFIX}-{role}-1' for role in
                  ('db', 'redis-cache', 'redis-queue', 'backend', 'websocket', 'frontend'))
ORIGINAL = tuple(f'{p}-{role}-1' for p in
                 ('ccpc_full_acceptance_20261107', 'ccpc_restore_rehearsal_20261107')
                 for role in ('redis-queue', 'redis-cache', 'db'))
TEST_PREFIX = 'ccpc_a3_restore_drill_20261112'
TEST_RUNNING = tuple(f'{TEST_PREFIX}-{role}-1' for role in
                     ('frontend-completion1', 'websocket-completion1', 'backend-recovery1',
                      'redis-queue', 'redis-cache', 'db'))
TEST_FAILED = f'{TEST_PREFIX}-backend-1'
EXPECTED = set(CANDIDATE + ORIGINAL + TEST_RUNNING + (TEST_FAILED,))


class PlanStop(Exception):
    """A sanitized refusal; do not guess or mutate any containers."""


@dataclass(frozen=True)
class PolicyChange:
    name: str
    pinned_id: str
    before: str
    after: str


def require(condition):
    if not condition:
        raise PlanStop()


def verify_identity(manifest, snapshot):
    """Validate exact 19 identities, preserved run/exit state and policies.

    Candidate restart policies may be no or unless-stopped only. Neither this
    nor any plan proves backend queue/job side-effect safety.
    """
    require(isinstance(manifest, dict) and isinstance(snapshot, dict))
    ids = manifest.get('container_ids')
    require(isinstance(ids, dict) and set(ids) == EXPECTED and set(snapshot) == EXPECTED)
    require(all(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value)
                for value in ids.values()))
    require(len(set(ids.values())) == 19)
    for name in EXPECTED:
        item = snapshot.get(name)
        require(isinstance(item, dict) and item.get('id') == ids[name])
        require(item.get('restart') in (('no', 'unless-stopped') if name in CANDIDATE
                                        else ('no',)))
        if name == TEST_FAILED:
            require(item.get('running') is False and item.get('exit') == 1)
        else:
            require(item.get('running') is True)
    return ids


def plan_candidate_updates(manifest, snapshot):
    """Produce six immutable no->unless-stopped exact-ID intents, no effects."""
    ids = verify_identity(manifest, snapshot)
    require(all(snapshot[name]['restart'] == 'no' for name in CANDIDATE))
    return tuple(PolicyChange(name, ids[name], 'no', 'unless-stopped')
                 for name in CANDIDATE)


def plan_partial_compensation(manifest, snapshot, applied_names):
    """Reverse *only* known applied candidates, after an all-19 revalidation.

    Do not call this as a general rollback after a different actor modifies
    policies. Unknown/duplicate/noncandidate applied names cause a STOP.
    """
    ids = verify_identity(manifest, snapshot)
    require(isinstance(applied_names, (tuple, list)))
    require(all(isinstance(name, str) for name in applied_names))
    require(len(set(applied_names)) == len(applied_names))
    require(set(applied_names) <= set(CANDIDATE))
    for name in CANDIDATE:
        wanted = 'unless-stopped' if name in applied_names else 'no'
        require(snapshot[name]['restart'] == wanted)
    return tuple(PolicyChange(name, ids[name], 'unless-stopped', 'no')
                 for name in reversed(applied_names))
