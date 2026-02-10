#!/usr/bin/env python3
"""
Add persona field to all domain configs based on domain_type.

Type mapping:
- Type 1 → poet
- Type 2 → librarian
- Type 3 → librarian
- Type 4 → researcher
- Type 5 → researcher
"""

import json
import glob
from pathlib import Path

# Type to persona mapping
TYPE_TO_PERSONA = {
    "1": "poet",
    "2": "librarian",
    "3": "librarian",
    "4": "researcher",
    "5": "researcher"
}


def update_domain_config(domain_path):
    """Add persona field to domain config"""
    with open(domain_path, 'r') as f:
        config = json.load(f)

    # Skip if already has persona
    if 'persona' in config:
        print(f"✓ {domain_path.name} already has persona")
        return

    # Get domain type
    domain_type = config.get('domain_type')
    if not domain_type:
        print(f"⚠ {domain_path.name} has no domain_type, skipping")
        return

    # Map to persona
    persona = TYPE_TO_PERSONA.get(str(domain_type))
    if not persona:
        print(f"⚠ {domain_path.name} has unknown type {domain_type}, defaulting to librarian")
        persona = "librarian"

    # Add persona and enable_pattern_override
    config['persona'] = persona
    config['enable_pattern_override'] = True

    # Write back
    with open(domain_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ {domain_path.name}: Type {domain_type} → persona '{persona}'")


def main():
    """Update all domain configs"""
    # Find all domain.json files
    pattern = "universes/*/domains/*/domain.json"
    domain_files = glob.glob(pattern)

    print(f"Found {len(domain_files)} domain configs\n")

    for domain_file in sorted(domain_files):
        domain_path = Path(domain_file)
        try:
            update_domain_config(domain_path)
        except Exception as e:
            print(f"✗ {domain_path.name}: ERROR - {e}")

    print(f"\n✓ Updated {len(domain_files)} domains")


if __name__ == "__main__":
    main()
