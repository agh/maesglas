"""The same fail-closed checks for a local checkout and CI."""

import hashlib
import importlib.metadata
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from check import public_files
from model import ROOT, load, load_json, mapping, text


def command(args: list[str], label: str) -> None:
    result = subprocess.run(args, cwd=ROOT, check=False)
    if result.returncode:
        raise SystemExit(f"FAIL {label} (exit {result.returncode})")
    print(f"PASS {label}", flush=True)


def versions() -> None:
    lock = load_json(ROOT / "tools.lock")
    tools = {
        "vale": ["--version"],
        "gitleaks": ["version"],
        "shellcheck": ["--version"],
        "shfmt": ["--version"],
        "lychee": ["--version"],
        "uv": ["--version"],
        "node": ["--version"],
        "npm": ["--version"],
    }
    for tool, args in tools.items():
        if shutil.which(tool) is None:
            raise SystemExit(f"Missing gate tool: {tool}")
        result = subprocess.run([tool, *args], capture_output=True, text=True, check=True)
        if text(lock[tool]) not in result.stdout + result.stderr:
            raise SystemExit(f"Wrong gate tool version: {tool}")
    if ".".join(str(v) for v in sys.version_info[:3]) != lock["python"]:
        raise SystemExit("Wrong Python version")
    packages = mapping(load_json(ROOT / "package.json")["devDependencies"])
    if packages != mapping(lock["node_packages"]):
        raise SystemExit("Package versions differ from tools.lock")
    for name, expected in packages.items():
        package = load_json(ROOT / "node_modules" / name / "package.json")
        if package["version"] != expected:
            raise SystemExit(f"Wrong installed check package: {name}")
    for name, expected in mapping(lock["python_packages"]).items():
        if importlib.metadata.version(name) != expected:
            raise SystemExit(f"Wrong installed check package: {name}")
    print("PASS tool versions", flush=True)


def prose_package() -> None:
    lock = load_json(ROOT / "tools.lock")
    url = f"https://github.com/agh/crefft/releases/download/v{text(lock['crefft'])}/Crefft.zip"
    if f"Packages = {url}" not in (ROOT / ".vale.ini").read_text():
        raise SystemExit("Prose package URL differs from tools.lock")
    with urllib.request.urlopen(url, timeout=30) as response:
        payload: object = response.read()
    if not isinstance(payload, bytes):
        raise SystemExit("Prose package download did not return bytes")
    if hashlib.sha256(payload).hexdigest() != lock["crefft_sha256"]:
        raise SystemExit("Prose package digest differs from tools.lock")
    command(["vale", "--no-global", "sync"], "prose package and digest")


def scan() -> None:
    env = os.environ.copy()
    env.pop("GITLEAKS_CONFIG", None)
    env.pop("GITLEAKS_CONFIG_TOML", None)
    options = ["--no-banner", "--redact", "--ignore-gitleaks-allow", "--log-level=warn"]
    with tempfile.TemporaryDirectory(prefix="scan-", dir=ROOT / ".cache") as directory:
        stage = Path(directory)
        for source in public_files():
            destination = stage / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        result = subprocess.run(["gitleaks", "dir", *options, str(stage)], env=env, check=False)
        if result.returncode:
            raise SystemExit("FAIL file scan")
    print("PASS file scan", flush=True)
    history = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        check=False,
    )
    if history.returncode == 0:
        command(["gitleaks", "git", *options, "--log-opts=--all", "."], "history scan")
    elif (ROOT / ".git").exists():
        print("PASS history scan: no commits to scan", flush=True)
    else:
        raise SystemExit("History scan requires a Git checkout")


def link_exclusions() -> list[str]:
    # The site's own output is exercised at /maesglas/ by the local browser gate.
    exclusions = [r"^https://agh\.github\.io/maesglas/$"]
    version = load().version
    request = urllib.request.Request(
        f"https://api.github.com/repos/agh/maesglas/git/ref/tags/v{version}",
        headers={"User-Agent": "maesglas-gate", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30):
            return [argument for pattern in exclusions for argument in ("--exclude", pattern)]
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise SystemExit("Could not determine whether the public release tag exists") from error
        print(
            f"PENDING public release links: owner has not pushed v{version}; "
            "the tag run checks them without exclusions",
            flush=True,
        )
        escaped = version.replace(".", r"\.")
        exclusions.extend(
            [
                rf"^https://github\.com/agh/maesglas/compare/v{escaped}\.\.\.HEAD$",
                rf"^https://github\.com/agh/maesglas/releases/tag/v{escaped}$",
            ]
        )
    return [argument for pattern in exclusions for argument in ("--exclude", pattern)]


def main() -> None:
    (ROOT / ".cache").mkdir(exist_ok=True)
    versions()
    command(["uv", "run", "--locked", "ruff", "check", "scripts", "tests"], "Python lint")
    command(
        ["uv", "run", "--locked", "ruff", "format", "--check", "scripts", "tests"], "Python format"
    )
    command(["uv", "run", "--locked", "mypy", "scripts", "tests"], "Mypy")
    command(["npx", "--no-install", "pyright"], "Pyright")
    shells = [str(path.relative_to(ROOT)) for path in public_files() if path.suffix == ".sh"]
    command(["shellcheck", *shells], "ShellCheck")
    command(["shfmt", "-i", "2", "-ci", "-bn", "-d", *shells], "shfmt")
    command(
        [
            "npx",
            "--no-install",
            "prettier",
            "--check",
            "site/layout.css",
            "site/app.js",
            "site/choice.js",
            "scripts/browser.mjs",
            ".github/**/*.yml",
            ".github/**/*.md",
            "docs/design.md",
            "CONTRIBUTING.md",
            "AGENTS.md",
            "SECURITY.md",
            "CHANGELOG.md",
            "THIRD_PARTY_NOTICES.md",
        ],
        "authored text and web format",
    )
    command(["npx", "--no-install", "stylelint", "site/*.css"], "CSS lint")
    command(["npx", "--no-install", "markdownlint-cli2", "**/*.md"], "Markdown structure")
    prose_package()
    prose = [
        str(path.relative_to(ROOT)) for path in public_files() if path.suffix in (".md", ".html")
    ]
    command(["vale", "--no-global", *prose], "prose")
    command(["uv", "run", "--locked", "codespell"], "spelling")
    scan()
    command([sys.executable, "scripts/generate.py", "--check"], "generated files")
    command([sys.executable, "scripts/outline_face.py", "--check"], "font outlines")
    command([sys.executable, "scripts/check.py"], "source invariants")
    command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "unit tests")
    command([sys.executable, "scripts/validate_ports.py"], "native ports")
    command([sys.executable, "scripts/validate_extended.py"], "additional native and schema ports")
    command(["node", "scripts/browser.mjs"], "browser")
    command(
        [
            "npx",
            "--no-install",
            "impeccable@4.7.0",
            "detect",
            "--no-config",
            "--json",
            "site/",
        ],
        "design detector",
    )
    command(
        ["lychee", "--no-progress", "--max-retries", "2", *link_exclusions(), *prose],
        "links",
    )
    print("PASS gate", flush=True)


if __name__ == "__main__":
    main()
