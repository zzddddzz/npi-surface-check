from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi


API_URL = "https://npiregistry.cms.hhs.gov/api/"


class NppesError(RuntimeError):
    """Raised when the NPPES API cannot be queried or parsed."""


@dataclass(frozen=True)
class NppesQuery:
    number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    organization_name: str | None = None
    state: str | None = None
    city: str | None = None
    limit: int = 10

    def params(self) -> dict[str, str]:
        params: dict[str, str] = {"version": "2.1", "limit": str(self.limit)}
        optional = {
            "number": self.number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "organization_name": self.organization_name,
            "state": self.state,
            "city": self.city,
        }
        params.update({key: value for key, value in optional.items() if value})
        return params


def fetch_nppes(query: NppesQuery, timeout: float = 20.0) -> dict[str, Any]:
    url = f"{API_URL}?{urlencode(query.params())}"
    request = Request(url, headers={"User-Agent": "npi-surface-check/0.1"})
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(request, timeout=timeout, context=context) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise NppesError(f"NPPES API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise NppesError(f"NPPES API request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise NppesError("NPPES API request timed out") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise NppesError("NPPES API returned invalid JSON") from exc

    if not isinstance(data, dict):
        raise NppesError("NPPES API returned an unexpected payload")
    return data
