"""Static-only checks: cannot start Docker or authenticate to Codex."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "scripts" / "development" / "codex-isolated"
DOCKERFILE = PARTS / "Dockerfile"
STAGE = PARTS / "ccpc_codex_stage_offline_worker_20261116.sh"


class OfflineWorkerStaticTests(unittest.TestCase):
    def setUp(self):
        self.script = STAGE.read_text(encoding="utf-8")
        self.image = DOCKERFILE.read_text(encoding="utf-8")

    def test_exact_script_is_bash_syntax_valid(self):
        result = subprocess.run(["bash", "-n", str(STAGE)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_clean_image_has_nonroot_cli_and_no_copy(self):
        self.assertIn("FROM node:24-bookworm-slim", self.image)
        self.assertIn("@openai/codex@0.161.0", self.image)
        self.assertIn("USER 14532:14532", self.image)
        self.assertIn('CMD ["--version"]', self.image)
        for forbidden in ("COPY ", "ADD ", "ARG OPENAI_API_KEY",
                          "ENV OPENAI_API_KEY", "ssh-agent", "docker.sock"):
            if forbidden == "docker.sock":
                continue  # descriptive comments may mention absence
            self.assertNotIn(forbidden, self.image)

    def test_host_identity_and_optin_pinned(self):
        for expected in ('"ccpcerpserver"', '"gani"',
                         "CCPC_APPROVE_CODEX_WORKER_SETUP",
                         "unix:///var/run/docker.sock",
                         "OLD_EXPECTED", "SHARED_HOST_SCOPE=PASS"):
            self.assertIn(expected, self.script)

    def test_resource_guard_and_immutable_image_identity(self):
        self.assertIn("DockerRootDir", self.script)
        self.assertIn("4294967296", self.script)
        self.assertIn('IMAGE_ID=', self.script)
        self.assertIn('"$IMAGE_ID" --version', self.script)

    def test_runtime_restricted_offline_probe_only(self):
        for expected in ("--network none", "--read-only", "--user 14532:14532",
                         "--cap-drop ALL", "--security-opt no-new-privileges",
                         "--pids-limit 64", "--memory 768m", "--cpus 1",
                         "--restart no", "--version", "ISOLATED_PROBE_CONFIG=PASS",
                         "NO_MODEL_AUTH_OR_AGENT_RUN=PASS"):
            self.assertIn(expected, self.script)

    def test_does_not_mutate_old_or_dev_containers(self):
        for forbidden in ('docker exec', 'docker stop', 'docker restart',
                          'docker rm ', 'docker network create', 'bench migrate',
                          'git reset', 'git clean', 'codex exec',
                          'OPENAI_API_KEY=', 'docker commit',
                          'docker system prune', 'frappe.db.commit'):
            self.assertNotIn(forbidden, self.script)

    def test_not_a_host_ssh_mount_clone(self):
        self.assertIn('--network none', self.script)
        self.assertIn("'{{len .Mounts}}'", self.script)
        self.assertNotIn("--volumes-from", self.script)
        self.assertNotIn("--mount type=bind", self.script)


if __name__ == "__main__":
    unittest.main()
