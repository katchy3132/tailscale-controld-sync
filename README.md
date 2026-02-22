# tailscale-controld-sync

Sync Tailscale hosts and services to ControlD DNS rules.

Keep ControlD DNS entries in sync with devices and services from a Tailscale tailnet.

## Features

- Fetches Tailscale devices and services via the Tailscale API and then builds DNS records from device/service names, supporting multiple DNS suffixes and optional bare hostnames.
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
1. Run (dry run): `uv run sync` or `python tailscale_controld_sync.py`
1. Apply changes: `uv run sync --apply` or `python tailscale_controld_sync.py --apply`
1. Apply in quiet mode (scheduled tasks): `uv run sync --apply --quiet` or `python tailscale_controld_sync.py --apply --quiet`

## Backups

When running in live mode the script saves a timestamped backup JSON file named like `controld_backup_YYYYMMDD_HHMMSS.json` before making changes.
