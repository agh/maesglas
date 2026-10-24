"""Render the generator's small Markdown dialect as accessible, local HTML."""

import html
import re


def inline(content: str, targets: dict[str, str]) -> str:
    pieces: list[str] = []
    end = 0
    pattern = r"`([^`]+)`|\[([^]]+)\]\(([^)]+)\)|<(https?://[^>]+)>"
    for match in re.finditer(pattern, content):
        pieces.append(html.escape(content[end : match.start()]))
        code, label, url, bare = match.groups()
        if code is not None:
            pieces.append(f"<code>{html.escape(code)}</code>")
        else:
            href = bare or targets.get(url, url)
            pieces.append(
                f'<a href="{html.escape(href, quote=True)}">{html.escape(bare or label)}</a>'
            )
        end = match.end()
    pieces.append(html.escape(content[end:]))
    return "".join(pieces)


def render(content: str, prefix: str, targets: dict[str, str]) -> str:
    lines = content.splitlines()
    blocks: list[str] = []
    index = 0
    heading = prefix
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line:
            continue
        if line.startswith("# "):
            continue
        if line.startswith("```"):
            code: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError("Unclosed guidance code block")
            index += 1
            blocks.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
        elif line.startswith("#"):
            match = re.fullmatch(r"(#{2,5}) (.+)", line)
            if match is None:
                raise ValueError(f"Unsupported guidance heading: {line}")
            level = len(match[1]) + 1
            heading = prefix + "-" + re.sub(r"[^a-z0-9]+", "-", match[2].lower()).strip("-")
            blocks.append(f'<h{level} id="{heading}">{inline(match[2], targets)}</h{level}>')
        elif line == "<details>" or line == "</details>":
            blocks.append(line)
        elif line.startswith("<summary>") and line.endswith("</summary>"):
            blocks.append("<summary>" + inline(line[9:-10], targets) + "</summary>")
        elif line.startswith("|"):
            rows = [line]
            while index < len(lines) and lines[index].startswith("|"):
                rows.append(lines[index])
                index += 1
            if len(rows) < 2 or not re.fullmatch(r"[\s|:-]+", rows[1]):
                raise ValueError("Guidance table needs a header and separator")
            blocks.append(
                f'<div class="table-scroll" tabindex="0" role="region" '
                f'aria-labelledby="{heading}"><table>'
            )
            for number, row in enumerate([rows[0], *rows[2:]]):
                tag = "th" if number == 0 else "td"
                cells = row.strip("|").split("|")
                blocks.append(
                    "<tr>"
                    + "".join(
                        f"<{tag}{' scope="col"' if number == 0 else ''}>"
                        f"{inline(cell.strip(), targets)}</{tag}>"
                        for cell in cells
                    )
                    + "</tr>"
                )
            blocks.append("</table></div>")
        else:
            paragraph = [line]
            while (
                index < len(lines)
                and lines[index]
                and not lines[index].startswith(("#", "```", "<details", "</details", "|"))
            ):
                paragraph.append(lines[index])
                index += 1
            blocks.append("<p>" + inline(" ".join(paragraph), targets) + "</p>")
    return "\n".join(blocks)
