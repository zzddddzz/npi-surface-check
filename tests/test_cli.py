import io
from contextlib import redirect_stdout
from unittest import TestCase
from unittest.mock import patch

from npi_surface_check.cli import build_report, main


PAYLOAD = {
    "result_count": 1,
    "results": [
        {
            "number": "1881018208",
            "enumeration_type": "NPI-2",
            "basic": {
                "organization_name": "MAYO CLINIC",
                "status": "A",
                "last_updated": "2021-04-12",
            },
            "addresses": [],
            "endpoints": [],
            "taxonomies": [{"code": "261QM1300X", "desc": "Clinic/Center, Multi-Specialty", "primary": True}],
        }
    ],
}


class CliTests(TestCase):
    def test_build_report(self):
        report = build_report(PAYLOAD)
        self.assertEqual(report["result_count"], 1)
        self.assertEqual(report["records"][0]["name"], "MAYO CLINIC")
        self.assertEqual(report["records"][0]["primary_taxonomy"], "Clinic/Center, Multi-Specialty (261QM1300X)")

    @patch("npi_surface_check.cli.fetch_nppes", return_value=PAYLOAD)
    def test_main_json(self, mocked_fetch):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = main(["--organization", "Mayo Clinic", "--json"])
        self.assertEqual(result, 0)
        self.assertIn('"name": "MAYO CLINIC"', stdout.getvalue())
        mocked_fetch.assert_called_once()
