#!/usr/bin/env python3
"""Review-only site-free 67-test launcher; never run on unproven shared DEV/PROD host.

No site initialization, database login, Docker calls, mutations or network setup.
A genuine, independently isolated Frappe/ERPNext Python environment is required.
GitHub preparation does NOT authorize staging or execution on CCPC Ubuntu.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import MagicMock

FEATURE_SHA = "bd03077e7339c250b727091825f6bd187bf58534"
TEST_MODULES = (
    "ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_slip",
    "ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_issue_safety",
    "ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_peer_issuance",
)
EXPECTED_TESTS = 67


class Stop(Exception):
    """Fail closed without falling back to another checkout or site."""


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=8,
        check=False,
    )
    if result.returncode:
        raise Stop("Source verification failed")
    return result.stdout.strip()


def verify_source(root: Path) -> None:
    if not root.is_dir() or root.is_symlink():
        raise Stop("A real, non-symlink isolated checkout is required")
    if git(root, "rev-parse", "--show-toplevel") != str(root):
        raise Stop("Expected checkout does not match requested root")
    if git(root, "rev-parse", "HEAD") != FEATURE_SHA:
        raise Stop("Feature commit does not match pinned source")
    if git(root, "rev-parse", "--abbrev-ref", "HEAD") != "HEAD":
        raise Stop("A detached, non-serving source checkout is required")
    if git(root, "status", "--porcelain", "--untracked-files=normal"):
        raise Stop("Source checkout is not clean")
    if not (root / "ccpcerp" / "ccpc_erp" / "withdrawal_slip_stock.py").is_file():
        raise Stop("Feature module is missing")



def verify_loaded_ccpc_modules(root: Path) -> None:
    """Reject CCPC Python modules loaded from another checkout or path.

    A pinned Git HEAD alone does not guarantee that Python imports follow it.
    Reject namespace paths spanning multiple locations as well as modules
    whose dotted name and resolved file do not agree.
    """
    for name, module in tuple(sys.modules.items()):
        if name != "ccpcerp" and not name.startswith("ccpcerp."):
            continue
        expected = root.joinpath(*name.split("."))
        location = getattr(module, "__file__", None)
        if location:
            resolved = Path(location).resolve()
            if resolved not in (expected.with_suffix(".py"), expected / "__init__.py"):
                raise Stop("CCPC module origin does not match pinned checkout")
        else:
            search_paths = getattr(module, "__path__", None)
            if search_paths is None:
                raise Stop("CCPC module has no verifiable origin")
            paths = [Path(p).resolve() for p in search_paths]
            if paths != [expected]:
                raise Stop("CCPC namespace package origin is ambiguous")


def install_non_site_context():
    import frappe

    # These context-local assignments were required by the earlier 65-test
    # site-free Frappe v16 harness; no bench site or DB is initialized.
    frappe.local.session = frappe._dict(user="Guest")
    frappe.local.flags = frappe._dict()
    frappe.local.conf = frappe._dict()
    frappe.local.lang = "en"
    frappe.local.initialised = False
    frappe.local.db = MagicMock(name="denied_sitefree_db")

    def deny(*_args, **_kwargs):
        raise Stop("Unmocked site, database or network access is forbidden")

    for name in ("sql", "commit", "rollback", "connect", "begin", "get_value", "set_value", "get_all", "get_list", "exists", "delete"):
        getattr(frappe.local.db, name).side_effect = deny
    frappe.init = deny
    frappe.connect = deny
    return frappe


def run_tests(root: Path) -> bool:
    verify_source(root)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
    import importlib

    frappe = install_non_site_context()
    importlib.import_module("ccpcerp.ccpc_erp.withdrawal_slip_stock")
    try:
        suite = unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)
        verify_loaded_ccpc_modules(root)
        if suite.countTestCases() != EXPECTED_TESTS:
            raise Stop("Unexpected test count; source or suite has drifted")
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        return result.wasSuccessful() and result.testsRun == EXPECTED_TESTS
    finally:
        # Recheck on success and failure; loaded mocks must not change
        # which source was executed, or leave the tested checkout dirty.
        verify_loaded_ccpc_modules(root)
        verify_source(root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("isolated_feature_checkout", type=Path)
    args = parser.parse_args()
    try:
        if args.isolated_feature_checkout.is_symlink():
            raise Stop("A symlink checkout path is not permitted")
        root = args.isolated_feature_checkout.resolve(strict=True)
        return 0 if run_tests(root) else 1
    except (Stop, OSError, subprocess.TimeoutExpired) as exc:
        print("SITE-FREE WITHDRAWAL REGRESSIONS: STOP — " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
