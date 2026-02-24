# tailscale-controld-sync

Sync Tailscale devices and services to ControlD DNS rules.

This keeps your ControlD DNS records aligned with what exists in your Tailscale tailnet.

Use case: some clients (for example, browser profiles/containers tied to different endpoints) may not be able to use your local Tailscale DNS resolver. Publishing tailnet host/service names into ControlD makes those names resolvable even when the local resolver isn’t available.

a Client Specific ControlD Resolver for DNS-over-HTTPS (DoH) looks like : `https://dns.controld.com/abcd1234/name-goes-here`

see more here : https://docs.controld.com/docs/device-clients

## Features

- Fetches Tailscale devices and services via the Tailscale API and builds DNS records from their names (supports multiple DNS suffixes and optional bare hostnames).
- Default dry-run mode. Use `--apply` to make live changes; `--debug` for verbose HTTP output; `--quiet` to suppress startup informational output.
- Creates timestamped JSON backups of existing rules before applying changes (live mode).

## Quick start

1. Install dependencies:

```powershell
uv sync
```

1. Copy the example config:

```powershell
cp config_example.py config.py
```

1. Edit `config.py` and set your Tailscale and ControlD credentials and settings.
2. Run (dry run): `uv run sync` or `python tailscale_controld_sync.py`
3. Apply changes: `uv run sync --apply` or `python tailscale_controld_sync.py --apply`
4. Apply in quiet mode (scheduled tasks): `uv run sync --apply --quiet` or `python tailscale_controld_sync.py --apply --quiet`

## Backups

When running in live mode the script saves a timestamped backup JSON file named like `controld_backup_YYYYMMDD_HHMMSS.json` before making changes.
