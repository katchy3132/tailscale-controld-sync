# Changelog

## 0.1.7 - 2026-09-02

### Security

- Added bounded HTTP request timeouts.
- Added redacted `--debug` HTTP logging.
- Restricted configuration loading to the script directory.
- Added hostname and IP validation before records are applied.
- Added API response-shape validation and required folder-ID checks.
- Updated `requests` to `2.34.2`, `urllib3` to `2.7.0`, and `idna` to `3.15`.
- Raised the minimum supported Python version to 3.10.

### Fixed

- Corrected Control D rule reconciliation for `PK`-based hostnames.
- Preserved existing hostnames when updating rules.
- Safely skipped Tailscale devices without addresses.
- Preserved a nonzero exit status when `config.py` is missing.

### Tests

- Added regression coverage for reconciliation, validation, configuration loading, API responses, and redacted logging.

### Documentation

- Restored detailed setup, dry-run, apply, quiet-mode, and direct Python instructions.
- Documented configuration fields, Python requirements, debug logging, and Control D DoH usage.
