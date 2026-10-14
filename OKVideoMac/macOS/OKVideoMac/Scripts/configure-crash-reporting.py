#!/usr/bin/env python3
"""Inject a public crash DSN before signing; keep service configuration out of source."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import plistlib
import re
import stat
import sys
import tarfile
import tempfile
from urllib.parse import urlsplit

MAX_CONFIG_BYTES = 16384
KEY = "OKCrashReportDSN"


def validate_dsn(value: str) -> None:
    if not value or not value.isascii() or any(c.isspace() for c in value) or any(c in value for c in "?#"):
        raise ValueError("Require a nonempty public HTTPS DSN without query or fragment.")
    endpoint = urlsplit(value)
    if (endpoint.scheme != "https" or not endpoint.hostname or endpoint.password is not None
        or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", endpoint.username or "")
        or not endpoint.path.split("/")[-1].isdigit()):
        raise ValueError("Require a public HTTPS DSN; secret-bearing DSNs are forbidden.")
    if endpoint.port is not None and not 1 <= endpoint.port <= 65535:
        raise ValueError("Invalid DSN port.")


def configuration(path: Path, repo: Path) -> str:
    if not path.is_absolute() or path.resolve().is_relative_to(repo.resolve()):
        raise ValueError("Crash configuration must be an absolute file outside the checkout.")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or info.st_mode & 0o077 or info.st_size > MAX_CONFIG_BYTES):
            raise ValueError("Crash configuration must be an owner-only regular file of at most 16 KiB.")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(MAX_CONFIG_BYTES + 1)
        if len(data) > MAX_CONFIG_BYTES:
            raise ValueError("Crash configuration is too large.")
    finally:
        os.close(fd)
    values = {}
    for line in data.decode("utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        name, separator, value = line.partition("=")
        if not separator or name.strip() != "SENTRY_DSN" or name.strip() in values:
            raise ValueError("Crash configuration may contain only one SENTRY_DSN; no management credentials.")
        values[name.strip()] = value.strip()
    if set(values) != {"SENTRY_DSN"}:
        raise ValueError("Crash configuration requires exactly one SENTRY_DSN.")
    validate_dsn(values["SENTRY_DSN"])
    return values["SENTRY_DSN"]


def expected_dsn(mode: str, config: Path | None, repo: Path) -> str:
    if mode == "local":
        if config is not None:
            raise ValueError("Local packages cannot use the private release crash configuration.")
        return ""
    if config is None:
        raise ValueError("Distribution requires --crash-config; public source builds remain unconfigured.")
    return configuration(config, repo)


def apply(app: Path, expected: str) -> None:
    path = app / "Contents/Info.plist"
    info = plistlib.loads(path.read_bytes())
    info[KEY] = expected
    fd, temporary = tempfile.mkstemp(prefix=".crash-info-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            plistlib.dump(info, stream, sort_keys=False)
        os.chmod(temporary, stat.S_IMODE(path.stat().st_mode))
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def verify_sources(archive: Path, expected: str) -> None:
    if not expected:
        return
    forbidden = expected.encode()
    with tarfile.open(archive, "r:*") as source:
        for member in source:
            if not member.isfile():
                continue
            stream = source.extractfile(member)
            if stream is None:
                continue
            with stream:
                tail = b""
                while chunk := stream.read(1024 * 1024):
                    data = tail + chunk
                    if forbidden in data:
                        raise ValueError("Actual release crash DSN found in the source archive.")
                    tail = data[-len(forbidden):]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "apply", "verify"])
    parser.add_argument("--mode", required=True, choices=["local", "distribution"])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--app", type=Path)
    parser.add_argument("--source-archive", action="append", type=Path, default=[])
    args = parser.parse_args()
    expected = expected_dsn(args.mode, args.config, args.repo)
    if args.action != "check":
        if args.app is None:
            raise ValueError("App path is required.")
        if args.action == "apply":
            apply(args.app, expected)
        info = plistlib.loads((args.app / "Contents/Info.plist").read_bytes())
        if info.get(KEY) != expected:
            raise ValueError("Packaged crash configuration does not match the selected release mode.")
        for archive in args.source_archive:
            verify_sources(archive, expected)
    print("Crash configuration passed: " + ("public HTTPS upload endpoint configured" if expected else "local capture only") + "; values omitted.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError, plistlib.InvalidFileException, tarfile.TarError):
        print("Crash configuration failed validation. Use an owner-only DSN file outside the checkout; no credentials or configuration values were logged.", file=sys.stderr)
        raise SystemExit(2)
