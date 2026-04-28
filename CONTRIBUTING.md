# Contributing

Thanks for considering a contribution. Keep this project focused on public NPPES data and small, testable changes.

## Local Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
PYTHONPATH=src python -m unittest discover -s tests
```

## Rules

- Use public NPPES data only.
- Do not add credentials, private files, screenshots of private systems, or non-public data.
- Use synthetic individual-provider fixtures in tests and documentation unless a real public example is necessary.
- Keep wording careful: the tool flags fields to review, not legal or compliance conclusions.
- Add tests for parser, CLI, and finding logic changes.
