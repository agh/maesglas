# Publishing

The owner publishes version `2026.10.0` with tag `v2026.10.0`. Preparing the
changelog, workflows, or archive does not create a release or change GitHub.

## Release

Run `scripts/gate.sh` on the exact revision being published. Review
`CHANGELOG.md`, `docs/ports.md`, the specimen page, and the generated
`site/maesglas.zip`. The archive includes `INSTALL.md`, typography, licenses,
and both variants of every shipped port.

After approval, the owner commits with a signature and their DCO sign-off,
creates the signed `v2026.10.0` tag, and pushes. Create the GitHub release from
that tag using the prepared installer-facing notes, and attach
`site/maesglas.zip` with its SHA-256. Tags never move.

The upstream identity release pin and the private vulnerability-reporting
channel still need the owner's review before publication. Neither is enabled or
invented by the release preparation.

## GitHub Pages

In the repository's Pages settings, the owner selects **GitHub Actions** as the
publishing source. The workflow does not enable Pages automatically. The
`github-pages` environment must allow deployment from `main` and the approved
`v*` tags.

`.github/workflows/pages.yml` runs on pushes to `main` and `v*` tags. It calls
the reusable gate, packages the checked-in `site/` only after the gate passes,
and deploys that artifact. Only the deployment job can write Pages or request an
identity token; the gate cannot publish.

The project URL is <https://agh.github.io/maesglas/>. Assets, specimens,
downloads, and guidance use project-relative URLs. The browser gate serves the
site under `/maesglas/` and rejects requests escaping that path.

After deployment, check both variants, the font link, the ports archive, and the
[privacy notice](privacy.md) at that URL. Deployment itself requires the owner's
push and repository settings; a local gate cannot certify GitHub's deployment
service.

## Linux CI

Mutable documentation for a rejected format remains dated historical evidence,
not a required download. The corresponding native registry and contrast proof
are still checked; a documentation-site edit cannot break unrelated ports.

The browser gate checks the site's own URL through its local project-path
server, not by contacting a deployment that does not exist yet. The link gate
reports the two future changelog URLs as pending until `v2026.10.0` exists on
the public remote. After the owner pushes the tag, those links receive the
normal live check; other external links are never exempted by this rule.

The gate uses the multi-architecture Python image index in `tools.lock`. Linux
AMD64 and ARM64 release artifacts have separate digest pins; bootstrap selects
the current architecture and fails on unsupported targets. Go probes use
explicit `GOOS` and `GOARCH`, with no inherited cross-compilation target.

Node.js 24 LTS is pinned with its bundled npm. Node.js 26.12.0 leaves the pinned
browser installer's ZIP extraction promise unresolved after its first entry; the
same archive passes its CRC check and extracts with Node.js 24. This failure was
reproduced natively as well as under AMD64 emulation.

An emulated clean-checkout reproduction and its transcript belong in the ignored
`.cache/ci-amd64/` directory, not in the published site.
