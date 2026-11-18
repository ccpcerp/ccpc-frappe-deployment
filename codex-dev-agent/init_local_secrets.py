#!/usr/bin/env python3
"""Create two private passwords ONLY for the new disposable DEV-only MariaDB.

Does not touch any existing DEV or PROD config. Never prints secret values.
Files are gitignored and creation is exclusive/non-destructive.
"""
import os
import secrets
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIRECTORY = ROOT / "local-secrets"
FILES = ("db-root-password", "db-user-password")


def verify_existing(path):
    data = path.lstat()
    if not stat.S_ISREG(data.st_mode) or data.st_uid != os.geteuid():
        raise RuntimeError("Existing synthetic secret file type/owner is unsafe.")
    if stat.S_IMODE(data.st_mode) != 0o600 or data.st_nlink != 1:
        raise RuntimeError("Existing synthetic secret file permissions/links are unsafe.")


def main():
    if DIRECTORY.exists():
        info = DIRECTORY.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid():
            raise RuntimeError("Synthetic secret directory has unexpected owner/type.")
        if stat.S_IMODE(info.st_mode) != 0o700:
            raise RuntimeError("Synthetic secret directory must have mode 0700.")
    else:
        DIRECTORY.mkdir(mode=0o700)
    for name in FILES:
        path = DIRECTORY / name
        if path.exists() or path.is_symlink():
            verify_existing(path)
            print(name + ": existing protected file preserved")
            continue
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(secrets.token_urlsafe(36) + "\n")
        except BaseException:
            try:
                path.unlink()
            except OSError:
                pass
            raise
        print(name + ": new synthetic-only password created (value hidden)")
    print("PASS: private synthetic secrets prepared. Never upload this directory.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as exc:
        print("STOP: synthetic secrets not ready:", type(exc).__name__, file=sys.stderr)
        sys.exit(1)
