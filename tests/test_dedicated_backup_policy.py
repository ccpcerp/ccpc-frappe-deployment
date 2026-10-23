"""Step 127 synthetic-only unit tests: no Docker, NAS, live secrets or Frappe."""
import dataclasses
import datetime as dt
import hashlib
import json
import unittest

from scripts import dedicated_backup_policy as p


class Step127PolicyTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "schema_version": 1, "release_id": "ccpc-example-release-00001",
            "deployment_commit": "1" * 40, "frappe_sha": p.FRAPPE_SHA,
            "erpnext_sha": p.ERPNEXT_SHA, "ccpc_sha": p.CCPC_SHA,
            "patch_sha256": p.PATCH_SHA256, "overlay_sha256": p.OVERLAY_SHA256,
            "host": p.HOST, "site": p.SITE, "profile": p.PROFILE,
            "compose_project": "ccpc-dedicated", "backend_image_id": "sha256:" + "2" * 64,
            "db_image_id": "sha256:" + "3" * 64,
            "backend_config_hash": "4" * 64, "db_config_hash": "5" * 64,
            "sites_volume": "ccpc-dedicated_sites",
            "db_volume": "ccpc-dedicated_db-data",
            "backend_logs_volume": "ccpc-dedicated_logs",
        }
        zero = dt.datetime(2026, 10, 23, 8, tzinfo=dt.timezone.utc)
        self.claim = p.ConsistencyObservation(
            zero, zero + dt.timedelta(seconds=1),
            zero + dt.timedelta(minutes=1),
            zero + dt.timedelta(minutes=1, seconds=1),
            {key: False for key in p.WRITER_CLASSES}, 0, False,
            True, True, True, True,
        )

    def encoded(self, data=None):
        return json.dumps(self.data if data is None else data, sort_keys=True, separators=(",", ":")).encode()

    def checked(self, data=None):
        raw = self.encoded(data)
        return p.validate_reviewed_release(
            raw, independently_approved_sha256=hashlib.sha256(raw).hexdigest()
        )

    def rejected(self, fn):
        with self.assertRaises(p.PolicyRejected):
            fn()

    def mounts(self):
        release = self.checked()
        names = {
            release.sites_volume: "sites", release.db_volume: "db-data",
            release.backend_logs_volume: "logs",
        }
        volumes = {
            name: {
                "Name": name,
                "Mountpoint": "/var/lib/docker/volumes/" + name + "/_data",
                "Labels": {
                    "com.docker.compose.project": release.project,
                    "com.docker.compose.volume": logical,
                },
            } for name, logical in names.items()
        }

        def mount(name, destination):
            return {
                "Type": "volume", "Name": name,
                "Source": volumes[name]["Mountpoint"],
                "Destination": destination, "RW": True,
            }

        backend = [
            mount(release.sites_volume, "/home/frappe/frappe-bench/sites"),
            mount(release.backend_logs_volume, "/home/frappe/frappe-bench/logs"),
        ]
        db = [mount(release.db_volume, "/var/lib/mysql")]
        return release, backend, db, volumes

    def test_reviewed_synthetic_manifest_not_backup_ready(self):
        release = self.checked()
        self.assertFalse(release.trusted_runtime)
        self.assertFalse(release.backup_ready)

    def test_independent_digest_missing_wrong_or_tampered(self):
        raw = self.encoded()
        self.rejected(lambda: p.validate_reviewed_release(
            raw, independently_approved_sha256=""))
        self.rejected(lambda: p.validate_reviewed_release(
            raw, independently_approved_sha256="f" * 64))
        new = self.encoded({**self.data, "release_id": "ccpc-changed-release-00001"})
        self.rejected(lambda: p.validate_reviewed_release(
            new, independently_approved_sha256=hashlib.sha256(raw).hexdigest()))

    def test_unknown_secret_or_missing_field_rejected(self):
        self.rejected(lambda: self.checked({**self.data, "db_password": "synthetic"}))
        self.rejected(lambda: self.checked({
            k: v for k, v in self.data.items() if k != "db_volume"
        }))

    def test_duplicate_json_key_rejected(self):
        raw = self.encoded()[:-1] + b',"release_id":"ccpc-duplicate-00001"}'
        self.rejected(lambda: p.validate_reviewed_release(
            raw, independently_approved_sha256=hashlib.sha256(raw).hexdigest()))

    def test_bad_schema_or_format_rejected(self):
        for schema in (True, 2, "1"):
            self.rejected(lambda: self.checked({**self.data, "schema_version": schema}))
        for raw in (b'{}', b'\xff', b' ' * 12_001, "not bytes"):
            self.rejected(lambda: p.validate_reviewed_release(
                raw, independently_approved_sha256="0" * 64))

    def test_unpinned_or_wrong_source_rejected(self):
        for key, val in (
            ("host", "ccpcerpserver"), ("frappe_sha", "f" * 40),
            ("erpnext_sha", "e" * 40), ("ccpc_sha", "a" * 40),
            ("patch_sha256", "0" * 64), ("profile", "legacy-lan"),
            ("backend_image_id", "ccpcerp:latest"),
            ("db_config_hash", "not-a-hash"),
            ("deployment_commit", "pending"),
        ):
            self.rejected(lambda: self.checked({**self.data, key: val}))

    def test_log_mount_requires_exact_named_volume(self):
        for volume in ("anonymous", "", "ccpc-dedicated_old", None):
            self.rejected(lambda: self.checked({
                **self.data, "backend_logs_volume": volume
            }))

    def test_named_mounts_pass_policy_but_never_authorize_backup(self):
        release, backend, db, volumes = self.mounts()
        status = p.verify_exact_mount_layout(
            release, backend_mounts=backend, db_mounts=db, inspected_volumes=volumes
        )
        self.assertTrue(status.exact_layout)
        self.assertFalse(status.backup_ready)

    def test_unauthorized_mount_type_or_destination_rejected(self):
        release, backend, db, volumes = self.mounts()
        for changed in (
            {"Type": "bind"}, {"Name": "anonymous"},
            {"RW": False}, {"Destination": "/run/docker.sock"},
        ):
            mounts = [dict(m) for m in backend]
            mounts[1].update(changed)
            self.rejected(lambda: p.verify_exact_mount_layout(
                release, backend_mounts=mounts, db_mounts=db, inspected_volumes=volumes
            ))

    def test_extra_duplicate_or_missing_mount_rejected(self):
        release, backend, db, volumes = self.mounts()
        for mounts in (backend + [dict(backend[0])], [backend[0]], [backend[0], dict(backend[0])]):
            self.rejected(lambda: p.verify_exact_mount_layout(
                release, backend_mounts=mounts, db_mounts=db, inspected_volumes=volumes
            ))

    def test_wrong_volume_labels_or_source_rejected(self):
        release, backend, db, volumes = self.mounts()
        for changed in (
            {"Mountpoint": "/var/lib/docker/../etc"},
            {"Name": "other"},
            {"Labels": {"com.docker.compose.project": "wrong", "com.docker.compose.volume": "logs"}},
        ):
            altered = {k: dict(v) for k, v in volumes.items()}
            altered[release.backend_logs_volume].update(changed)
            self.rejected(lambda: p.verify_exact_mount_layout(
                release, backend_mounts=backend, db_mounts=db,
                inspected_volumes=altered
            ))

    def test_valid_claim_never_establishes_trusted_quiescence(self):
        verdict = p.evaluate_quiescence_observation(self.claim)
        self.assertTrue(verdict.evidence_meets_shape_and_claims)
        self.assertFalse(verdict.writes_quiesced)
        self.assertFalse(verdict.backup_ready)

    def test_active_or_missing_writer_family_rejected(self):
        for activity in (
            {**self.claim.writer_activity, "queues": True},
            {**self.claim.writer_activity, "uploads": "no"},
            {k: v for k, v in self.claim.writer_activity.items() if k != "api"},
        ):
            self.rejected(lambda: p.evaluate_quiescence_observation(
                dataclasses.replace(self.claim, writer_activity=activity)
            ))

    def test_capture_must_be_inside_freeze_interval(self):
        for fields in (
            {"freeze_started_utc": self.claim.capture_started_utc},
            {"freeze_ended_utc": self.claim.capture_ended_utc},
            {"capture_started_utc": self.claim.capture_ended_utc},
            {"freeze_started_utc": self.claim.freeze_started_utc.replace(tzinfo=None)},
        ):
            self.rejected(lambda: p.evaluate_quiescence_observation(
                dataclasses.replace(self.claim, **fields)
            ))

    def test_transactions_warning_and_unsupported_policy_rejected(self):
        for fields in (
            {"in_flight_transactions": 1}, {"in_flight_transactions": False},
            {"changed_files_warning": True}, {"backup_side_effects_reviewed": False},
            {"full_backup_filters_verified": "yes"},
            {"encryption_state_verified": False},
            {"recoverable_abort_plan_verified": False},
        ):
            self.rejected(lambda: p.evaluate_quiescence_observation(
                dataclasses.replace(self.claim, **fields)
            ))


if __name__ == "__main__":
    unittest.main()
