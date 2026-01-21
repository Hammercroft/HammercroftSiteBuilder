# HSB Format Guide

**HSB (Hammercroft Site Builder)** is a custom file format for defining the metadata, base content, and insertion points for templates (which are snippets of HTML) for web pages. Each `.hsb` file consists of two distinct sections separated by a special marker.

---

## File Structure

An HSB file has the following structure:

``` txt
[YAML Manifest Section]
end of manifest
[HTML Body Section]
```

### 1. Manifest Section (YAML)

The **manifest section** contains metadata about the page and is written in **YAML format**. This section starts at the beginning of the file and continues until the `end of manifest` marker line.

#### Manifest Syntax Rules

- Must be valid YAML
- Can contain any YAML data structures (strings, lists, objects, etc.)

#### Manifest Keys

The manifest supports a wide range of keys organized into logical categories:

##### Basic Page Metadata

| Key                 | Type    | Description                                                                                                                                                                 |
|---------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `title`             | String  | The page title. Injected into `<title>` tag and used for SEO metadata (OpenGraph, Twitter Card, Schema.org).                                                               |
| `description`       | String  | The page description. Injected as `<meta name="description">` and used for SEO metadata.                                                                                    |
| `keywords`          | String  | Comma-separated keywords. Injected as `<meta name="keywords">` and used as article tags in SEO metadata.                                                                   |
| `canonical`         | String  | Canonical URL for the page. Injected as `<link rel="canonical">` and used in SEO metadata.                                                                                 |
| `robot_directives`  | String  | Robot directives for search engines (e.g., `"index, follow"`, `"noindex, nofollow"`). Injected as `<meta name="robots">`.                                                  |

##### HTML Structure Control

| Key                 | Type    | Description                                                                                                                                                                 |
|---------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `head_boilerplate`  | Boolean | Controls whether basic HTML head meta tags are automatically added. Defaults to `true`. When `true`, adds charset, X-UA-Compatible, and viewport meta tags.                |
| `lang`              | String  | Language code for the page (e.g., `"en"`, `"es"`, `"fr"`). Sets or overrides the `lang` attribute on the `<html>` tag.                                                     |
| `html_attributes`   | Array   | List of attributes to add to the `<html>` tag (e.g., `'lang="en"'`, `'dir="ltr"'`).                                                                                        |
| `body_attributes`   | Array   | List of attributes to add to the `<body>` tag (e.g., `'class="dark-mode"'`, `'data-theme="blue"'`).                                                                        |
| `is_application`    | Boolean | When `true`, adds `role="application"` to the `<body>` tag. Use for highly interactive web applications.                                                                   |
| `add_to_header`     | Array   | List of HTML snippets to inject into the page header. Processed last, after all other head content.                                                                        |

##### SEO Metadata - Author & Publisher

| Key                 | Type    | Description                                                                                                                                                                 |
|---------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `author`            | String  | Author name. Used in Schema.org JSON-LD and Open Graph metadata.                                                                                                           |
| `author_type`       | String  | Schema.org type for author (default: `"Person"`). Can be `"Person"` or `"Organization"`.                                                                                   |
| `author_url`        | String  | URL for the author's website or profile. Used in Schema.org JSON-LD.                                                                                                       |
| `publisher`         | String  | Publisher name. Used in Schema.org JSON-LD.                                                                                                                                |
| `publisher_type`    | String  | Schema.org type for publisher (default: `"Organization"`). Can be `"Person"` or `"Organization"`.                                                                          |
| `publisher_url`     | String  | URL for the publisher's website. Used in Schema.org JSON-LD.                                                                                                               |

##### SEO Metadata - Dates & Classification

| Key                 | Type    | Description                                                                                                                                                                 |
|---------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `date_published`    | String  | Publication date in ISO 8601 format (e.g., `"2025-02-28T23:33:10+08:00"`). Used in Schema.org and Open Graph.                                                              |
| `date_modified`     | String  | Last modification date in ISO 8601 format. Used in Schema.org JSON-LD.                                                                                                     |
| `article_section`   | String  | Article category/section (e.g., `"Gaming"`, `"Technology"`). Used in Schema.org and Open Graph.                                                                            |

##### SEO Metadata - Schema.org & Open Graph

| Key                   | Type    | Description                                                                                                                                                               |
|-----------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `schema_org_type`     | String  | Schema.org type (e.g., `"Article"`, `"BlogPosting"`, `"WebPage"`). Required for Schema.org JSON-LD generation.                                                          |
| `open_graph_type`     | String  | Open Graph type (e.g., `"article"`, `"website"`). Required for Open Graph metadata generation.                                                                           |
| `page_image`          | String  | URL to the page's featured image. Used in Schema.org, Open Graph, and Twitter Card metadata.                                                                             |
| `site_name`           | String  | Name of the website/site. Used in Open Graph metadata.                                                                                                                   |
| `main_entity_of_page` | Object  | Schema.org mainEntityOfPage object. Auto-generated from `canonical` if not provided.                                                                                     |

##### SEO Metadata - Twitter Card

| Key                 | Type    | Description                                                                                                                                                                 |
|---------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `twitter_user`      | String  | Twitter username (e.g., `"@hammercroft"`). Used for both `twitter:site` and `twitter:creator` meta tags.                                                                   |

##### Frontmatter Control

| Key                 | Type    | Description                                                                                                                                                                 |
|---------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `no_frontmatter`    | Boolean | When `true`, disables automatic generation of SEO metadata (Schema.org, Open Graph, Twitter Card). Defaults to `false`.                                                    |

#### Manifest Example

##### Basic Example

```yaml
# Page metadata
title: "Page Title"
description: "A comprehensive guide to using HSB format"
keywords: "hsb, html, static site generator"

# Language setting (alternative to using html_attributes)
lang: "en"

# HTML and body tag attributes
html_attributes:
  - 'dir="ltr"'
body_attributes:
  - 'class="dark-mode"'
  - 'data-theme="blue"'

# Application role for interactive web apps
is_application: false

# Custom header additions (processed last)
add_to_header:
  - "<!-- Custom metadata -->"
  - "<meta name='author' content='Your Name'>"
  - "<link rel='stylesheet' href='styles.css'>"
```

##### SEO-Optimized Example

```yaml
# Basic page metadata
title: "How to Install Mobile Legends: Bang Bang on Ubuntu"
description: "A concise step-by-step guide on how to install Mobile Legends: Bang Bang on Waydroid, on Ubuntu. This guide also involves the installation of Google Apps and LibNDK."
keywords: "Ubuntu, Mobile Legends, MLBB, Waydroid, Gaming, Android on Linux"
canonical: "https://hammercroft.nekoweb.org/mlbb-ubuntu-installation-guide.html"

# SEO Metadata
author: "Hammercroft"
author_type: "Person"
author_url: "https://hammercroft.nekoweb.org"
publisher: "Hammercroft"
publisher_type: "Organization"
publisher_url: "https://hammercroft.nekoweb.org"
date_published: "2025-02-28T23:33:10+08:00"
date_modified: "2025-03-01T00:17:13+08:00"

# Schema.org & Open Graph
schema_org_type: "Article"
open_graph_type: "article"
page_image: "https://hammercroft.nekoweb.org/mlbb-ubuntu-screenshot.webp"
site_name: "Hammercroft"
article_section: "Gaming"

# Twitter
twitter_user: "@hammercroft"

# HTML attributes
lang: "en"
```

> [!TIP]
> When using SEO metadata, ensure `schema_org_type` and `open_graph_type` are set to enable automatic generation of Schema.org JSON-LD and Open Graph meta tags. The system will automatically generate Twitter Card metadata with type `summary_large_image`.

---

### 2. End of Manifest Marker

The **end of manifest** marker is a special line that separates the YAML manifest from the HTML body.

#### Syntax

``` hsb
end of manifest
```

> [!IMPORTANT]
> This line must appear exactly as shown (case-sensitive, no extra whitespace). Everything before this line is treated as YAML; everything after is treated as HTML.

---

### 3. Body Section (HTML)

The **body section** contains the actual page content and is written in **HTML format**. This section begins immediately after the `end of manifest` line and continues to the end of the file.

#### Body Syntax Rules

- Standard HTML5 syntax
- Can include inline `<script>` and `<style>` tags
- Supports HTML comments

#### Body Section Example

```html
<h1>HTML Content</h1>
<p>Body content goes here</p>
<script>
  // Inline JavaScript is allowed
  console.log("Hello, world!");
</script>
```

---

## Special Comment Directives

HSB uses special HTML comment syntax to define insertion points for templates and dynamic content.

### Template Insertion Points

Template insertion points specify where named templates should be inserted during the build process.

#### Template Syntax

```html
<!--$^template-name-->
```

- **Prefix**: `$^`
- **Format**: `<!--$^` followed by the template name, then `-->`
- **Example**: `<!--$^test-template-insertion-->`

### Special Insertion Points

Special insertion points define locations for dynamic content insertion using keywords and optional arguments.

#### Syntax (Simple)

```html
<!--$_KEYWORD-->
```

#### Syntax (With Arguments)

```html
<!--$_KEYWORD arg1="value1" arg2="value2"
arg3="value3"
-->
```

- **Prefix**: `$_`
- **Format**: `<!--$_` followed by the keyword (typically uppercase), optional string attributes, then `-->`
- **Arguments**: Use `key="value"` syntax, can span multiple lines
- **Examples**:

  ```html
  <!--$_TEST_SPECIAL_INSERTION_KEYWORD-->
  <!--$_ANOTHER_SPECIAL_INSERTION_KEYWORD arg1="https://localhost:8080" arg2="12em" 
  arg3="false"
  -->
  ```

---

## SEO Metadata Generation

When SEO-related manifest keys are provided, the HCS Builder automatically generates comprehensive metadata in the HTML `<head>` section. This includes:

### Schema.org JSON-LD

If `schema_org_type` is set, a JSON-LD script tag is generated with structured data for search engines.

**Generated when**: `schema_org_type` is present

**Includes**:

- `@context` and `@type` (from `schema_org_type`)
- `headline` (from `title`)
- `description` (from `description`)
- `image` (from `page_image`)
- `url` (from `canonical`)
- `author` object (from `author`, `author_type`, `author_url`)
- `publisher` object (from `publisher`, `publisher_type`, `publisher_url`)
- `datePublished` and `dateModified` (from `date_published`, `date_modified`)
- `mainEntityOfPage` (auto-generated from `canonical` or custom object)
- `articleSection` (from `article_section`)

**Example output**:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to Install Mobile Legends: Bang Bang on Ubuntu",
  "author": {
    "@type": "Person",
    "name": "Hammercroft",
    "url": "https://hammercroft.nekoweb.org"
  },
  "datePublished": "2025-02-28T23:33:10+08:00"
}
</script>
```

### Open Graph Meta Tags

If `open_graph_type` is set, Open Graph meta tags are generated for social media sharing.

**Generated when**: `open_graph_type` is present

**Includes**:

- `og:title`, `og:type`, `og:url`, `og:image`, `og:description`, `og:site_name`
- Article-specific tags when `open_graph_type` is `"article"`:
  - `article:published_time`, `article:author`, `article:section`, `article:tag`

**Example output**:

```html
<meta property="og:title" content="How to Install Mobile Legends: Bang Bang on Ubuntu">
<meta property="og:type" content="article">
<meta property="og:url" content="https://hammercroft.nekoweb.org/mlbb-ubuntu-installation-guide.html">
<meta property="og:image" content="https://hammercroft.nekoweb.org/mlbb-ubuntu-screenshot.webp">
```

### Twitter Card Meta Tags

Twitter Card metadata is automatically generated when SEO metadata is enabled.

**Generated when**: SEO metadata is enabled (frontmatter is not disabled)

**Includes**:

- `twitter:card` (always `summary_large_image`)
- `twitter:title`, `twitter:description`, `twitter:image`
- `twitter:site` and `twitter:creator` (from `twitter_user`)

**Example output**:

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="How to Install Mobile Legends: Bang Bang on Ubuntu">
<meta name="twitter:site" content="@hammercroft">
```

### Disabling SEO Metadata

To disable automatic SEO metadata generation, set `no_frontmatter: true` in the manifest.

---

## Complete Example

```hsb
# Page configuration
title: "Test Page"
add_to_header:
  - "<!-- test use of add_to_header -->"

end of manifest

<h1>Welcome</h1>
<p>This is the page content.</p>

<br>

<!--$^test-template-insertion-->
<!--$_TEST_SPECIAL_INSERTION_KEYWORD-->

<script>
  console.log("Page loaded");
</script>

---

## Best Practices

### General

1. **Use comments**: Document complex YAML structures with `#` comments
2. **Validate YAML**: Ensure the manifest section is valid YAML before the `end of manifest` marker. Use quotes for strings containing colons (`:`)
3. **Consistent naming**: Use descriptive names for template and special insertion points
4. **Argument formatting**: For multi-line special insertion points, align arguments for readability
5. **Body Content Spacing**: Leave at least one blank line between the `end of manifest` marker and the first line of the body section for improved readability

### SEO Optimization

1. **Always set both types**: When using SEO metadata, set both `schema_org_type` and `open_graph_type` for maximum compatibility
2. **Use ISO 8601 dates**: Format dates as `YYYY-MM-DDTHH:MM:SS+TZ:TZ` (e.g., `"2025-02-28T23:33:10+08:00"`)
3. **Provide complete author info**: Include `author`, `author_type`, and `author_url` for rich author metadata
4. **Include images**: Always set `page_image` for better social media sharing (recommended: 1200x630px for Open Graph)
5. **Use descriptive keywords**: Comma-separate keywords in the `keywords` field for better article tagging
6. **Set canonical URLs**: Always include `canonical` to avoid duplicate content issues
7. **Update modification dates**: Keep `date_modified` current when updating content

---

## Syntax Highlighting

When using the HSB syntax highlighter extension:

- **Manifest section**: Highlighted as YAML
- **Body section**: Highlighted as HTML
- **`end of manifest`**: Special highlighting

---

## File Extension

HSB files use the `.hsb` file extension.
