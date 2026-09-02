import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "tailscale_controld_sync.py"
SPEC = importlib.util.spec_from_file_location("tailscale_controld_sync", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SecurityHardeningTests(unittest.TestCase):
    def test_config_path_uses_script_directory_only(self):
        expected = MODULE_PATH.with_name("config.py")
        with patch.object(MODULE.Path, "cwd", return_value=Path("C:/untrusted")):
            self.assertEqual(MODULE.get_config_path(), expected)

    def test_http_requests_have_a_bounded_timeout(self):
        response = object()
        with patch.object(MODULE.requests, "get", return_value=response) as request:
            result = MODULE.request("get", "https://example.test", headers={"X-Test": "1"})

        self.assertIs(result, response)
        request.assert_called_once_with(
            "https://example.test", headers={"X-Test": "1"}, timeout=MODULE.REQUEST_TIMEOUT
        )

    def test_existing_rules_are_indexed_by_hostname_and_keep_rule_id(self):
        rules = [{
            "PK": "rule-123",
            "hostnames": ["server.ts", "server.vpn"],
            "action": {"via": "100.64.0.1"},
        }]

        result = MODULE.build_existing_rules_map(rules)

        self.assertEqual(result["server.ts"]["id"], "rule-123")
        self.assertEqual(result["server.vpn"]["id"], "rule-123")
        self.assertEqual(result["server.ts"]["hostnames"], ["server.ts", "server.vpn"])

    def test_existing_rules_use_pk_as_hostname_when_hostnames_are_absent(self):
        rules = [{"PK": "server.ts", "action": {"via": "100.64.0.1"}}]

        result = MODULE.build_existing_rules_map(rules)

        self.assertEqual(result["server.ts"]["id"], "server.ts")
        self.assertEqual(result["server.ts"]["hostnames"], ["server.ts"])

    def test_empty_device_addresses_are_skipped(self):
        with patch.object(MODULE, "get_tailscale_nodes", return_value=[{"name": "server.ts", "addresses": []}]), \
             patch.object(MODULE, "get_tailscale_services", return_value=[]):
            self.assertEqual(MODULE.get_tailscale_records(), {})

    def test_invalid_ip_and_hostname_are_rejected(self):
        self.assertTrue(MODULE.is_valid_ip("100.64.0.1"))
        self.assertFalse(MODULE.is_valid_ip("not-an-ip"))
        self.assertTrue(MODULE.is_valid_hostname("server.ts"))
        self.assertFalse(MODULE.is_valid_hostname("bad hostname"))

    def test_invalid_node_records_are_not_added_as_bare_hostnames(self):
        with patch.object(MODULE, "get_tailscale_nodes", return_value=[{"name": "bad hostname", "addresses": ["100.64.0.1"]}]), \
             patch.object(MODULE, "get_tailscale_services", return_value=[]), \
             patch.object(MODULE, "DNS_SUFFIXES", []), \
             patch.object(MODULE, "CREATE_BARE_HOSTNAME", True):
            self.assertEqual(MODULE.get_tailscale_records(), {})

    def test_debug_headers_redact_authorization(self):
        headers = MODULE.redact_headers({"Authorization": "Bearer secret", "Content-Type": "application/json"})

        self.assertEqual(headers["Authorization"], "[REDACTED]")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_missing_config_exits_with_failure(self):
        with patch.object(MODULE, "get_config_path", return_value=Path("C:/missing/config.py")):
            with self.assertRaises(SystemExit) as exit_context:
                MODULE.sync_dns_records()

        self.assertEqual(exit_context.exception.code, 1)

    def test_response_json_requires_an_object(self):
        response = type("Response", (), {"json": lambda self: []})()

        with self.assertRaises(ValueError):
            MODULE.response_json(response, "test endpoint")


if __name__ == "__main__":
    unittest.main()
