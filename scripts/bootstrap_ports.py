"""Fetch digest-pinned port references and build isolated upstream parser probes."""

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from model import ROOT, load_json, mapping, text

CACHE = ROOT / ".cache"


def sources(fetch: bool = False) -> None:
    for name, value in mapping(load_json(ROOT / "tools.lock")["port_sources"]).items():
        record = mapping(value)
        path = CACHE / name
        if not path.is_file() and fetch:
            path.parent.mkdir(parents=True, exist_ok=True)
            request = urllib.request.Request(
                text(record["url"]), headers={"User-Agent": "maesglas-build"}
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                path.write_bytes(response.read())
        if not path.is_file():
            raise ValueError(f"Missing pinned port reference: {name}; run bootstrap_ports.py")
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Port reference digest differs: {name}")


def unpack(archive: str, destination: str, strip_root: bool = False) -> None:
    target = CACHE / "apps" / destination
    marker = target / ".maesglas-unpacked"
    source = CACHE / "downloads" / archive
    expected = hashlib.sha256(source.read_bytes()).hexdigest() + "\n"
    if marker.is_file():
        if marker.read_text() != expected:
            raise ValueError(f"Stale extracted port reference: {destination}")
        return
    target.mkdir(parents=True, exist_ok=True)
    if archive.endswith(".dmg"):
        subprocess.run(
            ["7zz", "x", "-y", "-snld", "-o" + str(target), str(source)],
            stdout=subprocess.DEVNULL,
            check=True,
        )
        for link in target.rglob("*"):
            if link.is_symlink() and not link.resolve().is_relative_to(target):
                raise ValueError("Application archive contains an escaping link")
    elif archive.endswith(".zip"):
        with zipfile.ZipFile(source) as bundle:
            for zip_entry in bundle.infolist():
                if not (target / zip_entry.filename).resolve().is_relative_to(target):
                    raise ValueError("Archive path escapes the tool directory")
        subprocess.run(["bsdtar", "-xf", str(source), "-C", str(target)], check=True)
    else:
        with tarfile.open(source) as bundle:
            for entry in bundle.getmembers():
                if strip_root:
                    entry.name = "/".join(Path(entry.name).parts[1:])
                if entry.name:
                    bundle.extract(entry, target, filter="data")
    marker.write_text(expected)


def probes() -> None:
    lock = load_json(ROOT / "tools.lock")
    result = subprocess.run(["go", "version"], capture_output=True, text=True, check=True)
    if text(lock["go"]) not in result.stdout:
        raise ValueError("Wrong Go version for native parser probes")
    home = CACHE / "probe-build"
    home.mkdir(exist_ok=True)
    env = os.environ | {
        "HOME": str(home),
        "GOPATH": str(CACHE / "go"),
        "GOCACHE": str(CACHE / "go-build"),
        "GOTMPDIR": str(home),
        "TMPDIR": str(home),
        "TMP": str(home),
        "TEMP": str(home),
        "GOENV": "off",
        "GOTOOLCHAIN": "local",
        "GOTELEMETRY": "off",
    }
    for port, probe in (("k9s", "k9s"), ("gh-dash", "gh_dash")):
        source = CACHE / "apps" / f"{port}-source"
        command = source / "cmd/maesglas-validate"
        command.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / f"scripts/probes/{probe}.go", command / "main.go")
        output = CACHE / "tools/bin" / f"maesglas-{port}-validate"
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "go",
                "build",
                "-mod=readonly",
                "-trimpath",
                "-o",
                str(output),
                "./cmd/maesglas-validate",
            ],
            cwd=source,
            env=env,
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify cached source digests only")
    args = parser.parse_args()
    sources(fetch=not args.check)
    if not args.check:
        for archive, target in (
            ("k9s-v0.51.0-source.tar.gz", "k9s-source"),
            ("gh-dash-v4.26.0-source.tar.gz", "gh-dash-source"),
            ("vscode-1.143.1-source.tar.gz", "vscode-source"),
            ("fsyh-v1.67.tar.gz", "fsyh"),
        ):
            unpack(archive, target, strip_root=True)
        if platform.system() == "Darwin":
            for archive, target in (
                ("Alacritty-v0.17.0.dmg", "alacritty"),
                ("kitty-0.49.2.dmg", "kitty"),
                ("WezTerm-macos-20240203-110809-5046fc22.zip", "wezterm"),
                ("nvim-macos-arm64.tar.gz", "neovim"),
                ("helix-25.07.1-aarch64-macos.tar.xz", "helix"),
            ):
                unpack(archive, target)
        probes()
    print("PASS pinned port references")


if __name__ == "__main__":
    main()
