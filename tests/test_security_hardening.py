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


if __name__ == "__main__":
    unittest.main()
