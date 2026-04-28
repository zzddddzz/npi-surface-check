# npi-surface-check

`npi-surface-check` shows what an NPI profile exposes in public NPPES data.

It is for clinicians, pharmacists, students, and small teams who want a quick way to review public-facing NPI information without logging in or storing a copy of the registry.

## What It Checks

- Public mailing and practice addresses
- Public phone numbers
- NPI type and active status
- Last-updated date
- Primary taxonomy
- Digital contact endpoints returned by the NPPES API

The tool does not decide whether a profile is correct. It points out public fields worth reviewing against official NPPES records.

## Data Source

This project uses the public NPPES NPI Registry API:

https://npiregistry.cms.hhs.gov/api-page

CMS describes NPI information as publicly accessible through the NPI Registry, API, and dissemination files:

https://www.cms.gov/priorities/burden-reduction/overview/interoperability/frequently-asked-questions/bulk-upload-reviewing-updating-digital-contact-information-national-plan-provider-enumeration-system

## Install

From a checkout:

```bash
python3 -m pip install .
```

Run without installing:

```bash
PYTHONPATH=src python3 -m npi_surface_check --organization "Mayo Clinic" --limit 1
```

## Usage

Search by NPI:

```bash
npi-surface-check --npi 1881018208
```

Search by name:

```bash
npi-surface-check --first-name Jane --last-name Smith --state CA
```

Search by organization:

```bash
npi-surface-check --organization "Mayo Clinic" --limit 3
```

Search by taxonomy description:

```bash
npi-surface-check --taxonomy-description "Internal Medicine" --state CA --limit 3
```

JSON output:

```bash
npi-surface-check --organization "Mayo Clinic" --limit 1 --json
```

CSV output:

```bash
npi-surface-check --organization "Mayo Clinic" --limit 1 --csv
```

## Examples

Organization searches return public NPPES organization fields:

```text
$ npi-surface-check --organization "Mayo Clinic" --limit 1
Results: 1

1. MAYO CLINIC (1881018208)
   Type: NPI-2  Status: A
   Last updated: 2021-04-12
   Primary taxonomy: Clinic/Center, Multi-Specialty (261QM1300X)
   Public addresses:
   - LOCATION, MAILING: 200 1ST ST SW, ROCHESTER MN 55905-0001, United States
     phone: 507-284-2511
```

Individual-provider output has the same shape. This sample uses synthetic values:

```text
Results: 1

1. ALEX R RIVERA PHARMD (0000000000)
   Type: NPI-1  Status: A
   Last updated: 2026-01-15
   Primary taxonomy: Pharmacist (183500000X)
   Public addresses:
   - MAILING: 100 MAIN ST, ANYTOWN CA 90001-0000, United States
     phone: 555-0100
```

Add `--json` for structured output or `--csv` for spreadsheet-friendly output.

## Safety Boundary

- Uses public NPPES data only.
- Does not ask for NPPES login credentials.
- Does not store queries by default.
- Does not scrape private sites.
- Does not provide legal, credentialing, privacy, or compliance advice.

Use the official NPPES website to review and update records.

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
