"""Execute exact GitHub PR33 executive gateway unittests in existing DEV Frappe.

Fed by the pinned, operator-delivered host wrapper. No filesystem staging in
the container, no source checkout changes, and no commits/business writes.
This runner is deliberately short-lived, with a read-only DB transaction.
"""
import hashlib
import importlib
import sys
import types
import unittest
from pathlib import Path
from subprocess import check_output

import frappe

SITE = "development.localhost"
BENCH_APP = "/workspace/development/frappe-bench/apps/ccpcerp"
CURRENT_DEV_SHA = "1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc"
REVIEW_SHA = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
GATEWAY = "ccpcerp/ccpc_erp/executive_reporting.py"
TEST = "ccpcerp/ccpc_erp/test_executive_reporting.py"
EXPECTED_BLOBS = {
    GATEWAY: "d75ffe318788d1cd8e3b8217a74dc3f9d8860cb4",
    TEST: "b78b42a858b9b1a98ca5be79b4037eb7c7b7a1fa",
}


def git(*args):
    return check_output(["git", "-C", BENCH_APP, *args], text=True, timeout=30).strip()


def git_blob_sha(raw):
    body = b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw
    return hashlib.sha1(body).hexdigest()


def ensure(cond, failure):
    if not cond:
        raise RuntimeError("STOP: " + failure)


def main():
    # The tar reader must inject ONLY these exact two file payloads;
    # the local older DEV checkout is never overwritten or imported as the
    # candidate gateway by accident.
    ensure(set(payload) == {GATEWAY, TEST}, "UNEXPECTED_SOURCE_MEMBERS")
    for path, expected in EXPECTED_BLOBS.items():
        ensure(git_blob_sha(payload[path]) == expected, "SOURCE_BLOB_MISMATCH")
        ensure(len(payload[path]) < 65000, "SOURCE_SIZE_EXCEEDED")

    ensure(sys.version_info >= (3, 14), "UNSUPPORTED_PYTHON")
    ensure(Path.cwd() == Path("/workspace/development/frappe-bench/sites"),
           "WRONG_SITES_WORKING_DIR")
    ensure(git("rev-parse", "HEAD") == CURRENT_DEV_SHA, "DEV_SOURCE_SHA_CHANGED")
    ensure(git("status", "--porcelain=v1", "--untracked-files=all") == "?? AGENTS.md",
           "DEV_PROTECTED_WORKTREE_CHANGED")
    ensure(Path(BENCH_APP, "AGENTS.md").is_file(), "PROTECTED_AGENTS_MISSING")
    ensure(not Path(BENCH_APP, "AGENTS.md").is_symlink(), "PROTECTED_AGENTS_SYMLINK")
    ensure(str(getattr(frappe, "__version__", "")).startswith("16."),
           "UNEXPECTED_FRAPPE_MAJOR")

    print("EXACT_GITHUB_SOURCE_BLOBS=PASS", flush=True)
    print("SUPPORTED_FRAPPE_PYTHON=PASS", flush=True)
    print("DEV_SOURCE_AND_PROTECTED_WORKTREE=PASS", flush=True)
    connected = False
    previous_gateway = None
    previous_pkg_attr = None
    previous_department_gateway = None
    package = None
    department = None
    try:
        frappe.init(site=SITE, sites_path=".")
        frappe.connect()
        connected = True
        ensure(frappe.local.site == SITE, "UNEXPECTED_CONNECTED_SITE")
        frappe.db.sql("START TRANSACTION READ ONLY")
        print("DEV_DB_TRANSACTION=READ_ONLY", flush=True)

        package = importlib.import_module("ccpcerp.ccpc_erp")
        module_name = "ccpcerp.ccpc_erp.executive_reporting"
        previous_gateway = importlib.import_module(module_name)
        previous_pkg_attr = getattr(package, "executive_reporting")

        # Inject exact new reviewed source into *this Python process only*.
        # No files copied over the installed app; no benchmark/migration.
        candidate = types.ModuleType(module_name)
        candidate.__file__ = "github-pr33/" + GATEWAY
        candidate.__package__ = "ccpcerp.ccpc_erp"
        sys.modules[module_name] = candidate
        package.executive_reporting = candidate
        exec(compile(payload[GATEWAY], candidate.__file__, "exec"),
             candidate.__dict__)

        # The native Department report is imported by the existing test
        # module; ensure its gateway reference is also process-local.
        department = importlib.import_module(
            "ccpcerp.ccpc_erp.report.ccpc_department_material_consumption."
            "ccpc_department_material_consumption"
        )
        previous_department_gateway = department.executive_reporting
        department.executive_reporting = candidate

        test_name = "ccpcerp.ccpc_erp._pr33_exact_source_test_executive_reporting"
        tests = types.ModuleType(test_name)
        tests.__package__ = "ccpcerp.ccpc_erp"
        tests.__file__ = "github-pr33/" + TEST
        exec(compile(payload[TEST], tests.__file__, "exec"), tests.__dict__)

        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        ensure(suite.countTestCases() == 15, "UNEXPECTED_TEST_COUNT")
        print("PR33_REVIEW_SHA=" + REVIEW_SHA, flush=True)
        print("PR33_EXACT_FRAPPE_TEST_COUNT=" + str(suite.countTestCases()), flush=True)
        result = unittest.TextTestRunner(verbosity=1, stream=sys.stdout).run(suite)
        ensure(result.wasSuccessful(), "UNITTEST_FAILURE")
        print("PR33_EXACT_FRAPPE_REGRESSIONS=PASS", flush=True)
    finally:
        if department is not None and previous_department_gateway is not None:
            department.executive_reporting = previous_department_gateway
        if package is not None and previous_gateway is not None:
            sys.modules["ccpcerp.ccpc_erp.executive_reporting"] = previous_gateway
            package.executive_reporting = previous_pkg_attr
        if connected:
            try:
                frappe.db.rollback()
            finally:
                frappe.destroy()
        else:
            frappe.destroy()
    print("PR33_SUPPORTED_RUNTIME_SOURCE_ONLY_TEST=COMPLETE", flush=True)


if __name__ == "__main__":
    # No tracebacks or secrets in normal output. Test details use only mock data.
    try:
        main()
    except Exception as exc:
        print("PR33_SUPPORTED_RUNTIME_SOURCE_ONLY_TEST=STOP", flush=True)
        if str(exc).startswith("STOP: "):
            print(str(exc), flush=True)
        sys.exit(1)
