# Hammercroft Site Builder

A personalized static site generation toolkit for `.hsb` files -- a custom text format combining YAML metadata (the "manifest") with HTML body content and template insertion tags.

While designed for building articles at <https://hammercroft.nekoweb.org>, the core `hcsbuilder` utility is general-purpose and can be adapted for any static site given its own set of custom templates and HSB source files.

---

## Quick Start

1. **Set up environment**: Run `./setup_env.sh` (Linux/macOS) or `setup_env.bat` (Windows)
2. **Build a page**: `./hcsbuilder.sh input.hsb`
3. **Build a directory**: `./hcsbuilder.sh ./path-to-your-hsb-files/`

Note: you may need to set execute permissions on all scripts before running them. On Linux, you can do this with `chmod +x <filename>`.

---

## File Overview

### Core Files

- **`requirements.txt`** — Python dependencies (PyYAML, rich, etc.)
- **`hcsbuilder.py`** — Main builder script
- **`hcsbuilder.sh` / `hcsbuilder.bat`** — Launcher scripts for Linux/macOS/Windows
- **`setup_env.sh` / `setup_env.bat`** — Creates `.venv` and installs dependencies

### Documentation

- **`HCSBUILDER-README.txt`** — Manual for the hcsbuilder utility
- **`HSB-FORMAT.md`** — HSB file format specification

### Editor Support

- **`.vscode/`** — VSCode settings (file associations)
- **`hsb-syntax-highlighter/`** — VSCode extension for `.hsb` syntax highlighting

### Development Files

- **`TODO.md`** — Development task list
- **`AI-AGENTS-MUST-READ.md`** — Instructions for AI assistants working on this project
- **`testinput.hsb`** — Sample HSB file for testing
- **`test-seo-complete.hsb`** — Development test file demonstrating front matter support & other SEO elements
- **`standardtestpage.hsb`** — Development test file demonstrating elements in a fully styled page

### Site Assets

- **`templates/`** — HTML snippets for template insertion (specific to Hammercroft's site)
- **`_output/`** — Local testing assets that emulate the production environment
- **`rsoutput.sh`** — Resets the `output/` directory and copies the contents of `_output/` into it

> **Note for forks**: If building your own site, you'll need custom templates. Feel free to reference mine as examples.

---

## License

MIT License — See `LICENSE` file for details.

---

## Contributing

This is a personal project. Contributions are not expected, but you're welcome to fork and adapt it for your own use.
