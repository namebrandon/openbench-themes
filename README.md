# OpenBench Theme Manager

A comprehensive theming system for [OpenBench](https://github.com/AndyGrant/OpenBench), the open-source chess engine testing framework. This tool enables customization of the OpenBench web interface through JSON-based theme configurations.

## Features

- **Multiple Pre-built Themes** - Six example themes included
- **Hot-swappable Themes** - Switch themes without manually modifying source code
- **Automatic Backups** - Preserves previous themes before applying changes
- **Path Auto-detection** - Automatically locates OpenBench installation
- **Safe Rollback** - Easy restoration to any previous theme

## Available Themes

| Theme | Description | Color Scheme |
|-------|-------------|--------------|
| **Original** | Default OpenBench theme | Dark background with green accents |
| **SeaJay** | Deep ocean-inspired theme | Navy blue with light blue accents |
| **Grass** | Terminal-inspired green theme | Dark green with lime highlights |
| **Aerogel** | Light, translucent appearance | Soft blue-grey with crystalline blue |
| **Red Sands** | Desert-inspired warm colors | Terracotta with sand tones |
| **FT** | Financial Times inspired | Light background with salmon accents |

## Installation

```bash
cd /path/to/OpenBench
git clone https://github.com/namebrandon/openbench-themes.git themes_temp
mv themes_temp/apply_theme.py .
mv themes_temp/themes .
rm -rf themes_temp
```

## Usage

### Basic Commands

```bash
# List available themes
python3 apply_theme.py --list

# Apply a theme
python3 apply_theme.py --apply theme_seajay.json

# Create backup of current theme
python3 apply_theme.py --backup

# List backups
python3 apply_theme.py --list-backups

# Restore latest backup
python3 apply_theme.py --restore latest

# Restore specific backup
python3 apply_theme.py --restore backup_20250826_230011
```

### Advanced Usage

```bash
# Specify OpenBench installation path
python3 apply_theme.py --path /opt/OpenBench --apply theme_ft.json

# Apply theme without creating backup
python3 apply_theme.py --apply theme_grass.json --no-backup

# Display help information
python3 apply_theme.py --help
```
Make sure to restart nginx/apache/gnunicorn 
You may need to collectstatic with the OB manage.py

## Creating Custom Themes

### Theme File Structure

Theme files are JSON documents containing color definitions for all UI elements. Create a new theme by copying an existing file and modifying the values.

```json
{
  "name": "Theme Name",
  "description": "Brief description of the theme",
  "colors": {
    "backgrounds": {
      "color1": "#HEX",      // Main background color
      "color2": "#HEX",      // Alternating table rows
      "color3": "#HEX"       // Buttons and UI blocks
    },
    "text": {
      "color-font1": "#HEX", // Primary text color
      "color-font2": "#HEX", // Secondary text color
      "color-font3": "#HEX"  // Accent color for headers
    },
    "links": {
      "default": "#HEX"      // Hyperlink color
    },
    "ui_elements": {
      "sidebar_hover": "#HEX",     // Sidebar hover background
      "table_header_bg": "#HEX",   // Table header background
      "table_border": "#HEX",      // Table border color
      "hover_row": "#HEX",         // Table row hover color
      "popup_bg": "#HEX",          // Popup background
      "popup_border": "#HEX"       // Popup border color
    },
    "buttons": {
      "btn_blue": "#HEX",          // Primary button
      "btn_blue_hover": "#HEX",    // Primary button hover
      "btn_start": "#HEX",         // Start button
      "btn_start_hover": "#HEX",   // Start button hover
      "btn_preset": "#HEX",        // Preset button
      "btn_preset_hover": "#HEX",  // Preset button hover
      "btn_yellow": "#HEX",        // Warning button
      "btn_yellow_hover": "#HEX",  // Warning button hover
      "btn_red": "#HEX",           // Danger button
      "btn_red_hover": "#HEX"      // Danger button hover
    },
    "status": {
      "statblock_green": "#HEX",   // Success indicators
      "statblock_red": "#HEX",     // Failure indicators
      "statblock_yellow": "#HEX",  // Warning indicators
      "statblock_blue": "#HEX",    // Information blocks
      "statblock_default": "#HEX"  // Default status block
    },
    "special": {
      "redlink": "#HEX",           // Error/danger links
      "was_default_network": "#HEX" // Network status indicator
    }
  }
}
```

### Color Selection Guidelines

1. **Contrast** - Ensure adequate contrast between text and backgrounds for readability
2. **Consistency** - Use a cohesive color palette throughout the theme
3. **Status Colors** - Maintain standard green/red indicators for pass/fail states
4. **Testing** - Verify theme appearance across different pages and UI elements
5. **Naming** - Follow the `theme_name.json` naming convention

### Example: Solarized Dark Theme

```json
{
  "name": "Solarized Dark",
  "description": "Popular Solarized Dark color scheme adapted for OpenBench",
  "colors": {
    "backgrounds": {
      "color1": "#002b36",
      "color2": "#073642",
      "color3": "#586e75"
    },
    "text": {
      "color-font1": "#fdf6e3",
      "color-font2": "#93a1a1",
      "color-font3": "#b58900"
    },
    "links": {
      "default": "#268bd2"
    }
    // Additional color definitions...
  }
}
```

## Technical Details

### Implementation

The theme manager operates by:

1. Reading theme configurations from JSON files
2. Applying color replacements to CSS files in `OpenBench/static/`
3. Updating `OPENBENCH_STATIC_VERSION` in `config.py` for cache invalidation
4. Creating timestamped backups before modifications

### Directory Structure

```
OpenBench/
├── apply_theme.py              # Theme manager script
├── themes/                     # Theme configurations
│   ├── theme_original.json     # Default OpenBench theme
│   ├── theme_seajay.json       # SeaJay theme
│   ├── theme_grass.json        # Grass theme
│   ├── theme_aerogel.json      # Aerogel theme
│   ├── theme_red_sands.json    # Red Sands theme
│   └── theme_ft.json           # Financial Times theme
└── theme_backups/              # Automatic backups
    └── backup_YYYYMMDD_HHMMSS/ # Timestamped backup folders
```

### Version Management

The script implements intelligent version management:
- Preserves base version numbers (e.g., `v6`)
- Appends theme suffixes (e.g., `v6-seajay`)
- Ensures browser cache refresh without disrupting version tracking

## Requirements

- Python 3.6 or higher
- OpenBench installation (local or server)
- Write permissions for OpenBench static files
- No external Python dependencies required

## Contributing

### Submission Process

1. Fork the repository
2. Create a new theme file following the JSON structure
3. Test thoroughly on a live OpenBench installation
4. Submit a pull request with:
   - Theme JSON file named `theme_yourname.json`
   - Screenshot demonstrating the theme
   - Description of color choices and inspiration

### Development Guidelines

- Validate JSON syntax before submission
- Include all required color fields
- Document any special considerations
- Follow existing code style and conventions

## Troubleshooting

### Common Issues

**Theme not applying:**
- Verify CSS file permissions
- Check Python version compatibility
- Ensure correct OpenBench path
- Restart gnunicorn / nginx / apache
- run collect static
- remove immutable from nginx site config

**Colors not updating:**
- Clear browser cache manually / try incognito
- Verify theme JSON syntax
- Check for CSS syntax errors

**Backup restoration failing:**
- Verify backup directory exists
- Check file permissions
- Ensure backup integrity

## License

Released under the GPL-3.0 License, maintaining compatibility with OpenBench licensing.

## Acknowledgments

- OpenBench framework by [Andrew Grant](https://github.com/AndyGrant/OpenBench)
- Theme system developed for the OpenBench community
- Color schemes inspired by popular terminal themes and design systems

## Support

- **Issue Tracking**: [GitHub Issues](https://github.com/YOUR_USERNAME/openbench-themes/issues)
- **OpenBench Repository**: [Official OpenBench](https://github.com/AndyGrant/OpenBench)
- **Community Discord**: [OpenBench Discord](https://discord.gg/9MVg7fBTpM)

---

Documentation version 1.0.0 - OpenBench Theme Manager
