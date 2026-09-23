from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

import yaml


PLUGIN_ROOT = Path(__file__).parents[1]


def read(relative_path: str) -> str:
    return (PLUGIN_ROOT / relative_path).read_text(encoding="utf-8")


class DeclarationTests(unittest.TestCase):
    def test_manifest_declares_independent_s2_identity_and_runner(self) -> None:
        manifest = read("manifest.yaml")

        self.assertRegex(manifest, r"(?m)^version: 0\.0\.2$")
        self.assertRegex(manifest, r"(?m)^author: shengshu-ai$")
        self.assertRegex(manifest, r"(?m)^name: vidu_s2$")
        self.assertIn("- provider/vidu_s2.yaml", manifest)
        self.assertIn('version: "3.12"', manifest)
        self.assertIn("entrypoint: main", manifest)
        self.assertTrue((PLUGIN_ROOT / "_assets" / "icon.svg").is_file())

    def test_provider_declares_credentials_and_four_s2_tools(self) -> None:
        provider = read("provider/vidu_s2.yaml")

        self.assertRegex(provider, r"(?m)^  author: shengshu-ai$")
        self.assertRegex(provider, r"(?m)^  name: vidu_s2$")
        self.assertIn("  vidu_api_key:", provider)
        self.assertIn("  region:", provider)
        expected_tools = [
            "tools/create_avatar_session.yaml",
            "tools/create_editing_session.yaml",
            "tools/get_live_session.yaml",
            "tools/list_voices.yaml",
        ]
        for tool_path in expected_tools:
            self.assertIn(f"  - {tool_path}", provider)

    def test_runtime_dependency_constraints_match_pyproject(self) -> None:
        requirements = {
            line.strip()
            for line in read("requirements.txt").splitlines()
            if line.strip()
        }
        pyproject = tomllib.loads(read("pyproject.toml"))
        normalized_project = {
            dependency.replace("dify-plugin", "dify_plugin", 1)
            for dependency in pyproject["project"]["dependencies"]
        }

        self.assertEqual(requirements, normalized_project)

    def test_s2_declarations_do_not_contain_s1_identity_or_creation_route(self) -> None:
        declaration_files = [
            "manifest.yaml",
            "provider/vidu_s2.yaml",
        ]
        combined = "\n".join(read(path) for path in declaration_files)

        self.assertNotIn("vidu_s1", combined)
        self.assertNotIn("Vidu S1", combined)
        self.assertNotIn("vidu-s1-api", combined)
        self.assertIsNone(re.search(r"POST\s+/live/v1/lives", combined))

    def test_every_declared_python_source_exists(self) -> None:
        manifest = yaml.safe_load(read("manifest.yaml"))
        provider_path = manifest["plugins"]["tools"][0]
        provider = yaml.safe_load(read(provider_path))

        self.assertTrue((PLUGIN_ROOT / provider["extra"]["python"]["source"]).is_file())
        for tool_path in provider["tools"]:
            tool = yaml.safe_load(read(tool_path))
            self.assertTrue((PLUGIN_ROOT / tool["extra"]["python"]["source"]).is_file())

    def test_tool_output_contracts_match_s2_product_boundary(self) -> None:
        avatar = yaml.safe_load(read("tools/create_avatar_session.yaml"))
        editing = yaml.safe_load(read("tools/create_editing_session.yaml"))
        query = yaml.safe_load(read("tools/get_live_session.yaml"))

        self.assertEqual(
            set(avatar["output_schema"]["properties"]),
            {"live_id", "status", "live_duration", "call_mode", "rtc"},
        )
        self.assertEqual(
            set(editing["output_schema"]["properties"]),
            {
                "live_id",
                "status",
                "live_duration",
                "render_uid",
                "client_secret",
                "rtc",
            },
        )
        self.assertEqual(
            set(query["output_schema"]["properties"]),
            {
                "live_id",
                "status",
                "live_duration",
                "call_mode",
                "billed_seconds",
                "credits_cost",
                "created_at",
                "started_at",
                "ended_at",
                "trace_id",
            },
        )

    def test_publication_documents_describe_s2_package_and_sensitive_outputs(self) -> None:
        required_files = [
            "README.md",
            "readme/README_zh_Hans.md",
            "PRIVACY.md",
            "PUBLISHING.md",
        ]
        for path in required_files:
            self.assertTrue((PLUGIN_ROOT / path).is_file(), path)

        combined = "\n".join(read(path) for path in required_files)
        for required in (
            "Vidu S2",
            "https://github.com/shengshu-ai/vidu-s-api",
            "vidu_s2-0.0.2.difypkg",
            "v0.0.2",
            "shengshu-ai/vidu_s2/vidu_s2-0.0.2.difypkg",
            "rtc.token",
            "client_secret",
            "Workflow",
            "WebSocket",
        ):
            self.assertIn(required, combined)


if __name__ == "__main__":
    unittest.main()
