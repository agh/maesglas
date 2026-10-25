"""Release, architecture, and least-privilege publishing invariants."""

import re
import unittest
from unittest.mock import patch

from bootstrap_ports import target
from generate import outputs
from model import ROOT, load_json, mapping, sequence, text


class PublicationTests(unittest.TestCase):
    def test_browser_installer_uses_the_verified_lts_runtime(self) -> None:
        lock = load_json(ROOT / "tools.lock")
        self.assertEqual(lock["node"], "24.22.1")
        self.assertEqual(lock["npm"], "11.19.1")

    def test_mutable_rejection_docs_are_not_a_ci_dependency(self) -> None:
        lock = load_json(ROOT / "tools.lock")
        self.assertNotIn("upstream/claude-terminal.md", mapping(lock["port_sources"]))
        reference = mapping(mapping(lock["historical_references"])["claude-code-documentation"])
        self.assertRegex(text(reference["sha256"]), r"^[0-9a-f]{64}$")

    def test_python_container_uses_the_index_everywhere(self) -> None:
        image = text(load_json(ROOT / "tools.lock")["linux_image"])
        self.assertIn(
            "@sha256:ec1b01f92099324b965a51c8547d9a3b71fedc99f6991a89662e7358f9b167c9",
            image,
        )
        self.assertIn(image, (ROOT / ".github/workflows/gate.yml").read_text())

    def test_native_targets_do_not_inherit_the_host_architecture(self) -> None:
        for system, machine, expected in (
            ("Linux", "x86_64", ("linux", "amd64")),
            ("Linux", "aarch64", ("linux", "arm64")),
            ("Darwin", "arm64", ("darwin", "arm64")),
        ):
            with (
                patch("bootstrap_ports.platform.system", return_value=system),
                patch("bootstrap_ports.platform.machine", return_value=machine),
            ):
                self.assertEqual(target(), expected)
        with (
            patch("bootstrap_ports.platform.machine", return_value="unsupported"),
            self.assertRaisesRegex(ValueError, "Unsupported"),
        ):
            target()

    def test_linux_artifact_pins_cover_both_architectures(self) -> None:
        lock = load_json(ROOT / "tools.lock")
        binaries = mapping(lock["linux_binaries"])
        self.assertEqual(len(binaries), 26)
        for value in binaries.values():
            record = mapping(value)
            self.assertRegex(text(record["sha256"]), r"^[0-9a-f]{64}$")
        sources = mapping(lock["port_sources"])
        for arch in ("amd64", "arm64"):
            for name in (
                f"downloads/k9s_Linux_{arch}.tar.gz",
                f"downloads/gh-dash_v4.26.0_linux-{arch}",
            ):
                record = mapping(sources[name])
                self.assertEqual(sequence(record["platforms"]), [f"linux-{arch}"])
                self.assertRegex(text(record["sha256"]), r"^[0-9a-f]{64}$")

    def test_actions_are_pinned_and_deployment_needs_the_gate(self) -> None:
        for workflow in (ROOT / ".github/workflows").glob("*.yml"):
            for use in re.findall(r"\buses: ([^\s]+)", workflow.read_text()):
                if not use.startswith("./"):
                    self.assertRegex(use, r"^[\w/-]+@[0-9a-f]{40}$")
        pages = (ROOT / ".github/workflows/pages.yml").read_text()
        self.assertIn("needs: gate", pages)
        self.assertIn("needs: package", pages)
        self.assertIn("uses: ./.github/workflows/gate.yml", pages)
        self.assertIn("enablement: false", pages)
        before_deploy, deploy = pages.split("  deploy:", 1)
        self.assertNotIn("pages: write", before_deploy)
        self.assertNotIn("id-token: write", before_deploy)
        self.assertIn("pages: write", deploy)
        self.assertIn("id-token: write", deploy)

    def test_privacy_is_generated_with_the_site(self) -> None:
        files = outputs()
        self.assertEqual(files["docs/privacy.md"], files["site/privacy.md"])
        notice = files["docs/privacy.md"].decode()
        self.assertIn("sets no cookies", notice)
        self.assertIn("uses no analytics", notice)
        self.assertIn("IP addresses", notice)
        self.assertIn("whether or not they are signed in", notice)
        self.assertIn(b'id="privacy"', files["site/index.html"])


if __name__ == "__main__":
    unittest.main()
