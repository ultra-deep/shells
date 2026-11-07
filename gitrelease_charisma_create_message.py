#!/usr/bin/env python3
"""Generate Trader APK update/release message from APK filenames in this repo.

Picks the highest semver from each environment/buildMode folder, e.g. if
production/release contains:
  trader-production-release-v1.0.69.apk
  trader-production-release-v1.0.70.apk
  trader-production-release-v1.0.71.apk
then production release is trader-production-release-v1.0.71.apk.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

CHANGELOG_URLS = {
    "production": (
        "https://azure.charisma.tech/Brokerage/Trader/_wiki/wikis/"
        "Trader.wiki/311/Production"
    ),
    "staging": (
        "https://azure.charisma.tech/Brokerage/Trader/_wiki/wikis/"
        "Trader.wiki/315/Staging"
    ),
    "develop": (
        "https://azure.charisma.tech/Brokerage/Trader/_wiki/wikis/"
        "Trader.wiki/312/Develop"
    ),
}

AZURE_APK_URL = (
    "https://azure.charisma.tech/Brokerage/"
    "e45539a6-393c-4129-9db8-1ce5febabe6c/_apis/git/repositories/"
    "911efa6a-effe-4402-a7c3-dc86278891c0/items"
    "?path=/{environment}/{build_mode}/{apk_file_name}"
    "&versionDescriptor%5BversionOptions%5D=0"
    "&versionDescriptor%5BversionType%5D=0"
    "&versionDescriptor%5Bversion%5D=master"
    "&resolveLfs=true&%24format=octetStream&api-version=5.0&download=true"
)

APK_NAME_RE = re.compile(
    r"^trader-(?P<environment>production|staging|develop)"
    r"-(?P<build_mode>debug|release)"
    r"-v(?P<version>\d+(?:\.\d+)*)"
    r"(?:-(?P<suffix>.+))?\.apk$",
    re.IGNORECASE,
)

ENV_LABEL = {
    "production": "Production",
    "staging": "Staging",
    "develop": "Develop",
}

ENV_ORDER = ("production", "staging", "develop")

# Flag -> list of (environment, build_mode)
TARGET_FLAGS: dict[str, list[tuple[str, str]]] = {
    "p": [("production", "release"), ("production", "debug")],
    "pr": [("production", "release")],
    "pd": [("production", "debug")],
    "s": [("staging", "release"), ("staging", "debug")],
    "sr": [("staging", "release")],
    "sd": [("staging", "debug")],
    "d": [("develop", "release"), ("develop", "debug")],
    "dr": [("develop", "release")],
    "dd": [("develop", "debug")],
}

DEFAULT_FLAGS = ("p", "s", "d")

MAIN_CONTENT_TEMPLATE = """
**⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠙⢷⣤⣤⣴⣶⣶⣦⣤⣤⡾⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣼⣿⣿⣉⣹⣿⣿⣿⣿⣏⣉⣿⣿⣧⠀⠀⠀⠀
⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀
⣠⣄⠀⢠⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⡄⠀⣠⣄
⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿
⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿
⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿
⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿
⠻⠟⠁⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠈⠻⠟
⠀⠀⠀⠀⠉⠉⣿⣿⣿⡏⠉⠉⢹⣿⣿⣿⠉⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⣿⣿⡇⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⣿⣿⡇⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠉⠀⠀⠀⠀⠉⠉⠁⠀**⠀⠀⠀


⠀

Hello everybody....
The latest version of the **Android trader application** can be downloaded from the following links:



{lines}


@pakan @a.sedaghatipour @amiralimadad  @m.mostafaei @sh.ranjbar @s.arshadi
"""


@dataclass(frozen=True, order=True)
class Version:
    parts: tuple[int, ...]

    @classmethod
    def parse(cls, text: str) -> Version:
        return cls(tuple(int(part) for part in text.split(".")))

    def __str__(self) -> str:
        return ".".join(str(part) for part in self.parts)


@dataclass(frozen=True)
class ApkRelease:
    environment: str
    build_mode: str
    version: Version
    file_name: str
    path: Path

    @property
    def azure_url(self) -> str:
        return AZURE_APK_URL.format(
            environment=self.environment,
            build_mode=self.build_mode,
            apk_file_name=self.file_name,
        )


def parse_apk_file(path: Path) -> ApkRelease | None:
    match = APK_NAME_RE.match(path.name)
    if not match:
        return None
    return ApkRelease(
        environment=match.group("environment").lower(),
        build_mode=match.group("build_mode").lower(),
        version=Version.parse(match.group("version")),
        file_name=path.name,
        path=path,
    )


def find_latest_apk(
    repo_root: Path, environment: str, build_mode: str
) -> ApkRelease | None:
    folder = repo_root / environment / build_mode
    if not folder.is_dir():
        return None

    candidates: list[ApkRelease] = []
    for apk_path in folder.glob("*.apk"):
        parsed = parse_apk_file(apk_path)
        if parsed is None:
            continue
        if (
            parsed.environment == environment
            and parsed.build_mode == build_mode
        ):
            candidates.append(parsed)

    if not candidates:
        return None

    return max(candidates, key=lambda apk: apk.version)


def resolve_targets(flags: list[str]) -> tuple[set[tuple[str, str]], list[str]]:
    """Expand flags like p/pr/pd into (environment, build_mode) pairs."""
    targets: set[tuple[str, str]] = set()
    unknown: list[str] = []
    for raw in flags:
        flag = raw.lower()
        mapped = TARGET_FLAGS.get(flag)
        if mapped is None:
            unknown.append(raw)
            continue
        targets.update(mapped)
    return targets, unknown


def build_message(
    repo_root: Path, targets: set[tuple[str, str]]
) -> tuple[str, list[str]]:
    lines: list[str] = []
    summary: list[str] = []

    for environment in ENV_ORDER:
        want_release = (environment, "release") in targets
        want_debug = (environment, "debug") in targets
        if not want_release and not want_debug:
            continue

        release = (
            find_latest_apk(repo_root, environment, "release")
            if want_release
            else None
        )
        debug = (
            find_latest_apk(repo_root, environment, "debug")
            if want_debug
            else None
        )

        if release is None and debug is None:
            missing = []
            if want_release:
                missing.append("release")
            if want_debug:
                missing.append("debug")
            summary.append(f"{environment}: no APK found ({', '.join(missing)})")
            continue

        # Prefer release version for the label; fall back to debug version.
        version = (release or debug).version
        label = ENV_LABEL[environment]
        changelog = CHANGELOG_URLS[environment]

        link_parts: list[str] = []
        if want_release:
            link_parts.append(
                f"[**Release**]({release.azure_url})"
                if release
                else "_Release missing_"
            )
        if want_debug:
            link_parts.append(
                f"[**Debug**]({debug.azure_url})"
                if debug
                else "_Debug missing_"
            )

        links = "     ".join(link_parts)
        lines.append(
            f"**{label} v{version}: **   {links}    [Change Logs]({changelog})"
        )

        parts: list[str] = [f"{environment}: v{version}"]
        if want_release:
            parts.append(f"release={release.file_name if release else '-'}")
        if want_debug:
            parts.append(f"debug={debug.file_name if debug else '-'}")
        summary.append("  ".join(parts))

    message = MAIN_CONTENT_TEMPLATE.format(lines="\n".join(lines)).strip() + "\n"
    return message, summary


def copy_to_clipboard(text: str) -> bool:
    try:
        import subprocess

        for command in (
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
            ["wl-copy"],
        ):
            try:
                subprocess.run(
                    command,
                    input=text.encode("utf-8"),
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
    except Exception:
        return False
    return False


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create Trader update message from the latest APK versions "
            "found under production|staging|develop / release|debug.\n\n"
            "Flags:\n"
            "  p  production release+debug   pr production release   pd production debug\n"
            "  s  staging release+debug      sr staging release      sd staging debug\n"
            "  d  develop release+debug      dr develop release      dd develop debug\n\n"
            "Examples:\n"
            "  %(prog)s\n"
            "  %(prog)s p sr dd\n"
            "  %(prog)s pr sd"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=list(DEFAULT_FLAGS),
        help=(
            "Target flags (default: p s d). "
            "Examples: p, pr, pd, s, sr, sd, d, dr, dd"
        ),
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=REPO_ROOT,
        help="APK repository root (default: this script's directory)",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Also copy the message to the clipboard when possible",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    targets, unknown = resolve_targets(args.targets)
    if unknown:
        known = ", ".join(TARGET_FLAGS)
        print(
            f"Unknown target flag(s): {', '.join(unknown)}. "
            f"Expected one of: {known}",
            file=sys.stderr,
        )
        return 1
    if not targets:
        print(
            "No targets selected. Use flags like: p pr pd s sr sd d dr dd",
            file=sys.stderr,
        )
        return 1

    repo_root = args.repo.resolve()
    message, summary = build_message(repo_root, targets)

    print("Selected APKs (highest version in each folder):")
    for line in summary:
        print(f"  - {line}")
    print("-" * 60)
    print(message)

    if args.copy:
        if copy_to_clipboard(message):
            print("Copied update message to clipboard.", file=sys.stderr)
        else:
            print("Clipboard copy unavailable.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
