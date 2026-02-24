# Code Review Notes

## Scope
Reviewed `tailscale_controld_sync.py` with focus on correctness of ControlD rule reconciliation logic.

## Findings

### 1) Incorrect identity mapping for existing ControlD rules (high)
The sync logic builds `existing_map` using `rule['PK']` as both the hostname key and rule ID, then uses that value for updates/deletes.

Why this is risky:
- The API payload used for create/update stores hostnames in `hostnames`, not in `PK`.
- If `PK` is actually a rule identifier (or any value other than the hostname), lookups against desired hostnames will miss matches and trigger unnecessary creates/deletes.
- Update/delete endpoints use `rules/{rule_id}` and should receive the real rule ID, not the hostname.

Suggested fix:
- Read hostname from `rule.get('hostnames', [])[0]` (or equivalent payload location).
- Keep the actual rule ID separately (e.g., `rule.get('PK')`) for update/delete calls.
- Guard against missing/empty hostnames arrays.

### 2) Verbose existing-rule logging ignores quiet mode (low)
`sync_dns_records` prints each existing rule unconditionally, even when `--quiet` is passed.

Suggested fix:
- Wrap per-rule debug output behind `if not quiet:` (or a dedicated debug flag).

## Positive notes
- Config loading includes robust fallbacks and clear user-facing error messages.
- Dry-run behavior is implemented consistently across create/update/delete paths.
- Backup creation before live changes is a good safety feature.
