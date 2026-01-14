"""
Configuration file for Tailscale to ControlD sync script.

Copy this file to config.py and fill in your actual values.
"""

# ============================================================================
# Tailscale Configuration
# ============================================================================

# Your Tailscale API key (create at: https://login.tailscale.com/admin/settings/keys)
TAILSCALE_API_KEY = 'tskey-api-xxxxx'

# Your Tailscale tailnet ID
# Use '-' to refer to the default tailnet of the access token being used
# Or specify your tailnet: 'example.com', 'user@domain.com', or organization name
# See: https://tailscale.com/api-docs#tag/devices/get/tailnet/%7Btailnet%7D/devices
TAILSCALE_TAILNET_ID = '-'


# ============================================================================
# ControlD Configuration
# ============================================================================

# Your ControlD API token
CONTROLD_API_TOKEN = 'your-controld-token'

# Your ControlD profile ID
CONTROLD_PROFILE_ID = 'your-profile-id'

# Folder name to organize rules in ControlD
# The script will create this folder if it doesn't exist
CONTROLD_FOLDER_NAME = 'Tailscale'


# ============================================================================
# DNS Configuration
# ============================================================================

# DNS suffixes to create for each host
# Each Tailscale host will get:
#   1. (Optional) A record with just the hostname if CREATE_BARE_HOSTNAME is True
#   2. A record for each suffix below (e.g., 'server1.ts.example.com')
#
# Example: For host 'server1' with IP '100.64.0.1', this creates:
#   - server1 → 100.64.0.1 (only if CREATE_BARE_HOSTNAME = True)
#   - server1.ts.example.com → 100.64.0.1
#   - server1.vpn.example.com → 100.64.0.1

DNS_SUFFIXES = [
    'ts',
    'funny-name.ts.net'
]

# Whether to create a record with just the hostname (no suffix)
# Set to True to create records like: server1 → 100.64.0.1
# Set to False to only create records with suffixes
CREATE_BARE_HOSTNAME = False
