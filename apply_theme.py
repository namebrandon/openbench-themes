#!/usr/bin/env python3
"""
OpenBench Theme Manager
Apply custom color themes to OpenBench installation
"""

import json
import os
import sys
import argparse
import shutil
import re
from datetime import datetime
from pathlib import Path


class ThemeManager:
    def __init__(self, openbench_root=None):
        """Initialize theme manager with OpenBench root directory."""
        self.openbench_root = self._find_openbench_root(openbench_root)
        self.static_dir = os.path.join(self.openbench_root, 'OpenBench', 'static')
        self.themes_dir = os.path.join(self.openbench_root, 'themes')
        self.backup_dir = os.path.join(self.openbench_root, 'theme_backups')
        
        # Ensure directories exist
        os.makedirs(self.themes_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        print(f"OpenBench root: {self.openbench_root}")
        print(f"Static files: {self.static_dir}")
        print(f"Themes directory: {self.themes_dir}")
    
    def _find_openbench_root(self, provided_path=None):
        """Find OpenBench root directory."""
        if provided_path and os.path.exists(provided_path):
            return provided_path
        
        # Try common locations
        possible_paths = [
            os.getcwd(),  # Current directory
            os.path.dirname(os.path.abspath(__file__)),  # Script directory
            '/home/brandon/OpenBench',
            '/opt/OpenBench',
            '/var/www/OpenBench',
        ]
        
        # Look for OpenBench markers (manage.py, OpenBench/static, etc.)
        for path in possible_paths:
            if self._is_openbench_root(path):
                return path
        
        # If not found, ask user
        raise ValueError(
            "Could not find OpenBench root directory. "
            "Please provide it using --path argument."
        )
    
    def _is_openbench_root(self, path):
        """Check if path is OpenBench root directory."""
        markers = [
            'manage.py',
            os.path.join('OpenBench', 'static', 'style.css'),
            os.path.join('Templates', 'OpenBench'),
        ]
        return all(os.path.exists(os.path.join(path, marker)) for marker in markers)
    
    def list_themes(self):
        """List available themes."""
        print("\nAvailable themes:")
        theme_files = Path(self.themes_dir).glob('theme_*.json')
        
        for theme_file in sorted(theme_files):
            try:
                with open(theme_file, 'r') as f:
                    theme = json.load(f)
                    name = theme.get('name', 'Unnamed')
                    desc = theme.get('description', 'No description')
                    filename = theme_file.name
                    print(f"  - {filename}: {name}")
                    print(f"    {desc}")
            except Exception as e:
                print(f"  - {theme_file.name}: Error reading theme ({e})")
    
    def backup_current(self):
        """Backup current CSS files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'backup_{timestamp}')
        os.makedirs(backup_path, exist_ok=True)
        
        css_files = ['style.css', 'form.css', 'paging.css', 'base.css']
        
        for css_file in css_files:
            src = os.path.join(self.static_dir, css_file)
            if os.path.exists(src):
                dst = os.path.join(backup_path, css_file)
                shutil.copy2(src, dst)
                print(f"  Backed up {css_file}")
        
        print(f"Backup created: {backup_path}")
        return backup_path
    
    def apply_theme(self, theme_file):
        """Apply a theme from JSON file."""
        theme_path = os.path.join(self.themes_dir, theme_file)
        
        if not os.path.exists(theme_path):
            # Try without themes directory
            if os.path.exists(theme_file):
                theme_path = theme_file
            else:
                raise FileNotFoundError(f"Theme file not found: {theme_file}")
        
        print(f"\nApplying theme from: {theme_path}")
        
        with open(theme_path, 'r') as f:
            theme = json.load(f)
        
        # Extract theme name for version suffix
        theme_name = os.path.basename(theme_file).replace('theme_', '').replace('.json', '')
        
        # Read current style.css
        style_css_path = os.path.join(self.static_dir, 'style.css')
        with open(style_css_path, 'r') as f:
            style_content = f.read()
        
        # Apply color replacements
        replacements = []
        
        # CSS Variables
        for var_name, color in theme['colors']['backgrounds'].items():
            pattern = f'--{var_name}:\\s*#[0-9A-Fa-f]{{6}}'
            replacement = f'--{var_name}: {color}'
            replacements.append((pattern, replacement))
        
        for var_name, color in theme['colors']['text'].items():
            pattern = f'--{var_name}:\\s*#[0-9A-Fa-f]{{6}}'
            replacement = f'--{var_name}: {color}'
            replacements.append((pattern, replacement))
        
        # Direct color replacements
        ui = theme['colors']['ui_elements']
        
        # Fix link colors (match the a: pseudo-class block)
        replacements.append(
            (r'(a:link, a:visited, a:hover, a:active\s*\{[^}]*color:\s*)#[0-9A-Fa-f]{6}', 
             f'\\1{theme["colors"]["links"]["default"]}')
        )
        
        replacements.extend([
            # Sidebar hover
            (r'(#sidebar li:hover\s*\{[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["sidebar_hover"]}'),
            # Table headers - multiple patterns to catch them all
            (r'(\.stripes th\s*\{[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["table_header_bg"]}'),
            (r'(\.table-header th\s*\{[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["table_header_bg"]}'),
            (r'(\.table-small-header th\s*\{[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["table_header_bg"]}'),
            (r'(\.table-spacer-small th[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["table_header_bg"]}'),
            # Table borders
            (r'(#content td\s*\{[^}]*border-bottom:[^;]*?)#[0-9A-Fa-f]{6}', f'\\1{ui["table_border"]}'),
            # Hover rows - need to match both odd and even
            (r'(\.hoverable tr:nth-child\(odd\):hover[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["hover_row"]}'),
            (r'(\.hoverable tr:nth-child\(even\):hover[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["hover_row"]}'),
            # Engine options popup
            (r'(\.engine-options-popup\s*\{[^}]*background-color:\s*)#[0-9A-Fa-f]{6}', f'\\1{ui["popup_bg"]}'),
            (r'(\.engine-options-popup\s*\{[^}]*border:[^;]*?)#[0-9A-Fa-f]{6}', f'\\1{ui["popup_border"]}'),
        ])
        
        # Button colors
        buttons = theme['colors']['buttons']
        for btn_class, color_key in [
            ('btn-blue', 'btn_blue'),
            ('btn-start', 'btn_start'),
            ('btn-preset', 'btn_preset'),
            ('btn-yellow', 'btn_yellow'),
            ('btn-red', 'btn_red'),
        ]:
            pattern = f'(\\.{btn_class}\\s*{{[^}}]*background-color:\\s*)#[0-9A-Fa-f]{{6}}'
            replacement = f'\\1{buttons[color_key]}'
            replacements.append((pattern, replacement))
            
            # Hover states
            pattern = f'(\\.{btn_class}:hover\\s*{{[^}}]*background-color:\\s*)#[0-9A-Fa-f]{{6}}'
            replacement = f'\\1{buttons[color_key + "_hover"]}'
            replacements.append((pattern, replacement))
        
        # Apply replacements
        modified_content = style_content
        for pattern, replacement in replacements:
            modified_content = re.sub(pattern, replacement, modified_content)
        
        # Write modified CSS
        with open(style_css_path, 'w') as f:
            f.write(modified_content)
        
        print(f"✓ Theme applied: {theme.get('name', 'Unknown')}")
        
        # Update static version if config.py exists
        self._update_static_version(theme_name)
    
    def _update_static_version(self, theme_name):
        """Update static version with theme suffix to force browser refresh."""
        config_path = os.path.join(self.openbench_root, 'OpenBench', 'config.py')
        
        if not os.path.exists(config_path):
            print("  Note: config.py not found, skipping version update")
            return
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Find current version (could be vX or vX-theme format)
        match = re.search(r"OPENBENCH_STATIC_VERSION = '([^']+)'", content)
        if match:
            old_version = match.group(1)
            
            # Extract base version number if present
            base_match = re.match(r'v(\d+)', old_version)
            if base_match:
                base_version = base_match.group(1)
            else:
                base_version = '6'  # Default if can't parse
            
            # Create new version with theme suffix
            new_version = f"v{base_version}-{theme_name}"
            
            new_content = re.sub(
                r"OPENBENCH_STATIC_VERSION = '[^']+'",
                f"OPENBENCH_STATIC_VERSION = '{new_version}'",
                content
            )
            with open(config_path, 'w') as f:
                f.write(new_content)
            print(f"  ✓ Updated static version: {old_version} → {new_version}")
        else:
            print("  Note: Could not find OPENBENCH_STATIC_VERSION in config.py")
    
    def restore_backup(self, backup_name):
        """Restore a backup."""
        if backup_name == 'latest':
            # Find latest backup
            backups = sorted(Path(self.backup_dir).iterdir(), key=os.path.getmtime)
            if not backups:
                print("No backups found!")
                return
            backup_path = backups[-1]
        else:
            backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            print(f"Backup not found: {backup_path}")
            return
        
        print(f"Restoring from: {backup_path}")
        
        css_files = ['style.css', 'form.css', 'paging.css', 'base.css']
        for css_file in css_files:
            src = os.path.join(backup_path, css_file)
            dst = os.path.join(self.static_dir, css_file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"  ✓ Restored {css_file}")
        
        self._update_static_version('restored')
        print("Restore complete!")
    
    def list_backups(self):
        """List available backups."""
        print("\nAvailable backups:")
        backups = sorted(Path(self.backup_dir).iterdir(), key=os.path.getmtime)
        
        if not backups:
            print("  No backups found")
            return
        
        for backup in backups:
            if backup.is_dir():
                timestamp = backup.name.replace('backup_', '')
                size = sum(f.stat().st_size for f in backup.glob('*.css'))
                print(f"  - {backup.name} ({size:,} bytes)")


def main():
    parser = argparse.ArgumentParser(description='OpenBench Theme Manager')
    parser.add_argument('--path', help='Path to OpenBench root directory')
    parser.add_argument('--list', action='store_true', help='List available themes')
    parser.add_argument('--list-backups', action='store_true', help='List available backups')
    parser.add_argument('--apply', help='Apply a theme (e.g., theme_navy_blue.json)')
    parser.add_argument('--backup', action='store_true', help='Create backup of current theme')
    parser.add_argument('--restore', help='Restore a backup (use "latest" for most recent)')
    parser.add_argument('--no-backup', action='store_true', help='Skip automatic backup when applying theme')
    
    args = parser.parse_args()
    
    try:
        manager = ThemeManager(args.path)
        
        if args.list:
            manager.list_themes()
        elif args.list_backups:
            manager.list_backups()
        elif args.backup:
            manager.backup_current()
        elif args.restore:
            manager.restore_backup(args.restore)
        elif args.apply:
            if not args.no_backup:
                print("Creating backup...")
                manager.backup_current()
            manager.apply_theme(args.apply)
            print("\n✅ Theme applied successfully!")
            print("Note: Restart Django server for changes to take effect")
        else:
            parser.print_help()
            print("\nExamples:")
            print("  python apply_theme.py --list")
            print("  python apply_theme.py --apply theme_navy_blue.json")
            print("  python apply_theme.py --restore latest")
            print("  python apply_theme.py --path /opt/OpenBench --apply theme_original.json")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()