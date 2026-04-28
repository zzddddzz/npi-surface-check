import csv
import io
from contextlib import redirect_stdout
from unittest import TestCase
from unittest.mock import patch

from npi_surface_check.cli import build_report, group_addresses, main


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

    @patch("npi_surface_check.cli.fetch_nppes", return_value=PAYLOAD)
    def test_main_csv(self, mocked_fetch):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = main(["--organization", "Mayo Clinic", "--csv"])

        self.assertEqual(result, 0)
        rows = list(csv.DictReader(io.StringIO(stdout.getvalue())))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["npi"], "1881018208")
        self.assertEqual(rows[0]["name"], "MAYO CLINIC")
        self.assertEqual(rows[0]["primary_taxonomy"], "Clinic/Center, Multi-Specialty (261QM1300X)")
        self.assertEqual(rows[0]["review_note_count"], "2")
        mocked_fetch.assert_called_once()

    @patch("npi_surface_check.cli.fetch_nppes", return_value=PAYLOAD)
    def test_main_taxonomy(self, mocked_fetch):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = main(["--taxonomy-description", "Internal Medicine", "--state", "CA"])
        self.assertEqual(result, 0)
        called_query = mocked_fetch.call_args[0][0]
        self.assertEqual(called_query.taxonomy_description, "Internal Medicine")
        self.assertEqual(called_query.state, "CA")
        mocked_fetch.assert_called_once()

    def test_group_addresses_keeps_purposes_for_duplicate_public_address(self):
        addresses = [
            {
                "purpose": "LOCATION",
                "address": "200 1ST ST SW, ROCHESTER MN 55905-0001, United States",
                "telephone_number": "507-284-2511",
            },
            {
                "purpose": "MAILING",
                "address": "200 1ST ST SW, ROCHESTER MN 55905-0001, United States",
                "telephone_number": "507-284-2511",
            },
        ]

        grouped = group_addresses(addresses)

        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]["purpose"], "LOCATION, MAILING")
