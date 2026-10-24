"""Repository invariants, source-derived contrast, and local link integrity."""

import argparse
import hashlib
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from colors import MACHADO, SYNTAX_PAIRS, apca, simulated_distance, wcag
from model import ROOT, Design, load, load_json, mapping, text
from validate_extended import evidence as extended_evidence


def contrast(design: Design) -> tuple[int, float]:
    pairs = 0
    minimum = 21.0
    for mode, p in design.colors.items():
        roles = list(design.roles.values()) + design.ansi
        for role in roles:
            for ground in design.grounds:
                ratio = wcag(p[role], p[ground])
                if ratio < 4.5:
                    raise ValueError(f"Contrast below 4.5: {mode}/{role}/{ground}")
                minimum = min(minimum, ratio)
                pairs += 1
        for role in ("boundary", "type"):
            for ground in design.grounds:
                if wcag(p[role], p[ground]) < 3:
                    raise ValueError(f"Boundary below 3: {mode}/{role}/{ground}")
        for role, target in (("ink", 90), ("secondary", 75), ("muted", 75)):
            if abs(apca(p[role], p["canvas"])) < target:
                raise ValueError(f"Canvas APCA below {target}: {mode}/{role}")
            for ground in design.grounds:
                if abs(apca(p[role], p[ground])) < 60:
                    raise ValueError(f"Emphasis APCA below 60: {mode}/{role}/{ground}")
        for a, b in SYNTAX_PAIRS:
            for condition in MACHADO:
                if simulated_distance(p[a], p[b], condition) < 5:
                    raise ValueError(f"Color-vision distance below 5: {mode}/{a}/{b}/{condition}")
        if p["branch"] != p[design.ansi[5]]:
            raise ValueError("Branch identity differs from slot 5")
    return pairs, minimum


def public_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return [ROOT / name.decode() for name in result.stdout.split(b"\0") if name]


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in ("src", "href") and value:
                self.links.append(value)
            if key == "id" and value:
                self.ids.add(value)


def links() -> int:
    count = 0
    for path in public_files():
        if path.suffix not in (".md", ".html", ".css"):
            continue
        content = path.read_text()
        parser = Links()
        parser.feed(content)
        targets = parser.links
        if path.suffix == ".md":
            targets += re.findall(r"!?\[[^]]*\]\(([^ )]+)(?: +[^)]*)?\)", content)
        if path.suffix == ".css":
            targets += re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', content)
        for url in targets:
            parts = urlsplit(html_unescape(url))
            if parts.scheme or parts.netloc:
                continue
            target = path.parent / unquote(parts.path) if parts.path else path
            if not target.exists():
                raise ValueError(f"Broken local link in {path.relative_to(ROOT)}: {url}")
            if parts.fragment and target.suffix == ".html":
                target_parser = Links()
                target_parser.feed(target.read_text())
                if parts.fragment not in target_parser.ids:
                    raise ValueError(f"Missing HTML anchor: {url}")
            count += 1
    return count


def html_unescape(value: str) -> str:
    from html import unescape

    return unescape(value)


def publication() -> int:
    count = 0
    forbidden_paths = re.compile(r"(?:/Users/|/home/|/private/|[A-Z]:\\Users\\)")
    banned_name = re.compile(r"field[g]lass", re.I)
    attribution = re.compile(
        r"(?i)([c]o-authored-by:|generated (?:by|with) .*(?:\bA[I]\b|copi[l]ot|clau[d]e))"
    )
    for path in public_files():
        name = str(path.relative_to(ROOT))
        if re.search(r"(?i)(secret|token|password|credential)", name):
            raise ValueError(f"Prohibited file name: {name}")
        if path.suffix in (".otf", ".png", ".zip") or name in ("uv.lock", "package-lock.json"):
            continue
        content = path.read_text()
        if banned_name.search(content) or attribution.search(content):
            raise ValueError(f"Publication naming failure: {name}")
        # Match literal personal paths in prose, not the scanner's own expressions.
        if path.suffix in (".md", ".html", ".svg") and forbidden_paths.search(content):
            raise ValueError(f"Personal path in public text: {name}")
        if name in ("README.md", "CHANGELOG.md") and "[unchecked]" in content:
            raise ValueError(f"Unverified marketing claim: {name}")
        count += 1
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
    for path in (ROOT / "site/fonts").iterdir():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest not in notice:
            raise ValueError(f"Missing font rights record: {path.name}")
    return count


def claims() -> int:
    tools = re.compile(
        r"\b(?:Ghostty|Starship|Vim|Git|Yazi|Commit Mono|iTerm2|Terminal\.app|"
        r"Alacritty|kitty|WezTerm|Windows Terminal|VS Code|Zed|Helix|Neovim|"
        r"k9s|gh-dash|Claude Code|fast-syntax-highlighting|Sublime Text|"
        r"nano|bat|delta|fzf|tmux|eza|glow|btop|lazygit)\b"
    )
    count = 0
    paths = [ROOT / "README.md", ROOT / "THIRD_PARTY_NOTICES.md", ROOT / "site/index.html"]
    paths.extend((ROOT / "docs").glob("*.md"))
    for path in paths:
        content = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
        content = re.sub(r"<(pre|select|script|style)\b[^>]*>.*?</\1>", "", content, flags=re.S)
        content = re.sub(r"</p>", "\n\n", content)
        content = re.sub(r"<[^>]*>", "", content)
        for paragraph in re.split(r"\n\s*\n", content):
            if paragraph.lstrip().startswith("#") or not tools.search(paragraph):
                continue
            if len(paragraph.split()) < 4:
                continue
            if paragraph.strip().startswith(("http", "Source:")):
                continue
            if "[checked:" not in paragraph and "[unchecked]" not in paragraph:
                raise ValueError(f"Untagged compatibility claim in {path.relative_to(ROOT)}")
            count += 1
    return count


def evidence() -> None:
    records = load_json(ROOT / "identity/validation.json")
    lock = load_json(ROOT / "tools.lock")
    validator = hashlib.sha256((ROOT / "scripts/validate_ports.py").read_bytes()).hexdigest()
    if "Darwin" not in records:
        raise ValueError("Missing native macOS evidence")
    for platform, value in records.items():
        record = mapping(value)
        if record["validator_sha256"] != validator:
            raise ValueError(f"Stale validator evidence: {platform}")
        for name, expected in mapping(record["inputs"]).items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"Stale input evidence: {platform}/{name}")
        for port, version in mapping(record["versions"]).items():
            if version != lock["bat" if port == "textmate" else port]:
                raise ValueError(f"Stale version evidence: {platform}/{port}")
        checks = mapping(record["checks"])
        if not checks or any(text(result) != "PASS" for result in checks.values()):
            raise ValueError(f"Incomplete native evidence: {platform}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contrast", action="store_true")
    args = parser.parse_args()
    pairs, minimum = contrast(load())
    print(f"PASS contrast: {pairs} text pairs; minimum {minimum:.6f}:1")
    print("PASS APCA targets, essential boundaries, and three color-vision simulations")
    if not args.contrast:
        print(f"PASS publication: {publication()} text files and font digests")
        print(f"PASS claims: {claims()} tagged compatibility passages")
        print(f"PASS local links: {links()} targets")
        evidence()
        extended_evidence()
        print("PASS native evidence digests")


if __name__ == "__main__":
    main()
