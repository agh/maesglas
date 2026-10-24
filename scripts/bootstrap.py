"""Install Linux check executables into the checkout's disposable tool cache."""

import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from model import ROOT, load_json, mapping, sequence, text

DEST = ROOT / ".cache/tools"


def cached(binary: str) -> bool:
    path = DEST / "bin" / binary
    if not path.is_file():
        return False
    flags = {"gitleaks": ["version"], "tmux": ["-V"]}.get(binary, ["--version"])
    result = subprocess.run([str(path), *flags], capture_output=True, text=True, check=False)
    return result.returncode == 0 and text(load_json(ROOT / "tools.lock")[binary]) in (
        result.stdout + result.stderr
    )


def download(url: str, api: bool = False) -> bytes:
    headers = {"User-Agent": "maesglas-build", "Accept": "application/vnd.github+json"}
    if api and os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=120) as response:
        payload: object = response.read()
    if not isinstance(payload, bytes):
        raise ValueError("Download did not return bytes")
    return payload


def release(repo: str, tag: str, asset_name: str, binary: str) -> None:
    if cached(binary):
        print(f"Using pinned {binary}", flush=True)
        return
    value: object = json.loads(
        download(f"https://api.github.com/repos/{repo}/releases/tags/{tag}", True)
    )
    assets = [mapping(asset) for asset in sequence(mapping(value)["assets"])]
    matches = [asset for asset in assets if asset["name"] == asset_name]
    if len(matches) != 1:
        raise ValueError(f"Missing release asset for {binary}")
    asset = matches[0]
    digest = text(asset["digest"]).removeprefix("sha256:")
    payload = download(text(asset["browser_download_url"]))
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError(f"Release asset digest differs: {binary}")
    if asset_name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            names = [name for name in archive.namelist() if Path(name).name == binary]
            if len(names) != 1:
                raise ValueError(f"Ambiguous executable in {binary} archive")
            executable = archive.read(names[0])
    elif asset_name.endswith((".tar.gz", ".tar.xz")):
        with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
            members = [
                member
                for member in archive.getmembers()
                if Path(member.name).name == binary and member.isfile()
            ]
            if len(members) != 1:
                raise ValueError(f"Ambiguous executable in {binary} archive")
            stream = archive.extractfile(members[0])
            if stream is None:
                raise ValueError(f"Unreadable executable: {binary}")
            executable = stream.read()
    else:
        executable = payload
    target = DEST / "bin" / binary
    target.write_bytes(executable)
    target.chmod(0o755)
    print(f"Installed {binary}", flush=True)


def source_build(name: str, url: str, configure: list[str] | None, make_args: list[str]) -> None:
    if cached(name):
        print(f"Using pinned {name}", flush=True)
        return
    build = DEST / "build" / name
    build.mkdir(parents=True, exist_ok=True)
    payload = download(url)
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        archive.extractall(build, filter="data")
    roots = list(build.iterdir())
    if len(roots) != 1:
        raise ValueError(f"Ambiguous build root: {name}")
    cwd = roots[0]
    if configure is not None:
        subprocess.run(["./configure", "--prefix=" + str(DEST), *configure], cwd=cwd, check=True)
    subprocess.run(["make", "-j2", *make_args], cwd=cwd, check=True)
    subprocess.run(["make", "install", *make_args], cwd=cwd, check=True)
    shutil.rmtree(build)
    print(f"Built {name}", flush=True)


def main() -> None:
    if platform.system() != "Linux":
        raise SystemExit("This bootstrap is for Linux; local checks use installed tools.")
    (DEST / "bin").mkdir(parents=True, exist_ok=True)
    lock = load_json(ROOT / "tools.lock")
    for tool, version in mapping(lock["linux_build"]).items():
        args = ["-dumpfullversion"] if tool == "cc" else ["--version"]
        result = subprocess.run([tool, *args], capture_output=True, text=True, check=True)
        if text(version) not in result.stdout:
            raise SystemExit(f"Wrong Linux build tool version: {tool}")
    arch = "aarch64" if platform.machine() == "aarch64" else "x86_64"
    go_arch = "arm64" if arch == "aarch64" else "amd64"
    vale_arch = "arm64" if arch == "aarch64" else "64-bit"
    specs = {
        "vale": ("vale-cli/vale", "v{v}", f"vale_{{v}}_Linux_{vale_arch}.tar.gz"),
        "gitleaks": (
            "gitleaks/gitleaks",
            "v{v}",
            f"gitleaks_{{v}}_linux_{'arm64' if arch == 'aarch64' else 'x64'}.tar.gz",
        ),
        "shellcheck": ("koalaman/shellcheck", "v{v}", f"shellcheck-v{{v}}.linux.{arch}.tar.xz"),
        "shfmt": ("mvdan/sh", "v{v}", f"shfmt_v{{v}}_linux_{go_arch}"),
        "lychee": ("lycheeverse/lychee", "lychee-v{v}", f"lychee-{arch}-unknown-linux-musl.tar.gz"),
        "starship": ("starship/starship", "v{v}", f"starship-{arch}-unknown-linux-musl.tar.gz"),
        "bat": ("sharkdp/bat", "v{v}", f"bat-v{{v}}-{arch}-unknown-linux-musl.tar.gz"),
        "delta": ("dandavison/delta", "{v}", f"delta-{{v}}-{arch}-unknown-linux-gnu.tar.gz"),
        "fzf": ("junegunn/fzf", "v{v}", f"fzf-{{v}}-linux_{go_arch}.tar.gz"),
        "eza": ("eza-community/eza", "v{v}", f"eza_{arch}-unknown-linux-gnu.tar.gz"),
        "glow": (
            "charmbracelet/glow",
            "v{v}",
            f"glow_{{v}}_Linux_{'arm64' if arch == 'aarch64' else 'x86_64'}.tar.gz",
        ),
        "lazygit": (
            "jesseduffield/lazygit",
            "v{v}",
            f"lazygit_{{v}}_linux_{'arm64' if arch == 'aarch64' else 'x86_64'}.tar.gz",
        ),
        "yazi": ("sxyazi/yazi", "v{v}", f"yazi-{arch}-unknown-linux-musl.zip"),
    }
    for binary, (repo, tag, asset) in specs.items():
        version = text(lock[binary])
        release(repo, tag.format(v=version), asset.format(v=version), binary)
    source_build(
        "git",
        f"https://www.kernel.org/pub/software/scm/git/git-{text(lock['git'])}.tar.xz",
        None,
        [
            f"prefix={DEST}",
            "NO_GETTEXT=YesPlease",
            "NO_TCLTK=YesPlease",
            "NO_CURL=YesPlease",
            "NO_OPENSSL=YesPlease",
            "NO_EXPAT=YesPlease",
            "NO_RUST=YesPlease",
        ],
    )
    source_build(
        "nano",
        f"https://www.nano-editor.org/dist/v9/nano-{text(lock['nano'])}.tar.xz",
        ["--disable-nls"],
        [],
    )
    source_build(
        "tmux",
        f"https://github.com/tmux/tmux/releases/download/{text(lock['tmux'])}/tmux-{text(lock['tmux'])}.tar.gz",
        [],
        [],
    )
    source_build(
        "vim",
        f"https://github.com/vim/vim/archive/refs/tags/v{text(lock['vim_build'])}.tar.gz",
        ["--with-features=normal", "--disable-gui", "--without-x", "--disable-nls"],
        [],
    )
    print("Linux tools are ready in .cache/tools/bin")


if __name__ == "__main__":
    main()
