#!/usr/bin/env python3
"""
Add Apache 2.0 license headers to Python source files.
"""

import os
from pathlib import Path

# Apache 2.0 license header for Python files
LICENSE_HEADER = '''#
# Copyright 2026 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
'''

def has_license_header(file_path: Path) -> bool:
    """Check if file already has a license header."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = ''.join([f.readline() for _ in range(15)])
            return 'Licensed under the Apache License' in first_lines or 'Copyright 2025' in first_lines
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def add_license_header(file_path: Path) -> bool:
    """Add license header to a Python file."""
    try:
        # Read existing content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if already has license
        if 'Licensed under the Apache License' in content[:1000]:
            print(f"  Skipping {file_path.relative_to(file_path.parents[2])} (already licensed)")
            return False

        # Check if file starts with shebang
        shebang = None
        if content.startswith('#!'):
            lines = content.split('\n', 1)
            shebang = lines[0] + '\n'
            content = lines[1] if len(lines) > 1 else ''

        # Check for encoding declaration
        encoding = None
        if content.startswith('# -*- coding:') or content.startswith('# coding:'):
            lines = content.split('\n', 1)
            encoding = lines[0] + '\n'
            content = lines[1] if len(lines) > 1 else ''

        # Add empty line after header for docstrings that follow
        new_content = LICENSE_HEADER + '\n' + content

        # Re-add shebang and encoding if they existed
        if encoding:
            new_content = shebang + encoding + new_content[len(shebang):] if shebang else encoding + new_content
        elif shebang:
            new_content = shebang + new_content

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  Added header to {file_path.relative_to(file_path.parents[2])}")
        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add license headers to all Python files in generic_framework."""
    base_path = Path('/home/peter/development/eeframe/generic_framework')

    if not base_path.exists():
        print(f"Path not found: {base_path}")
        return

    # Find all Python files
    py_files = list(base_path.rglob('*.py'))

    print(f"Found {len(py_files)} Python files")
    print(f"Adding Apache 2.0 license headers...\n")

    added = 0
    skipped = 0

    for py_file in py_files:
        if add_license_header(py_file):
            added += 1
        else:
            skipped += 1

    print(f"\nDone!")
    print(f"  Added: {added}")
    print(f"  Skipped: {skipped}")
    print(f"  Total: {len(py_files)}")

if __name__ == '__main__':
    main()
