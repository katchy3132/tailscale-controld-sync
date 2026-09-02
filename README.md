# tailscale-controld-sync

Sync Tailscale devices and services to ControlD DNS rules.

This keeps your ControlD DNS records aligned with what exists in your Tailscale tailnet.

Use case: some clients (for example, browser profiles/containers tied to different endpoints) may not be able to use your local Tailscale DNS resolver. Publishing tailnet host/service names into ControlD makes those names resolvable even when the local resolver isn’t available.

A client-specific Control D resolver for DNS-over-HTTPS (DoH) looks like:
`https://dns.controld.com/abcd1234/name-goes-here`

See the [Control D device clients documentation](https://docs.controld.com/docs/device-clients) for details.

## Features

- Fetches Tailscale devices and services via the Tailscale API and builds DNS records from their names (supports multiple DNS suffixes and optional bare hostnames).
- Default dry-run mode. Use `--apply` to make live changes; `--debug` for verbose HTTP output; `--quiet` to suppress startup informational output.
- Creates timestamped JSON backups of existing rules before applying changes (live mode).

## Quick start

The project requires Python 3.10 or newer. The examples below use [uv](https://docs.astral.sh/uv/).

1. Install dependencies:

```powershell
uv sync
```

2. Copy the example config:

```powershell
cp config_example.py config.py
```

3. Edit `config.py` and set:

   - `TAILSCALE_API_KEY` and `TAILSCALE_TAILNET_ID`
   - `CONTROLD_API_TOKEN` and `CONTROLD_PROFILE_ID`
   - `CONTROLD_FOLDER_NAME`, `DNS_SUFFIXES`, and `CREATE_BARE_HOSTNAME`

4. Preview changes in the default dry-run mode:

```powershell
uv run sync
```

You can also run the module directly:

```powershell
python tailscale_controld_sync.py
```

5. Apply changes to Control D:

```powershell
uv run sync --apply
```

Or:

```powershell
python tailscale_controld_sync.py --apply
```

6. For scheduled tasks, suppress startup messages with `--quiet`:

```powershell
uv run sync --apply --quiet
```

Use `--debug` to log HTTP methods, URLs, timeouts, and redacted request headers. API credentials are never included in debug logs.

## Backups

When running in live mode the script saves a timestamped backup JSON file named like `controld_backup_YYYYMMDD_HHMMSS.json` before making changes.
