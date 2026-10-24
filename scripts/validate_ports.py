"""Exercise shipped ports with native tools and disposable user state."""

import argparse
import datetime
import errno
import fcntl
import hashlib
import json
import os
import platform
import pty
import re
import select
import shutil
import struct
import subprocess
import tempfile
import termios
import time
from pathlib import Path

from model import MODES, ROOT, load, load_json, text
from port_renderers import PORTS


def has_color(output: str, color: str) -> bool:
    red, green, blue = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return re.search(rf"(?:38|48);2;{red};{green};{blue}(?:m|;)", output) is not None


VERSION_ARGS = {
    "ghostty": ["+version"],
    "starship": ["--version"],
    "vim": ["--version"],
    "bat": ["--version"],
    "delta": ["--version"],
    "git": ["--version"],
    "nano": ["--version"],
    "fzf": ["--version"],
    "tmux": ["-V"],
    "eza": ["--version"],
    "glow": ["--version"],
    "lazygit": ["--version"],
    "yazi": ["--version"],
}


def run(args: list[str], env: dict[str, str], cwd: Path, input_text: str | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        input=input_text,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"{Path(args[0]).name}: native check exited {result.returncode}")
    if result.stderr and re.search(
        r"(?i)(unknown (key|field|theme)|invalid|failed to (parse|load))", result.stderr
    ):
        raise RuntimeError(f"{Path(args[0]).name}: native loader reported invalid configuration")
    return result.stdout


def terminal(
    args: list[str],
    env: dict[str, str],
    cwd: Path,
    quit_keys: bytes,
    wait: float = 1.2,
    background: str | None = None,
) -> str:
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 32, 110, 0, 0))
    output = bytearray()

    def own_terminal() -> None:
        os.setsid()
        fcntl.ioctl(0, termios.TIOCSCTTY, 0)

    with subprocess.Popen(
        args,
        cwd=cwd,
        env=env,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        preexec_fn=own_terminal,
    ) as process:
        os.close(slave)
        next_input = wait
        start = time.monotonic()
        try:
            while time.monotonic() - start < 20:
                if time.monotonic() - start > next_input:
                    os.write(master, quit_keys)
                    next_input += 1.5
                if select.select([master], [], [], 0.1)[0]:
                    try:
                        data = os.read(master, 65536)
                    except OSError as error:
                        if error.errno != errno.EIO:
                            raise
                        break
                    if not data:
                        break
                    output.extend(data)
                    if b"\x1b[6n" in data:
                        os.write(master, b"\x1b[1;1R")
                    if b"\x1b]11;?" in data and background is not None:
                        channels = "/".join(background[i : i + 2] * 2 for i in (1, 3, 5))
                        os.write(master, f"\x1b]11;rgb:{channels}\x1b\\".encode())
                if process.poll() is not None:
                    break
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                diagnostic = output.decode(errors="replace")
                diagnostic = diagnostic.replace(str(ROOT), "<source>").replace(
                    str(cwd), "<fixture>"
                )
                (ROOT / ".cache/native-failure.txt").write_text(diagnostic)
                raise RuntimeError(
                    f"{Path(args[0]).name}: did not exit after the test input"
                ) from None
            if process.returncode not in (0, 130):
                raise RuntimeError(f"{Path(args[0]).name}: PTY check exited {process.returncode}")
        finally:
            os.close(master)
    result = output.decode(errors="replace")
    if not result:
        raise RuntimeError(f"{Path(args[0]).name}: no terminal output")
    errors = (
        r"(?i)(error in .*(?:nanorc|theme)|unknown (?:color|option)|"
        r"failed to (?:parse|load)|TOML parse error)"
    )
    if re.search(errors, result):
        raise RuntimeError(f"{Path(args[0]).name}: rejected the generated configuration")
    return result


def environment(root: Path) -> dict[str, str]:
    env = {
        "PATH": os.environ["PATH"],
        "HOME": str(root),
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
        "XDG_RUNTIME_DIR": str(root / "run"),
        "TMPDIR": str(root / "tmp"),
        "TMP": str(root / "tmp"),
        "TEMP": str(root / "tmp"),
        "TERM": "xterm-256color",
        "COLORTERM": "truecolor",
        "LANG": "en_US.UTF-8" if platform.system() == "Darwin" else "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": str(root / "gitconfig"),
        "GIT_TERMINAL_PROMPT": "0",
        "BAT_CONFIG_DIR": str(root / "bat"),
        "BAT_CACHE_PATH": str(root / "cache/bat"),
        "STARSHIP_CACHE": str(root / "starship-cache"),
        "YAZI_CONFIG_HOME": str(root / "yazi"),
        "YAZI_STATE_HOME": str(root / "yazi-state"),
        "YAZI_CACHE_HOME": str(root / "yazi-cache"),
        "EZA_CONFIG_DIR": str(root / "eza"),
        "DO_NOT_TRACK": "1",
    }
    for key, value in env.items():
        if key.endswith(("_HOME", "_DIR", "_PATH", "_CACHE")) and key != "GIT_CONFIG_GLOBAL":
            Path(value).mkdir(parents=True, exist_ok=True)
    (root / "tmp").mkdir()
    (root / "run").chmod(0o700)
    return env


def validate(root: Path, selected: set[str]) -> dict[str, str]:
    env = environment(root)
    work = root / "orchard"
    work.mkdir()
    run(["git", "init", "-q", "-b", "main", str(work)], env, root)
    (work / "harvest.py").write_text("def harvest(rows):\n    return rows\n")
    (work / "README.md").write_text("# Orchard\n\nA small plot.\n\n```python\nreturn 12\n```\n")
    (work / "src").mkdir()
    diff = "--- a/harvest.py\n+++ b/harvest.py\n@@ -1 +1 @@\n-return 11\n+return 12\n"
    results: dict[str, str] = {}
    if selected & {"textmate", "delta"}:
        themes = root / "bat/themes"
        themes.mkdir(parents=True)
        for mode in MODES:
            shutil.copyfile(
                ROOT / f"ports/textmate/maesglas-{mode}.tmTheme",
                themes / f"maesglas-{mode}.tmTheme",
            )
        run(["bat", "cache", "--build"], env, work)
        listing = run(["bat", "--list-themes", "--color=never"], env, work)
        if any(f"maesglas-{mode}" not in listing for mode in MODES):
            raise RuntimeError("bat did not register both theme names")
    for mode in MODES:
        palette = load().colors[mode]

        def path(port: str, mode: str = mode) -> str:
            return str(ROOT / f"ports/{port}/maesglas-{mode}.{PORTS[port][1]}")

        for port in sorted(selected):
            result = ""
            if port == "ghostty":
                run(["ghostty", "+validate-config", "--config-file=" + path(port)], env, work)
            elif port == "starship":
                current = env | {"STARSHIP_CONFIG": path(port), "STARSHIP_LOG": "trace"}
                run(["starship", "print-config"], current, work)
                result = run(["starship", "prompt", "--status", "7"], current, work)
                if "exit 7" not in result or "main" not in result:
                    raise RuntimeError("Starship lost branch or exit status")
                if not has_color(result, palette["branch"]):
                    raise RuntimeError("Starship did not apply the branch color")
            elif port == "vim":
                query = root / f"vim-{mode}.txt"
                run(
                    [
                        "vim",
                        "-Nu",
                        "NONE",
                        "-i",
                        "NONE",
                        "-n",
                        "-es",
                        "-c",
                        "source " + path(port),
                        "-c",
                        "redir! > " + str(query),
                        "-c",
                        "silent highlight Normal",
                        "-c",
                        "redir END",
                        "-c",
                        "qa!",
                    ],
                    env,
                    work,
                )
                if load().colors[mode]["ink"] not in query.read_text():
                    raise RuntimeError("Vim did not apply the foreground")
            elif port == "textmate":
                result = run(
                    [
                        "bat",
                        "--theme",
                        f"maesglas-{mode}",
                        "--color=always",
                        "--style=plain",
                        str(work / "harvest.py"),
                    ],
                    env,
                    work,
                )
                if not has_color(result, palette["keyword"]):
                    raise RuntimeError("bat did not render colored syntax")
            elif port == "delta":
                config = root / ".gitconfig"
                config.write_text(
                    Path(path(port)).read_text()
                    + f'\n[delta "review"]\n    features = maesglas-{mode}\n'
                    '    side-by-side = true\n[delta "interactive"]\n'
                    f"    features = maesglas-{mode}\n    color-only = true\n"
                    "    side-by-side = false\n    line-numbers = false\n"
                )
                current = env | {"GIT_CONFIG_GLOBAL": str(config)}
                for feature in (f"maesglas-{mode}", "review", "interactive"):
                    rendered = run(
                        ["delta", "--features", feature, "--paging=never", "--true-color=always"],
                        current,
                        work,
                        diff,
                    )
                    if not has_color(rendered, palette["added"]):
                        raise RuntimeError("delta did not render the composed feature")
                    if feature == "interactive":
                        plain = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", rendered)
                        if plain != diff:
                            raise RuntimeError("delta changed interactive patch structure")
                    result += rendered
            elif port == "git":
                keys = run(
                    ["git", "config", "--file", path(port), "--name-only", "--list"], env, work
                )
                for key in keys.splitlines():
                    result = run(
                        ["git", "config", "--file", path(port), "--get-color", key], env, work
                    )
                    if "\x1b[" not in result:
                        raise RuntimeError("Git did not parse a color")
                    expected = run(
                        ["git", "config", "--file", path(port), "--get", key], env, work
                    ).strip()
                    if not has_color(result, expected):
                        raise RuntimeError("Git changed a declared color")
            elif port == "nano":
                for syntax in (
                    "python",
                    "ruby",
                    "rust",
                    "shell",
                    "json",
                    "yaml",
                    "toml",
                    "markdown",
                    "makefile",
                    "diff",
                ):
                    result = terminal(
                        [
                            "nano",
                            "--rcfile",
                            path(port),
                            "--syntax",
                            syntax,
                            str(work / "harvest.py"),
                        ],
                        env,
                        work,
                        b"\x18",
                        wait=0.15,
                    )
                    if "Error in" in result or "Unknown syntax" in result:
                        raise RuntimeError("nano rejected a syntax")
            elif port == "fzf":
                match = re.search(r"--color=([^ ]+)", Path(path(port)).read_text())
                if not match:
                    raise RuntimeError("Missing picker color argument")
                result = terminal(["fzf", "--color=" + match[1], "--no-sort"], env, work, b"\x03")
                if not has_color(result, palette["canvas"]):
                    raise RuntimeError("fzf did not apply the canvas")
            elif port == "tmux":
                socket = str(root / f"tmux-{mode}.sock")
                command = ["tmux", "-S", socket, "-f", path(port)]
                try:
                    run(command + ["new-session", "-d", "-s", "check", "sleep 20"], env, work)
                    result = run(command + ["show-options", "-gv", "status-style"], env, work)
                    if load().colors[mode]["ink"].lower() not in result.lower():
                        raise RuntimeError("tmux did not apply status colors")
                finally:
                    run(command + ["kill-server"], env, work)
            elif port == "eza":
                shutil.copyfile(path(port), root / "eza/theme.yml")
                result = run(
                    ["eza", "--long", "--classify=always", "--icons=never", "--color=always", "."],
                    env,
                    work,
                )
                visible = re.sub(r"\x1b\[[0-9;]*m", "", result)
                if "harvest.py" not in visible or "\x1b[" not in result:
                    raise RuntimeError("eza did not render the fixture")
                if not has_color(result, palette["directory"]):
                    raise RuntimeError("eza did not apply the directory color")
            elif port == "glow":
                result = run(
                    ["glow", "--style", path(port), "--width", "70", "-"],
                    env | {"CLICOLOR_FORCE": "1"},
                    work,
                    (work / "README.md").read_text(),
                )
                if "Orchard" not in result:
                    raise RuntimeError("glow did not render Markdown")
                if not has_color(result, palette["ink"]):
                    raise RuntimeError("glow did not apply the reading color")
            elif port == "lazygit":
                config_dir = root / f"lazygit-{mode}"
                config_dir.mkdir()
                bootstrap = config_dir / "state.yml"
                bootstrap.write_text("lastupdatecheck: 9999999999\nstartupPopupVersion: 99\n")
                result = terminal(
                    [
                        "lazygit",
                        "--use-config-dir",
                        str(config_dir),
                        "--use-config-file",
                        path(port),
                    ],
                    env | {"LG_CONFIG_FILE": path(port)},
                    work,
                    b"q",
                    wait=2,
                )
                if not has_color(result, palette["ink"]):
                    raise RuntimeError("lazygit did not apply the reading color")
            elif port == "yazi":
                shutil.copyfile(path(port), root / "yazi/theme.toml")
                shutil.copytree(
                    ROOT / f"ports/yazi/maesglas-{mode}.yazi",
                    root / f"yazi/flavors/maesglas-{mode}.yazi",
                )
                result = terminal(
                    ["yazi", str(work)],
                    env,
                    work,
                    b"q",
                    wait=2,
                    background=palette["canvas"],
                )
                if not has_color(result, palette["ink"]):
                    raise RuntimeError("yazi did not apply the reading color")
            observed = {
                "#" + "".join(f"{int(channel):02X}" for channel in channels)
                for channels in re.findall(r"(?:38|48);2;(\d+);(\d+);(\d+)", result)
            }
            if observed - set(palette.values()):
                raise RuntimeError(f"{port}: emitted a color outside the selected palette")
            indexed = re.findall(r"(?:38|48);5;(\d+)", result)
            if any(int(index) > 15 for index in indexed):
                raise RuntimeError(f"{port}: emitted an unthemed indexed color")
            results[f"{port}/{mode}"] = "PASS"
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=PORTS)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.record and args.only:
        raise SystemExit("Record a complete platform run, not selected ports.")
    selected = set(args.only or PORTS)
    if platform.system() != "Darwin":
        selected.discard("ghostty")
    lock = load_json(ROOT / "tools.lock")
    for port in selected:
        binary = "bat" if port == "textmate" else port
        if shutil.which(binary) is None:
            raise SystemExit(f"Missing native validator: {binary}")
        result = subprocess.run(
            [binary, *VERSION_ARGS[binary]],
            capture_output=True,
            text=True,
            check=True,
        )
        if text(lock[binary]) not in result.stdout + result.stderr:
            raise SystemExit(f"Wrong native validator version: {binary}")
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ports-", dir=cache) as directory:
        results = validate(Path(directory), selected)
    (cache / "ports.json").write_text(json.dumps(results, indent=2) + "\n")
    if args.record:
        path = ROOT / "identity/validation.json"
        record = load_json(path) if path.exists() else {}
        inputs = {
            str(file.relative_to(ROOT)): hashlib.sha256(file.read_bytes()).hexdigest()
            for port in sorted(selected)
            for file in sorted((ROOT / "ports" / port).rglob("*"))
            if file.is_file()
        }
        record[platform.system()] = {
            "date": datetime.date.today().isoformat(),
            "checks": results,
            "inputs": inputs,
            "versions": {
                port: lock["bat" if port == "textmate" else port] for port in sorted(selected)
            },
            "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
        path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"PASS ports: {len(results)} native checks")


if __name__ == "__main__":
    main()
