# HSB Syntax Highlighter

Syntax highlighting extension for Hammercroft Site Builder (HSB) format files.

## Features

This extension provides syntax highlighting for `.hsb` files with special highlighting for:

- **End of Manifest Marker**: The `end of manifest` line that separates YAML manifest from HTML body
- **Template Insertion**: Comments with `$^` prefix (e.g., `<!--$^template-name-->`)
- **Special Insertion**: Comments with `$_` prefix (e.g., `<!--$_SPECIAL_KEYWORD-->`)
- **YAML Manifest**: YAML syntax highlighting in the manifest section
- **HTML Content**: HTML syntax highlighting in the body section

## Installation

### From Source

1. Copy the `hsb-syntax-highlighter` folder to your VS Code extensions directory:
   - **Linux/macOS**: `~/.vscode/extensions/`
   - **Windows**: `%USERPROFILE%\.vscode\extensions\`

2. Reload VS Code

### From VSIX (if packaged)

1. Run: `code --install-extension hsb-syntax-highlighter-0.1.4.vsix` (or replace `code` with any fork of VS Code, such as `antigravity`)

## Usage

Open any `.hsb` file and the syntax highlighting will be applied automatically.

## HSB Format Structure

```hsb
# actual keys that HSB uses
title: "Page Title"
add_to_header:
  - "<!-- metadata -->"
# as long as its valid yaml, it will be highlighted as yaml
further_yaml_data:
  - "item"
# end of manifest marker -- anything before this line is YAML, anything after is HTML
end of manifest

<h1>HTML Content</h1>
<p>Body content goes here</p>
<script>
  // nothing is stopping you from using inline scripts here
  console.log("Hello, world!");
</script>

<!--$^template-name-->
<!--$_SPECIAL_INSERTION_KEYWORD-->
<!--$_ANOTHER_SPECIAL_INSERTION_KEYWORD key="value"
key2="value2"
key3="value3"
-->
```

## Color Customization

You can customize the colors in your VS Code settings by adding theme overrides:

```json
{
  "editor.tokenColorCustomizations": {
    "textMateRules": [
      {
        "scope": "keyword.control.manifest.hsb",
        "settings": {
          "foreground": "#ff6b6b",
          "fontStyle": "bold"
        }
      },
      {
        "scope": "keyword.operator.template.hsb",
        "settings": {
          "foreground": "#4ecdc4",
          "fontStyle": "bold"
        }
      },
      {
        "scope": "entity.name.template.hsb",
        "settings": {
          "foreground": "#45b7d1"
        }
      },
      {
        "scope": "keyword.operator.special.hsb",
        "settings": {
          "foreground": "#f9ca24",
          "fontStyle": "bold"
        }
      },
      {
        "scope": "entity.name.special.hsb",
        "settings": {
          "foreground": "#f0932b"
        }
      }
    ]
  }
}
```

## License

MIT
