"""Offline source-contract checks only; never builds or runs Docker."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "FRAPPE_SHA": "988e54f3c4c291e2077a83809663f123731abe76",
    "ERPNEXT_SHA": "4048fb70e14d1843956fcdabb7c3cca75a1cbcdd",
    "CCPC_SHA": "cfcc19394a6646548f2b7050db040c8cf5ebafde",
    "ERPNEXT_PATCH_SHA": "b543d14453d4370c6ddaf53bee8f8b786bf9199d5ce33182eb80aa5080e85ba1",
    "ERPNEXT_OVERLAY_STATE_SHA": "13bfff41433c9ac380b9ed632911674b9b87f7e7cb728388912ed50c79c63d0e",
}
LABELS = {
    "frappe.sha": "FRAPPE_SHA", "erpnext.sha": "ERPNEXT_SHA",
    "ccpcerp.sha": "CCPC_SHA", "erpnext.patch.sha256": "ERPNEXT_PATCH_SHA",
    "erpnext.overlay.sha256": "ERPNEXT_OVERLAY_STATE_SHA",
}


def check(source, build, config):
    if source.count("FROM base AS builder\n") != 1 or source.count("FROM base AS backend\n") != 1:
        raise ValueError("Unapproved stages")
    builder, backend = source.split("FROM base AS backend\n")
    label_lines = [s.strip() for s in backend.splitlines() if "org.ccpc." in s and not s.lstrip().startswith("#")]
    if len(label_lines) != 5 or sum(s.startswith("LABEL ") for s in label_lines) != 1:
        raise ValueError("Unexpected provenance label instruction")
    for name, pin in LABELS.items():
        arg = "EXPECTED_" + pin
        value = 'org.ccpc.' + name + '="' + chr(36) + '{' + arg + '}"'
        if sum(value in line for line in label_lines) != 1:
            raise ValueError("Mismatched provenance label")
        if len(re.findall(r'^ARG ' + arg + '$', builder, re.M)) != 1 or len(re.findall(r'^ARG ' + arg + '$', backend, re.M)) != 1:
            raise ValueError("Missing stage argument")
        if '--build-arg ' + arg + '="' + chr(36) + pin + '"' not in build:
            raise ValueError("Build script pin mismatch")
        if pin + '="' + PINS[pin] + '"' not in config:
            raise ValueError("Unpinned source release")
    for expected in ('"${actual_sha}" != "${expected_sha}"',
                     '"${actual_patch_file_sha}" != "${EXPECTED_ERPNEXT_PATCH_SHA}"',
                     '"${actual_overlay_state_sha}" != "${EXPECTED_ERPNEXT_OVERLAY_STATE_SHA}"',
                     'post_build_overlay_state_sha='):
        if expected not in builder:
            raise ValueError("Builder verification missing")
    if 'COPY --from=builder' not in backend:
        raise ValueError("Unverified backend contents")
    return True


class ProvenanceOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'images/custom/Containerfile').read_text()
        cls.build = (ROOT / 'scripts/modules/docker.sh').read_text()
        cls.config = (ROOT / 'scripts/config.sh').read_text()

    def reject(self, source=None, build=None, config=None):
        with self.assertRaises(ValueError):
            check(self.source if source is None else source,
                  self.build if build is None else build,
                  self.config if config is None else config)

    def test_exact_five_labels(self):
        self.assertTrue(check(self.source, self.build, self.config))

    def test_wrong_label_value(self):
        self.reject(source=self.source.replace('org.ccpc.frappe.sha="${EXPECTED_FRAPPE_SHA}"',
                                               'org.ccpc.frappe.sha="${EXPECTED_CCPC_SHA}"'))

    def test_missing_final_arg(self):
        a, b = self.source.split('FROM base AS backend\n')
        self.reject(source=a + 'FROM base AS backend\n' + b.replace('ARG EXPECTED_CCPC_SHA\n', ''))

    def test_build_script_mismatch(self):
        self.reject(build=self.build.replace('--build-arg EXPECTED_FRAPPE_SHA="$FRAPPE_SHA"',
                                             '--build-arg EXPECTED_FRAPPE_SHA="$ERPNEXT_SHA"'))

    def test_unpinned_release(self):
        self.reject(config=self.config.replace(PINS['FRAPPE_SHA'], '0' * 40))

    def test_removed_builder_check(self):
        self.reject(source=self.source.replace('"${actual_sha}" != "${expected_sha}"',
                                               '"${actual_sha}" = "${expected_sha}"'))

    def test_additional_label(self):
        self.reject(source=self.source.replace('      org.ccpc.ccpcerp.sha',
                                               '      org.ccpc.unapproved.sha="${EXPECTED_CCPC_SHA}" \\\n      org.ccpc.ccpcerp.sha'))


if __name__ == '__main__':
    unittest.main()
