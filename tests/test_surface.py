from datetime import date
from unittest import TestCase

from npi_surface_check.surface import analyze_record, display_name, format_address, primary_taxonomy


INDIVIDUAL_RECORD = {
    "number": "1234567893",
    "enumeration_type": "NPI-1",
    "basic": {
        "first_name": "ALEX",
        "middle_name": "R",
        "last_name": "RIVERA",
        "credential": "PHARMD",
        "status": "A",
        "last_updated": "2021-04-25",
    },
    "addresses": [
        {
            "address_1": "100 MAIN ST",
            "address_purpose": "MAILING",
            "city": "ANYTOWN",
            "state": "CA",
            "postal_code": "900010000",
            "country_name": "United States",
            "telephone_number": "555-0100",
        }
    ],
    "endpoints": [],
    "taxonomies": [{"code": "1041C0700X", "desc": "Social Worker, Clinical", "primary": True}],
}


class SurfaceTests(TestCase):
    def test_display_name_for_individual(self):
        self.assertEqual(display_name(INDIVIDUAL_RECORD), "ALEX R RIVERA PHARMD")

    def test_format_address(self):
        self.assertEqual(
            format_address(INDIVIDUAL_RECORD["addresses"][0]),
            "100 MAIN ST, ANYTOWN CA 900010000, United States",
        )

    def test_primary_taxonomy(self):
        self.assertEqual(primary_taxonomy(INDIVIDUAL_RECORD), "Social Worker, Clinical (1041C0700X)")

    def test_analyze_record_flags_public_mailing_and_stale_update(self):
        findings = analyze_record(INDIVIDUAL_RECORD, today=date(2026, 4, 28))
        titles = {finding.title for finding in findings}
        self.assertIn("Mailing address is public", titles)
        self.assertIn("Profile has not been updated recently", titles)
        self.assertIn("No endpoint entries returned", titles)
