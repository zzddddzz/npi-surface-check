from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class SurfaceFinding:
    level: str
    title: str
    detail: str


def display_name(record: dict[str, Any]) -> str:
    basic = record.get("basic") or {}
    if record.get("enumeration_type") == "NPI-2":
        return str(basic.get("organization_name") or "Unknown organization")
    parts = [
        basic.get("first_name"),
        basic.get("middle_name"),
        basic.get("last_name"),
        basic.get("credential"),
    ]
    return " ".join(str(part) for part in parts if part).strip() or "Unknown provider"


def format_address(address: dict[str, Any]) -> str:
    lines = [
        address.get("address_1"),
        address.get("address_2"),
        " ".join(
            str(part)
            for part in [address.get("city"), address.get("state"), format_postal_code(address)]
            if part
        ),
        address.get("country_name"),
    ]
    return ", ".join(str(line) for line in lines if line)


def format_postal_code(address: dict[str, Any]) -> str:
    postal_code = str(address.get("postal_code") or "")
    digits = "".join(character for character in postal_code if character.isdigit())
    country_code = str(address.get("country_code") or "").upper()
    country_name = str(address.get("country_name") or "").upper()
    is_us_address = country_code in {"", "US"} and (not country_name or country_name == "UNITED STATES")

    if is_us_address and len(digits) == 9:
        return f"{digits[:5]}-{digits[5:]}"
    return postal_code


def primary_taxonomy(record: dict[str, Any]) -> str:
    taxonomies = record.get("taxonomies") or []
    if not taxonomies:
        return "No taxonomy listed"
    primary = next((item for item in taxonomies if item.get("primary") is True), taxonomies[0])
    code = primary.get("code") or "unknown"
    desc = primary.get("desc") or "Unknown taxonomy"
    return f"{desc} ({code})"


def analyze_record(record: dict[str, Any], today: date | None = None) -> list[SurfaceFinding]:
    today = today or date.today()
    basic = record.get("basic") or {}
    findings: list[SurfaceFinding] = []

    if basic.get("status") != "A":
        findings.append(
            SurfaceFinding(
                "review",
                "NPI status is not active",
                f"NPPES status is {basic.get('status') or 'missing'}.",
            )
        )

    last_updated = _parse_date(str(basic.get("last_updated") or ""))
    if last_updated:
        age_days = (today - last_updated).days
        if age_days > 365 * 3:
            findings.append(
                SurfaceFinding(
                    "review",
                    "Profile has not been updated recently",
                    f"NPPES last_updated is {last_updated.isoformat()} ({age_days // 365} years ago).",
                )
            )
    else:
        findings.append(SurfaceFinding("review", "Missing last-updated date", "NPPES did not return last_updated."))

    addresses = record.get("addresses") or []
    for address in addresses:
        purpose = address.get("address_purpose") or "ADDRESS"
        if record.get("enumeration_type") == "NPI-1" and purpose == "MAILING":
            findings.append(
                SurfaceFinding(
                    "review",
                    "Mailing address is public",
                    f"Review whether this public mailing address is appropriate: {format_address(address)}",
                )
            )
        if address.get("telephone_number"):
            findings.append(
                SurfaceFinding(
                    "info",
                    f"{purpose.title()} phone is public",
                    str(address["telephone_number"]),
                )
            )

    endpoints = record.get("endpoints") or []
    if not endpoints:
        findings.append(
            SurfaceFinding(
                "info",
                "No endpoint entries returned",
                "The NPPES API response did not include digital contact endpoints for this record.",
            )
        )

    if not record.get("taxonomies"):
        findings.append(SurfaceFinding("review", "No taxonomy listed", "NPPES did not return taxonomy records."))

    return findings


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
