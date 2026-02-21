#!/usr/bin/env python3
"""
Sync Tailscale nodes to ControlD DNS records.
This script fetches all Tailscale nodes and creates/updates DNS records in ControlD.
"""

import requests
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict
 
# Import configuration
try:
    from config import (
        TAILSCALE_API_KEY,
        TAILSCALE_TAILNET_ID,
        CONTROLD_API_TOKEN,
        CONTROLD_PROFILE_ID,
        CONTROLD_FOLDER_NAME,
        DNS_SUFFIXES,
        CREATE_BARE_HOSTNAME
    )
except ImportError:
    print("Error: config.py not found!")
    print("\nPlease create a config.py file with your configuration.")
    print("You can copy config.example.py and rename it to config.py")
    sys.exit(1)

# API endpoints
TAILSCALE_API_BASE = 'https://api.tailscale.com/api/v2'
CONTROLD_API_BASE = 'https://api.controld.com'


def validate_config():
    """Validate that all required configuration is set."""
    required_vars = {
        'TAILSCALE_API_KEY': TAILSCALE_API_KEY,
        'TAILSCALE_TAILNET_ID': TAILSCALE_TAILNET_ID,
        'CONTROLD_API_TOKEN': CONTROLD_API_TOKEN,
        'CONTROLD_PROFILE_ID': CONTROLD_PROFILE_ID,
    }
    
    missing = []
    for name, value in required_vars.items():
        if not value or value.startswith('your-') or value.startswith('tskey-api-xxxxx'):
            missing.append(name)
    
    if missing:
        print(f"Error: Please configure the following variables at the top of the script:")
        for var in missing:
            print(f"  - {var}")
        sys.exit(1)


def get_tailscale_nodes() -> List[Dict]:
    """Fetch all Tailscale nodes."""
    url = f"{TAILSCALE_API_BASE}/tailnet/{TAILSCALE_TAILNET_ID}/devices"
    headers = {'Authorization': f'Bearer {TAILSCALE_API_KEY}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        devices = response.json().get('devices', [])
        print(f"✓ Found {len(devices)} Tailscale nodes")
        return devices
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Tailscale nodes: {e}")
        sys.exit(1)


def get_tailscale_services() -> List[Dict]:
    """Fetch all Tailscale services."""
    url = f"{TAILSCALE_API_BASE}/tailnet/{TAILSCALE_TAILNET_ID}/services"
    headers = {'Authorization': f'Bearer {TAILSCALE_API_KEY}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        services = response.json().get('vipServices', [])
        print(f"✓ Found {len(services)} Tailscale services ")
        for svc in services:
            orig_name = svc.get('name', '')
            # Use the canonical name after the ':' if present, otherwise keep original
            svc['name'] = orig_name.partition(':')[2] or orig_name
            addrs = svc.get('addrs', [])
            addr = addrs[0] if addrs else ''
            # print(f"  Service: {svc.get('name')} -> {addr}")
        return services
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Tailscale services: {e}")
        sys.exit(1)


def get_tailscale_records() -> Dict[str, str]:
    """Fetch Tailscale nodes & services and build the desired DNS records map.

    Returns a dict mapping hostname -> ip.
    """
    desired_records: Dict[str, str] = {}

    # Fetch nodes and services
    tailscale_nodes = get_tailscale_nodes()
    tailscale_services = get_tailscale_services()

    # Add nodes
    for node in tailscale_nodes:
        raw_name = node.get('name', '')
        device_name = raw_name.split('.', 1)[0].lower() if raw_name else ''
        ip = node.get('addresses', [''])[0]  # Get first IP (usually IPv4)

        if not device_name or not ip:
            continue

        if CREATE_BARE_HOSTNAME:
            desired_records[device_name] = ip

        for suffix in DNS_SUFFIXES:
            suffix = suffix.strip()
            if suffix:
                fqdn = f"{device_name}.{suffix}"
                desired_records[fqdn] = ip

    # Add services
    for service in tailscale_services:
        service_name = service.get('name', '').lower()
        addrs = service.get('addrs', [])
        ip = addrs[0] if addrs else ''

        if not service_name or not ip:
            continue

        if CREATE_BARE_HOSTNAME:
            desired_records[service_name] = ip

        for suffix in DNS_SUFFIXES:
            suffix = suffix.strip()
            if suffix:
                fqdn = f"{service_name}.{suffix}"
                desired_records[fqdn] = ip

    return desired_records


def get_controld_records(folder_id: str) -> List[Dict]:
    """Fetch existing ControlD DNS records for a specific folder."""
    url = f"{CONTROLD_API_BASE}/profiles/{CONTROLD_PROFILE_ID}/rules/{folder_id}"
    headers = {'Authorization': f'Bearer {CONTROLD_API_TOKEN}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        rules = response.json().get('body', {}).get('rules', [])
        
        print(f"✓ Found {len(rules)} existing rules in ControlD '{CONTROLD_FOLDER_NAME}' folder")
        return rules
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ControlD rules: {e}")
        sys.exit(1)


def get_or_create_controld_rules_folder() -> str:
    """Get the folder ID for the Tailscale folder, creating it if necessary."""
    url = f"{CONTROLD_API_BASE}/profiles/{CONTROLD_PROFILE_ID}/groups"
    headers = {'Authorization': f'Bearer {CONTROLD_API_TOKEN}'}
    
    try:
        # Get existing folders
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        groups = response.json().get('body', {}).get('groups', [])

        # Check if folder exists. ControlD response uses 'group' for the name.
        for group in groups:
            group_name = group.get('group') or group.get('name') or ''
            if group_name and group_name.lower() == CONTROLD_FOLDER_NAME.lower():
                pk = group.get('PK')
                print(f"✓ Found existing folder: {CONTROLD_FOLDER_NAME}")
                return pk

        # Create folder if it doesn't exist
        print(f"Creating folder: {CONTROLD_FOLDER_NAME}")
        # ControlD expects 'group' when creating a folder
        response = requests.post(
            url,
            headers={**headers, 'Content-Type': 'application/json'},
            json={'group': CONTROLD_FOLDER_NAME}
        )
        response.raise_for_status()
        folder_id = response.json().get('body', {}).get('folder', {}).get('PK')
        print(f"✓ Created folder: {CONTROLD_FOLDER_NAME}")
        return folder_id
    except requests.exceptions.RequestException as e:
        print(f"Error getting/creating folder: {e}")
        sys.exit(1)


def create_controld_record(hostname: str, ip: str, folder_id: str, dry_run: bool = False) -> bool:
    """Create a DNS rule in ControlD."""
    if dry_run:
        return True
    
    url = f"{CONTROLD_API_BASE}/profiles/{CONTROLD_PROFILE_ID}/rules"
    headers = {
        'Authorization': f'Bearer {CONTROLD_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'group': folder_id,
        'status': 1,  # 1 = enabled
        'do': 2,  # 2 = SPOOF
        'via': ip,  # IP to spoof to
        'hostnames': [hostname]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"  Error creating rule {hostname}: {e}")
        return False


def update_controld_record(rule_id: str, hostname: str, ip: str, folder_id: str, dry_run: bool = False) -> bool:
    """Update an existing DNS rule in ControlD."""
    if dry_run:
        return True
    
    url = f"{CONTROLD_API_BASE}/profiles/{CONTROLD_PROFILE_ID}/rules/{rule_id}"
    headers = {
        'Authorization': f'Bearer {CONTROLD_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'group': folder_id,
        'status': 1,  # 1 = enabled
        'do': 2,  # 2 = SPOOF
        'via': ip,  # IP to spoof to
        'hostnames': [hostname]
    }
    
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"  Error updating rule {hostname}: {e}")
        return False


def delete_controld_record(rule_id: str, hostname: str, dry_run: bool = False) -> bool:
    """Delete a DNS rule from ControlD."""
    if dry_run:
        return True
    
    url = f"{CONTROLD_API_BASE}/profiles/{CONTROLD_PROFILE_ID}/rules/{rule_id}"
    headers = {'Authorization': f'Bearer {CONTROLD_API_TOKEN}'}
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"  Error deleting rule {hostname}: {e}")
        return False


def create_backup(existing_rules: List[Dict], folder_id: str):
    """Create a timestamped backup of existing rules."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"controld_backup_{timestamp}.json"
    
    backup_data = {
        'timestamp': timestamp,
        'profile_id': CONTROLD_PROFILE_ID,
        'folder_id': folder_id,
        'folder_name': CONTROLD_FOLDER_NAME,
        'rules': existing_rules
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        print(f"✓ Backup created: {filename}\n")
        return filename
    except Exception as e:
        print(f"Warning: Could not create backup: {e}\n")
        return None


def sync_dns_records(dry_run: bool = True):
    """Main sync function."""
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"Starting Tailscale → ControlD DNS sync ({mode})...\n")
    
    if dry_run:
        print("ℹ️  Running in DRY RUN mode - no changes will be made")
        print("   Use --apply to actually apply changes\n")
    
    # Validate configuration
    validate_config()

    
    # Get or create folder
    folder_id = get_or_create_controld_rules_folder()
    
    # Build desired DNS records from Tailscale nodes and services
    desired_records = get_tailscale_records()
    
    # Get existing ControlD rules in our folder
    existing_rules = get_controld_records(folder_id)
    for rule in existing_rules:
        print(f"  Existing rule: {rule.get('PK')} -> {rule.get('action', {}).get('via', '')}")
        
        
    # Create backup before making changes (only in live mode)
    if not dry_run and existing_rules:
        create_backup(existing_rules, folder_id)
      
    print(f"\n✓ Generated {len(desired_records)} desired DNS records")
    # for hostname, ip in desired_records.items():
    #     print(f"  • {hostname} → {ip}")
    
    # Build map of existing rules in our folder
    existing_map = {}
    for rule in existing_rules:
        # Extract hostname from hostnames array
        hostname = rule.get('PK')
        if not hostname:
            continue
        
        # Extract IP from via field
        ip = rule.get('action', {}).get('via', '')
        
        existing_map[hostname] = {
            'id': hostname,
            'ip': ip
        }
    
    # Sync records
    created = 0
    updated = 0
    deleted = 0
    
    print("\nSyncing records...")
    
    # Create or update records
    for hostname, ip in desired_records.items():
        if hostname in existing_map:
            existing_rule = existing_map[hostname]
            if existing_rule['ip'] != ip:
                if update_controld_record(existing_rule['id'], hostname, ip, folder_id, dry_run):
                    print(f"  ↻ Updated: {hostname} → {ip}")
                    updated += 1
            else:
                print(f"  ✓ Unchanged: {hostname}")
        else:
            if create_controld_record(hostname, ip, folder_id, dry_run):
                print(f"  + Created: {hostname} → {ip}")
                created += 1
    
    # Delete rules that are no longer in Tailscale
    for hostname, rule_info in existing_map.items():
        if hostname not in desired_records:
            if delete_controld_record(rule_info['id'], hostname, dry_run):
                print(f"  - Deleted: {hostname}")
                deleted += 1
    
    print(f"\n{'='*50}")
    if dry_run:
        print(f"DRY RUN Summary (no changes made):")
    else:
        print(f"Sync complete!")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Deleted: {deleted}")
    print(f"{'='*50}")
    
    if dry_run and (created > 0 or updated > 0 or deleted > 0):
        print("\nTo apply these changes, run with --apply flag")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sync Tailscale nodes to ControlD DNS rules',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python sync_tailscale_controld.py           # Dry run (preview changes)
  python sync_tailscale_controld.py --apply   # Apply changes to ControlD
        '''
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes to ControlD (default is dry run)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output for HTTP requests'
    )
    
    args = parser.parse_args()
    sync_dns_records(dry_run=not args.apply)
