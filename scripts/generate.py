"""Render every derived artifact, or reject drift without writing."""

import argparse
import hashlib
import io
import json
import re
import zipfile

import documents
import plates
import port_renderers
from model import ROOT, load


def outputs() -> dict[str, bytes]:
    design = load()
    files = port_renderers.render(design) | plates.render(design) | documents.render(design)
    for name, content in list(files.items()):
        if name.startswith("specimens/"):
            files[f"site/{name}"] = content
    files["site/mark-16.svg"] = files["identity/mark-16.svg"]
    files["site/LICENSE.txt"] = (ROOT / "LICENSE").read_bytes()
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text().replace("site/fonts/", "fonts/")
    compact: list[str] = []
    for line in notice.splitlines():
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            cells = ["---" if re.fullmatch(r"[-:]+", cell) else cell for cell in cells]
            line = "| " + " | ".join(cells) + " |"
        compact.append(line)
    files["site/THIRD_PARTY_NOTICES.md"] = ("\n".join(compact) + "\n").encode()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, content in sorted(files.items()):
            if name.startswith("ports/"):
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 24, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                bundle.writestr(info, content)
        bundle.writestr(
            zipfile.ZipInfo("PORTS.md", (2026, 10, 24, 0, 0, 0)),
            files["docs/ports.md"],
        )
        bundle.writestr(
            zipfile.ZipInfo("INSTALL.md", (2026, 10, 24, 0, 0, 0)),
            files["docs/installation.md"]
            .decode()
            .replace("(typography.md)", "(TYPOGRAPHY.md)")
            .replace("(ports.md)", "(PORTS.md)")
            .replace("(../THIRD_PARTY_NOTICES.md)", "(THIRD_PARTY_NOTICES.md)"),
        )
        bundle.writestr(
            zipfile.ZipInfo("TYPOGRAPHY.md", (2026, 10, 24, 0, 0, 0)),
            files["docs/typography.md"]
            .decode()
            .replace("(../THIRD_PARTY_NOTICES.md)", "(THIRD_PARTY_NOTICES.md)"),
        )
        bundle.writestr(
            zipfile.ZipInfo("THIRD_PARTY_NOTICES.md", (2026, 10, 24, 0, 0, 0)),
            (ROOT / "THIRD_PARTY_NOTICES.md").read_text().replace("site/fonts/OFL.txt", "OFL.txt"),
        )
        bundle.writestr(
            zipfile.ZipInfo("OFL.txt", (2026, 10, 24, 0, 0, 0)),
            (ROOT / "site/fonts/OFL.txt").read_bytes(),
        )
        bundle.writestr(
            zipfile.ZipInfo("LICENSE", (2026, 10, 24, 0, 0, 0)), (ROOT / "LICENSE").read_bytes()
        )
    files["site/maesglas.zip"] = archive.getvalue()
    claims = [
        {"file": name, "checked": match.group(1)}
        for name, content in sorted(files.items())
        if name.endswith((".md", ".html"))
        for match in re.finditer(r"\[checked: ([^]]+)\]", content.decode())
    ]
    files["identity/claims.json"] = (json.dumps(claims, indent=2) + "\n").encode()
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}
    files["identity/generated.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = outputs()
    stale: list[str] = []
    for name, content in sorted(files.items()):
        path = ROOT / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    for directory in ("ports", "specimens"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and str(path.relative_to(ROOT)) not in files:
                stale.append(str(path.relative_to(ROOT)))
    if stale:
        raise SystemExit("Stale or orphaned generated files:\n" + "\n".join(stale))
    print(
        f"PASS generation: {len(files)} artifacts"
        if args.check
        else f"Wrote {len(files)} artifacts"
    )


if __name__ == "__main__":
    main()
