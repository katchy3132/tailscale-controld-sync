# tailscale-controld-sync

Sync Tailscale hosts and services to ControlD DNS rules.

Keep ControlD DNS entries in sync with devices and services from a Tailscale tailnet.

Features
--------

- Fetches Tailscale devices and services via the Tailscale API and then builds DNS records from device/service names, supporting multiple DNS suffixes and optional bare hostnames.
- Default dry-run mode. Use  `--apply` to make live changes; `--debug` for verbose HTTP output.
- Creates timestamped JSON backups of existing rules before applying changes (live mode).

Quick start
-----------

1. Copy the example config:

```powershell
cp config_example.py config.py
```

2. Edit `config.py` and set your Tailscale and ControlD credentials and settings.
3. Preview changes (dry run):

```powershell
python tailscale_controld_sync.py
```

4. Apply changes:

```powershell
python tailscale_controld_sync.py --apply
```

Backups
-------

When running in live mode the script saves a timestamped backup JSON file named like `controld_backup_YYYYMMDD_HHMMSS.json` before making changes.
