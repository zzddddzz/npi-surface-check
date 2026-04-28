from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import Any, Sequence

from .nppes import NppesError, NppesQuery, fetch_nppes
from .surface import analyze_record, display_name, format_address, primary_taxonomy


CSV_FIELDS = [
    "npi",
    "name",
    "enumeration_type",
    "status",
    "last_updated",
    "primary_taxonomy",
    "review_note_count",
]


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    query = NppesQuery(
        number=args.npi,
        first_name=args.first_name,
        last_name=args.last_name,
        organization_name=args.organization,
        state=args.state,
        city=args.city,
        limit=args.limit,
        taxonomy_description=args.taxonomy_description,
    )

    if not any([query.number, query.last_name, query.organization_name, query.taxonomy_description]):
        parser.error("provide --npi, --last-name, --organization, or --taxonomy-description")

    try:
        payload = fetch_nppes(query)
    except NppesError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = build_report(payload)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.csv:
        print_csv_report(report)
    else:
        print_human_report(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="npi-surface-check",
        description="Show what an NPI profile exposes in public NPPES data.",
    )
    parser.add_argument("--npi", help="10-digit NPI number")
    parser.add_argument("--first-name", help="individual provider first name")
    parser.add_argument("--last-name", help="individual provider last name")
    parser.add_argument("--organization", help="organization name")
    parser.add_argument("--state", help="2-letter state filter")
    parser.add_argument("--city", help="city filter")
    parser.add_argument("--limit", type=int, default=5, help="maximum records to return")
    parser.add_argument("--taxonomy-description", help="taxonomy description filter")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    output_group.add_argument("--csv", action="store_true", help="emit spreadsheet-friendly CSV")
    return parser


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload.get("results") or []
    report_records = []
    for record in records:
        findings = analyze_record(record)
        report_records.append(
            {
                "npi": record.get("number"),
                "enumeration_type": record.get("enumeration_type"),
                "name": display_name(record),
                "status": (record.get("basic") or {}).get("status"),
                "last_updated": (record.get("basic") or {}).get("last_updated"),
                "primary_taxonomy": primary_taxonomy(record),
                "addresses": [
                    {
                        "purpose": address.get("address_purpose"),
                        "address": format_address(address),
                        "telephone_number": address.get("telephone_number"),
                    }
                    for address in (record.get("addresses") or [])
                ],
                "endpoints_count": len(record.get("endpoints") or []),
                "findings": [finding.__dict__ for finding in findings],
            }
        )
    return {"result_count": payload.get("result_count", len(records)), "records": report_records}


def print_human_report(report: dict[str, Any]) -> None:
    print(f"Results: {report['result_count']}")
    if not report["records"]:
        print("No NPPES records matched the query.")
        return

    for index, record in enumerate(report["records"], start=1):
        print()
        print(f"{index}. {record['name']} ({record['npi']})")
        print(f"   Type: {record['enumeration_type']}  Status: {record.get('status') or 'unknown'}")
        print(f"   Last updated: {record.get('last_updated') or 'unknown'}")
        print(f"   Primary taxonomy: {record['primary_taxonomy']}")
        if record["addresses"]:
            print("   Public addresses:")
            for address in group_addresses(record["addresses"]):
                print(f"   - {address['purpose']}: {address['address']}")
                if address.get("telephone_number"):
                    print(f"     phone: {address['telephone_number']}")
        print("   Review notes:")
        for finding in record["findings"]:
            print(f"   - {finding['level'].upper()}: {finding['title']} - {finding['detail']}")


def print_csv_report(report: dict[str, Any]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for record in report["records"]:
        writer.writerow(
            {
                "npi": record.get("npi"),
                "name": record.get("name"),
                "enumeration_type": record.get("enumeration_type"),
                "status": record.get("status"),
                "last_updated": record.get("last_updated"),
                "primary_taxonomy": record.get("primary_taxonomy"),
                "review_note_count": len(record.get("findings") or []),
            }
        )


def group_addresses(addresses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: list[dict[str, Any]] = []
    indexes: dict[tuple[str, str | None], int] = {}

    for address in addresses:
        key = (str(address.get("address") or ""), address.get("telephone_number"))
        purpose = str(address.get("purpose") or "ADDRESS")
        if key in indexes:
            existing = grouped[indexes[key]]
            existing["purpose"] = f"{existing['purpose']}, {purpose}"
            continue

        indexes[key] = len(grouped)
        grouped.append({**address, "purpose": purpose})

    return grouped
