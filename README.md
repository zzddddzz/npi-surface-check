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
