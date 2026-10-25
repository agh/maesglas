# Contributing

Open an issue with a reproducible example. External pull requests are closed
with a pointer to the issue forms; the maintainer makes changes. Support is best
effort for the latest release, without a response schedule or service level.
There is no bounty.

For a palette defect, identify the variant, foreground role, background,
application version, and the smallest input that shows the problem. Use
synthetic data. Reports must not include personal paths or private
configuration.

## Development

Edit `identity/maesglas.json` for color and geometry changes. Edit the renderers
for port mappings. Do not edit files listed in `identity/generated.json`
directly.

```sh
uv sync --locked
npm ci --ignore-scripts --no-audit --no-fund
python3 scripts/generate.py
scripts/gate.sh
```

The development checks are pinned in `tools.lock`, `uv.lock`, and
`package-lock.json`. The generator itself needs only the standard library. Font
maintenance additionally uses the pinned outline extractor.

After changing specimen text or font features, rebuild the shaped outline cache
with `uv run scripts/outline_face.py` before running the generator. The
extractor uses pinned HarfBuzz bindings; ordinary generation remains
dependency-free.

Serve `site/` over HTTP for a local preview; opening the file directly does not
provide its data request. Browser checks use `.cache/browsers`. Set
`PLAYWRIGHT_BROWSERS_PATH` to that directory when running the browser installer.
Keep pinned executables in `.cache/tools/bin` when shared system packages use
different versions.

After a port or validator change, run
`python3 scripts/validate_ports.py --record` on each recorded platform, then
regenerate. The [verification record](docs/verification.md) ties native results
to exact inputs.

Additional ports use `python3 scripts/bootstrap_ports.py` and
`python3 scripts/validate_extended.py --record` on macOS. The bootstrap
downloads only digest-pinned references into `.cache/` and builds the upstream
configuration probes there. It requires the pinned Go runtime, and macOS archive
extraction requires `7zz` and `bsdtar`. Linux runs the portable checks against
the recorded macOS evidence rather than attempting to execute macOS
applications.

The gate checks files before a first commit and the full history after one
exists. Native application checks use disposable configuration and cache
directories. Missing tools fail; they do not turn into successful skips. The
terminal-specific parser check runs on macOS, while portable checks also run on
Linux.

Inspect each specimen at its intrinsic size after a visual change. Check both
modes, a narrow viewport, keyboard operation, and reduced motion. A passing
color calculation is not a substitute for reading the result.

## Publishing

Only the owner publishes. Commits use Conventional Commits and must be signed.
Contributors certify the
[Developer Certificate of Origin](https://developercertificate.org/) with
`Signed-off-by: Your Name <your-email@example.com>`, using their own name and
email, not the maintainer's identity. When signing is unavailable, stop rather
than making an unsigned commit.

Before publishing, review the upstream identity pin, approve the documented
omissions, and verify the private reporting channel. Release preparation and
Pages setup are documented in [publishing](docs/publishing.md). Record the
release date in `CHANGELOG.md`.

Verify the name against a Welsh dictionary and with a Welsh speaker before
publishing a pronunciation or recording.

## Network

Generation and native port checks run locally. Development setup downloads
packages from `pypi.org`, `files.pythonhosted.org`, `registry.npmjs.org`,
`github.com`, `api.github.com`, and `release-assets.githubusercontent.com`. The
external link check contacts the public URLs present in the documents. The
design detector runs with telemetry disabled.

Additional port setup downloads from `zed.dev`, `code.claude.com`, and
`raw.githubusercontent.com`. Upstream Go probes use `proxy.golang.org` and
`sum.golang.org`; the downloaded source archives retain their own `go.sum`
dependency digests. No account or cluster credentials are used in port checks.

Browser setup downloads from `cdn.playwright.dev` and
`playwright.download.prss.microsoft.com`. Linux source builds download from
`www.kernel.org` and `www.nano-editor.org`; the operating system package manager
contacts its configured mirrors.

The specimen page makes only same-origin requests. It stores theme and shortcut
preferences in browser storage. There are no analytics or cookies. GitHub Pages
hosts the specimen page; its IP-address logging is described in the generated
[privacy notice](docs/privacy.md).
