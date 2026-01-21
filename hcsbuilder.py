#!/usr/bin/env python3
"""
HCS Builder - Hammercroft Site Builder
A command line utility for building and managing sites.
"""

# ============================================================================
# CONSTANTS
# ============================================================================

ALLOWED_EXTENSIONS = {'hsb', 'txt', 'htm', 'html', 'utf8', 'u8', ''}
DEFAULT_TWITTER_CARD_TYPE = 'summary_large_image'

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
import argparse
import yaml
import re

try:
    from rich import print as rprint
    from rich.console import Console
    richAvailable = True
except ImportError:
    richAvailable = False


# ============================================================================
# COLORS CLASS
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ============================================================================
# MANIFEST CLASS
# ============================================================================

class Manifest:
    """
    Wrapper class for manifest data that provides attribute-style access.
    
    Usage:
        manifest = Manifest({'title': 'My Page', 'add_to_header': ['<meta>']})
        print(manifest.title)  # 'My Page'
        print(manifest.add_to_header)  # ['<meta>']
        print(manifest.nonexistent)  # None
    """
    
    def __init__(self, data=None):
        """Initialize manifest with optional data dictionary."""
        self._data = data if data is not None else {}
    
    def __getattr__(self, name):
        """Allow attribute-style access to manifest data."""
        if name.startswith('_'):
            # Avoid infinite recursion for private attributes
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return self._data.get(name)
    
    def __contains__(self, key):
        """Support 'in' operator."""
        return key in self._data
    
    def get(self, key, default=None):
        """Dictionary-style get method."""
        return self._data.get(key, default)
    
    def __repr__(self):
        """String representation for debugging."""
        return f"Manifest({self._data})"


# ============================================================================
# FILE COLLECTION UTILITIES
# ============================================================================

def collectFilesFromDirectory(directory_path, allowed_extensions):
    """
    Recursively collect all files with valid extensions from a directory.
    
    Args:
        directory_path: Root directory to search
        allowed_extensions: Set of allowed file extensions (without dots)
        
    Returns:
        List of absolute file paths
    """
    collectedFiles = []
    
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            fileExt = os.path.splitext(filename)[1].lstrip('.')
            if fileExt in allowed_extensions:
                filePath = os.path.join(root, filename)
                collectedFiles.append(os.path.abspath(filePath))
    
    return collectedFiles


# ============================================================================
# TEMPLATE LOADING AND INSERTION POINT PROCESSING
# ============================================================================

def loadTemplates(template_dir, verbose=False):
    """
    Load all HTML templates and Python handler scripts from the templates directory.
    
    Args:
        template_dir: Path to the templates directory
        verbose: Enable verbose output
        
    Returns:
        Tuple of (templates_dict, handler_scripts_list)
        - templates_dict: {template_id: html_content}
        - handler_scripts_list: [script_name, ...]
    """
    templates = {}
    handlers = []
    
    if not os.path.exists(template_dir) or not os.path.isdir(template_dir):
        if verbose:
            print(f"{Colors.YELLOW}Template directory not found: {template_dir}{Colors.ENDC}")
        return templates, handlers
    
    # Valid filename pattern: alphanumeric plus _-. symbols
    valid_filename_pattern = re.compile(r'^[a-zA-Z0-9_.-]+$')
    
    # Scan immediate children only (not recursive)
    try:
        entries = os.listdir(template_dir)
    except OSError as e:
        print(f"{Colors.RED}ERROR: Cannot read template directory: {template_dir}{Colors.ENDC}", file=sys.stderr)
        print(f"{Colors.RED}Reason: {e}{Colors.ENDC}", file=sys.stderr)
        return templates, handlers
    
    for entry in entries:
        entry_path = os.path.join(template_dir, entry)
        
        # Skip directories
        if not os.path.isfile(entry_path):
            continue
        
        # Validate filename
        if not valid_filename_pattern.match(entry):
            if verbose:
                print(f"{Colors.YELLOW}Skipping invalid filename: {entry}{Colors.ENDC}")
            continue
        
        # Get file extension
        name_without_ext, ext = os.path.splitext(entry)
        ext = ext.lower()
        
        # Load HTML templates
        if ext in ['.html', '.htm']:
            try:
                with open(entry_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                templates[name_without_ext] = template_content
                if verbose:
                    print(f"{Colors.CYAN}Loaded template:{Colors.ENDC} {name_without_ext}")
            except Exception as e:
                print(f"{Colors.YELLOW}WARNING: Failed to load template {entry}: {e}{Colors.ENDC}", file=sys.stderr)
        
        # Track Python handler scripts
        elif ext == '.py':
            handlers.append(name_without_ext)
            if verbose:
                print(f"{Colors.CYAN}Found handler script:{Colors.ENDC} {name_without_ext}")
    
    if verbose and templates:
        print(f"{Colors.GREEN}Loaded {len(templates)} template(s){Colors.ENDC}")
    if verbose and handlers:
        print(f"{Colors.GREEN}Found {len(handlers)} handler script(s){Colors.ENDC}")
    
    return templates, handlers


def applyIndentation(content, indentation):
    """
    Apply indentation to each line of content.
    
    Args:
        content: Multi-line string to indent
        indentation: String of whitespace to prepend to each line
        
    Returns:
        Indented content string
    """
    if not indentation:
        return content
    
    lines = content.split('\n')
    # Apply indentation to all lines except the first (which is already positioned)
    indented_lines = [lines[0]] + [indentation + line for line in lines[1:]]
    return '\n'.join(indented_lines)


def scanInsertionPoints(html_content):
    """
    Scan HTML content for HSB insertion points.
    
    Args:
        html_content: HTML string to scan
        
    Returns:
        Dictionary with:
        - 'template_insertions': List of {name, position, original, indentation}
        - 'special_insertions': List of {keyword, arguments, position, original, indentation}
    """
    results = {
        'template_insertions': [],
        'special_insertions': []
    }
    
    # Helper function to extract leading whitespace before a position
    def get_leading_whitespace(content, pos):
        """Get the whitespace from the start of the line to the position."""
        # Find the start of the line
        line_start = content.rfind('\n', 0, pos) + 1  # +1 to skip the newline itself
        # Extract whitespace between line start and position
        leading_text = content[line_start:pos]
        # Return only if it's all whitespace, otherwise empty string
        return leading_text if leading_text.strip() == '' else ''
    
    # Template insertions: <!--$^template-name-->
    template_pattern = r'<!--\$\^([a-zA-Z0-9_-]+)-->'
    for match in re.finditer(template_pattern, html_content):
        indentation = get_leading_whitespace(html_content, match.start())
        results['template_insertions'].append({
            'name': match.group(1),
            'position': match.start(),
            'original': match.group(0),
            'indentation': indentation
        })
    
    # Special insertions: <!--$_KEYWORD args...-->
    special_pattern = r'<!--\$_([A-Z_]+)(.*?)-->'
    for match in re.finditer(special_pattern, html_content, re.DOTALL):
        keyword = match.group(1)
        args_section = match.group(2).strip()
        
        # Parse arguments: key="value" pairs
        arguments = {}
        if args_section:
            arg_pattern = r'(\w+)="([^"]*)"'
            for arg_match in re.finditer(arg_pattern, args_section):
                arguments[arg_match.group(1)] = arg_match.group(2)
        
        indentation = get_leading_whitespace(html_content, match.start())
        results['special_insertions'].append({
            'keyword': keyword,
            'arguments': arguments,
            'position': match.start(),
            'original': match.group(0),
            'indentation': indentation
        })
    
    return results


def applyTemplates(body_content, templates_dict, verbose=False):
    """
    Apply templates to insertion points in body content.
    
    Args:
        body_content: HTML body content with insertion points
        templates_dict: Dictionary of {template_id: html_content}
        verbose: Enable verbose output
        
    Returns:
        Processed body content with templates applied
        
    Raises:
        ValueError: If a referenced template is not found
    """
    # Scan for insertion points
    insertion_points = scanInsertionPoints(body_content)
    
    # Process template insertions
    # Replace in reverse order to maintain correct positions
    template_insertions = sorted(insertion_points['template_insertions'], 
                                key=lambda x: x['position'], 
                                reverse=True)
    
    for insertion in template_insertions:
        template_name = insertion['name']
        
        # Check if template exists
        if template_name not in templates_dict:
            raise ValueError(f"Template not found: {template_name}")
        
        # Get template content and apply indentation
        template_content = templates_dict[template_name]
        indentation = insertion.get('indentation', '')
        indented_content = applyIndentation(template_content, indentation)
        
        # Replace the insertion point comment with indented template content
        start_pos = insertion['position']
        end_pos = start_pos + len(insertion['original'])
        body_content = body_content[:start_pos] + indented_content + body_content[end_pos:]
        
        if verbose:
            indent_info = f" (indent: {len(indentation)} spaces)" if indentation else ""
            print(f"{Colors.GREEN}Applied template:{Colors.ENDC} {template_name}{indent_info}")
    
    # Log special insertions (not yet implemented)
    special_insertions = insertion_points['special_insertions']
    if special_insertions:
        print(f"\n{Colors.HEADER}Special insertion points found:{Colors.ENDC}")
        for insertion in special_insertions:
            print(f"  {Colors.CYAN}Keyword:{Colors.ENDC} {insertion['keyword']}")
            if insertion['arguments']:
                print(f"  {Colors.CYAN}Arguments:{Colors.ENDC} {insertion['arguments']}")
    
    return body_content


# ============================================================================
# ATTRIBUTE MANIPULATION UTILITIES
# ============================================================================

def setOrOverrideAttribute(attribute_list, attribute_name, attribute_value):
    """
    Set or override an attribute in an attribute list.
    
    If an attribute with the given name already exists (e.g., 'lang='), 
    it will be replaced. Otherwise, the new attribute will be appended.
    
    Args:
        attribute_list: List of attribute strings (e.g., ['lang="en"', 'dir="ltr"'])
        attribute_name: Name of the attribute to set (e.g., 'lang')
        attribute_value: Full attribute string to set (e.g., 'lang="en"')
        
    Returns:
        None (modifies attribute_list in place)
    """
    attribute_prefix = f"{attribute_name}="
    
    # Try to find and replace existing attribute
    for i, attr in enumerate(attribute_list):
        if attr.startswith(attribute_prefix):
            attribute_list[i] = attribute_value
            return
    
    # If not found, append the new attribute
    attribute_list.append(attribute_value)


# ============================================================================
# PER-FILE PROCESSING FUNCTION
# ============================================================================

def processSingleFile(input_path, output_dir, templates_dict=None, input_root=None, verbose=False):
    """
    Process a single input file and generate HTML output.
    
    Args:
        input_path: Path to the input file to process
        output_dir: Directory where output file should be written
        templates_dict: Dictionary of {template_id: html_content}
        input_root: Optional root directory for batch processing (preserves relative paths)
        verbose: Enable verbose output
        
    Returns:
        0 on success, 1 on error
    """
    # Input is a file - get absolute path and echo it
    absPath = os.path.abspath(input_path)
    print(f"{Colors.CYAN}Processing input file:{Colors.ENDC} {absPath}")
    
    # Determine output path, preserving directory structure if input_root is provided
    inputFilename = os.path.basename(input_path)
    outputFilename = os.path.splitext(inputFilename)[0] + '.html'
    
    if input_root:
        # Preserve directory structure relative to input_root
        relPath = os.path.relpath(input_path, input_root)
        relDir = os.path.dirname(relPath)
        
        if relDir:
            # Create subdirectory in output
            outputSubdir = os.path.join(output_dir, relDir)
            os.makedirs(outputSubdir, exist_ok=True)
            outputPath = os.path.join(outputSubdir, outputFilename)
        else:
            # File is directly in input_root
            outputPath = os.path.join(output_dir, outputFilename)
    else:
        # Single file mode - output directly to output_dir
        outputPath = os.path.join(output_dir, outputFilename)
    
    # Read and process the input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"{Colors.RED}ERROR: Failed to read input file: {input_path}{Colors.ENDC}", file=sys.stderr)
        print(f"{Colors.RED}Reason: {e}{Colors.ENDC}", file=sys.stderr)
        return 1
    
    # Parse the manifest and body
    # Look for "end of manifest" line (case-insensitive)
    lines = content.split('\n')
    manifestEndIndex = -1
    
    for i, line in enumerate(lines):
        if line.strip().lower() == 'end of manifest':
            manifestEndIndex = i
            break
    
    # Parse manifest YAML and extract body content
    manifest = Manifest()  # Empty manifest by default
    htmlAttributes = []
    bodyAttributes = []

    # Initialize frontmatter dictionary for SEO/metadata generation
    # Frontmatter includes: OpenGraph, Schema.org, Twitter Card, and other metadata
    frontmatter = {}
    shouldGenerateFrontmatter = True
    frontmatter['twitterCardType'] = DEFAULT_TWITTER_CARD_TYPE


    if manifestEndIndex >= 0:
        # Extract manifest YAML (everything before "end of manifest" line)
        manifestLines = lines[:manifestEndIndex]
        manifestYaml = '\n'.join(manifestLines)
        
        # Parse YAML if there's content
        if manifestYaml.strip():
            try:
                manifestData = yaml.safe_load(manifestYaml)
                if manifestData is not None:
                    manifest = Manifest(manifestData)
                    if verbose:
                        if richAvailable:
                            print(f"{Colors.HEADER}Parsed manifest:{Colors.ENDC}")
                            rprint(manifest._data)
                        else:
                            print(f"Parsed manifest: {manifest}")
            except yaml.YAMLError as e:
                print(f"{Colors.RED}ERROR: Failed to parse manifest YAML:{Colors.ENDC}", file=sys.stderr)
                print(f"{Colors.RED}{e}{Colors.ENDC}", file=sys.stderr)
                print(f"{Colors.YELLOW}Skipping file: {input_path}{Colors.ENDC}", file=sys.stderr)
                return 1
        
        # Skip the manifest and the "end of manifest" line itself
        bodyLines = lines[manifestEndIndex + 1:]
        bodyContent = '\n'.join(bodyLines)
    else:
        # No manifest found, use entire content
        bodyContent = content
    
    # MANIFEST PROCESSING & HEAD BUILDING
    # All appended lines should begin with 1 tab character

    # THIS MANIFEST CHECK SHOULD ALWAYS BE FIRST
    # Determine if head boilerplate should be added
    # Add boilerplate if key is missing or if it's explicitly set to true
    shouldAddHeadBoilerplate = manifest.get('head_boilerplate', True)
    
    # Build initial head content
    headContent = ""
    if shouldAddHeadBoilerplate:
        headContent = """
	<!-- [BASIC HEAD BOILERPLATE] -->
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">"""

    # Helper function to reduce repetitive manifest-to-frontmatter mapping
    def _map_manifest_to_frontmatter(manifest_key, frontmatter_key, label, add_to_head=None):
        """Map a manifest value to frontmatter and optionally add to head content.
        
        Args:
            manifest_key: Key to check in manifest object
            frontmatter_key: Key to set in frontmatter dict (None to skip frontmatter)
            label: Human-readable label for verbose output
            add_to_head: Function that takes value and returns HTML string to add to head
        """
        value = getattr(manifest, manifest_key, None)
        if value:
            if verbose:
                print(f"{Colors.BOLD}{label}:{Colors.ENDC} {value}")
            if frontmatter_key:
                frontmatter[frontmatter_key] = value
            if add_to_head:
                nonlocal headContent
                headContent += add_to_head(value)
    
    # Web robot (spider) directives
    _map_manifest_to_frontmatter(
        'robotDirectives', None, 'Page robot directives',
        lambda v: f"\n\t<meta name=\"robots\" content=\"{v}\">"
    )
    
    # Basic metadata (with head content generation)
    _map_manifest_to_frontmatter(
        'title', 'pageTitle', 'Page title',
        lambda v: f"\n\t<title>{v}</title>"
    )
    _map_manifest_to_frontmatter(
        'description', 'pageDescription', 'Page description',
        lambda v: f"\n\t<meta name=\"description\" content=\"{v}\">"
    )
    _map_manifest_to_frontmatter(
        'keywords', 'articleTags', 'Page keywords',
        lambda v: f"\n\t<meta name=\"keywords\" content=\"{v}\">"
    )
    _map_manifest_to_frontmatter(
        'canonical', 'canonicalAddress', 'Page canonical',
        lambda v: f"\n\t<link rel=\"canonical\" href=\"{v}\">"
    )
    
    # Metadata for frontmatter only (no head content)
    frontmatter_mappings = [
        ('author', 'author', 'Page author'),
        ('date_published', 'datePublished', 'Page date published'),
        ('date_modified', 'dateModified', 'Page date modified'),
        ('article_section', 'articleSection', 'Page article section'),
        ('open_graph_type', 'openGraphType', 'Page open graph type'),
        ('twitter_user', 'twitterUser', 'Page twitter user'),
        ('main_entity_of_page', 'mainEntityOfPage', 'Schema.org main entity of page'),
        ('schema_org_type', 'schemaOrgType', 'Schema.org type'),
        ('page_image', 'pageImage', 'Page image'),
        ('site_name', 'siteName', 'Site name'),
        ('author_type', 'authorType', 'Author type'),
        ('author_url', 'authorUrl', 'Author URL'),
        ('publisher', 'publisher', 'Publisher name'),
        ('publisher_type', 'publisherType', 'Publisher type'),
        ('publisher_url', 'publisherUrl', 'Publisher URL'),
    ]
    
    for manifest_key, frontmatter_key, label in frontmatter_mappings:
        _map_manifest_to_frontmatter(manifest_key, frontmatter_key, label)

    # html tag attributes & body tag attributes
    # Store as objects for now, will convert to strings after all manifest checks
    if manifest.html_attributes:
        if verbose:
            print(f"{Colors.BOLD}HTML attributes:{Colors.ENDC} {manifest.html_attributes}")
        # Store the list directly for now
        htmlAttributes = manifest.html_attributes if isinstance(manifest.html_attributes, list) else [manifest.html_attributes]
    if manifest.body_attributes:
        if verbose:
            print(f"{Colors.BOLD}Body attributes:{Colors.ENDC} {manifest.body_attributes}")
        # Store the list directly for now
        bodyAttributes = manifest.body_attributes if isinstance(manifest.body_attributes, list) else [manifest.body_attributes]

    # html language attribute
    if manifest.lang:
        if verbose:
            print(f"{Colors.BOLD}HTML language:{Colors.ENDC} {manifest.lang}")
        setOrOverrideAttribute(htmlAttributes, "lang", f"lang=\"{manifest.lang}\"")

    # application role
    if manifest.is_application:
        if verbose:
            print(f"{Colors.BOLD}Application role:{Colors.ENDC} {manifest.is_application}")
        setOrOverrideAttribute(bodyAttributes, "role", "role=\"application\"")

    # Front matter generation question
    if manifest.no_frontmatter:
        shouldGenerateFrontmatter = False

    # Generate frontmatter (Schema.org JSON-LD, Open Graph, Twitter Card)
    if shouldGenerateFrontmatter and frontmatter:
        import json
        
        frontmatterContent = "\n\n\t<!-- [SEO METADATA] -->"
        
        # Generate Schema.org JSON-LD
        if frontmatter.get('schemaOrgType'):
            jsonld = {
                "@context": "https://schema.org",
                "@type": frontmatter['schemaOrgType']
            }
            
            # Add common fields
            if frontmatter.get('pageTitle'):
                jsonld['headline'] = frontmatter['pageTitle']
            if frontmatter.get('pageDescription'):
                jsonld['description'] = frontmatter['pageDescription']
            if frontmatter.get('pageImage'):
                jsonld['image'] = frontmatter['pageImage']
            if frontmatter.get('canonicalAddress'):
                jsonld['url'] = frontmatter['canonicalAddress']
            
            # Add author
            if frontmatter.get('author'):
                author_obj = {
                    "@type": frontmatter.get('authorType', 'Person'),
                    "name": frontmatter['author']
                }
                if frontmatter.get('authorUrl'):
                    author_obj['url'] = frontmatter['authorUrl']
                jsonld['author'] = author_obj
            
            # Add publisher
            if frontmatter.get('publisher'):
                publisher_obj = {
                    "@type": frontmatter.get('publisherType', 'Organization'),
                    "name": frontmatter['publisher']
                }
                if frontmatter.get('publisherUrl'):
                    publisher_obj['url'] = frontmatter['publisherUrl']
                jsonld['publisher'] = publisher_obj
            
            # Add dates
            if frontmatter.get('datePublished'):
                # Convert datetime to ISO 8601 string if needed
                date_pub = frontmatter['datePublished']
                jsonld['datePublished'] = date_pub.isoformat() if hasattr(date_pub, 'isoformat') else str(date_pub)
            if frontmatter.get('dateModified'):
                date_mod = frontmatter['dateModified']
                jsonld['dateModified'] = date_mod.isoformat() if hasattr(date_mod, 'isoformat') else str(date_mod)
            
            # Add mainEntityOfPage
            if frontmatter.get('mainEntityOfPage'):
                jsonld['mainEntityOfPage'] = frontmatter['mainEntityOfPage']
            elif frontmatter.get('canonicalAddress'):
                # Auto-generate from canonical address
                jsonld['mainEntityOfPage'] = {
                    "@type": "WebPage",
                    "@id": frontmatter['canonicalAddress']
                }
            
            # Add article-specific fields
            if frontmatter.get('articleSection'):
                jsonld['articleSection'] = frontmatter['articleSection']
            
            # Format JSON-LD with proper indentation
            jsonld_str = json.dumps(jsonld, indent=2, ensure_ascii=False)
            # Indent each line with tabs
            jsonld_lines = jsonld_str.split('\n')
            jsonld_indented = '\n'.join('\t\t\t' + line for line in jsonld_lines)
            
            frontmatterContent += f"\n\t<script type=\"application/ld+json\">\n{jsonld_indented}\n\t</script>"
        
        # Generate Open Graph meta tags
        if frontmatter.get('openGraphType'):
            frontmatterContent += "\n\n\t<!-- Open Graph (Facebook, LinkedIn, etc.) -->"
            
            if frontmatter.get('pageTitle'):
                frontmatterContent += f"\n\t<meta property=\"og:title\" content=\"{frontmatter['pageTitle']}\">"
            if frontmatter.get('openGraphType'):
                frontmatterContent += f"\n\t<meta property=\"og:type\" content=\"{frontmatter['openGraphType']}\">"
            if frontmatter.get('canonicalAddress'):
                frontmatterContent += f"\n\t<meta property=\"og:url\" content=\"{frontmatter['canonicalAddress']}\">"
            if frontmatter.get('pageImage'):
                frontmatterContent += f"\n\t<meta property=\"og:image\" content=\"{frontmatter['pageImage']}\">"
            if frontmatter.get('pageDescription'):
                frontmatterContent += f"\n\t<meta property=\"og:description\" content=\"{frontmatter['pageDescription']}\">"
            if frontmatter.get('siteName'):
                frontmatterContent += f"\n\t<meta property=\"og:site_name\" content=\"{frontmatter['siteName']}\">"
            
            # Article-specific Open Graph tags
            if frontmatter.get('openGraphType') == 'article':
                if frontmatter.get('datePublished'):
                    date_pub = frontmatter['datePublished']
                    date_str = date_pub.isoformat() if hasattr(date_pub, 'isoformat') else str(date_pub)
                    frontmatterContent += f"\n\t<meta property=\"article:published_time\" content=\"{date_str}\">"
                if frontmatter.get('author'):
                    frontmatterContent += f"\n\t<meta property=\"article:author\" content=\"{frontmatter['author']}\">"
                if frontmatter.get('articleSection'):
                    frontmatterContent += f"\n\t<meta property=\"article:section\" content=\"{frontmatter['articleSection']}\">"
                if frontmatter.get('articleTags'):
                    frontmatterContent += f"\n\t<meta property=\"article:tag\" content=\"{frontmatter['articleTags']}\">"
        
        # Generate Twitter Card meta tags
        if frontmatter.get('twitterCardType'):
            frontmatterContent += "\n\n\t<!-- Twitter Card -->"
            
            frontmatterContent += f"\n\t<meta name=\"twitter:card\" content=\"{frontmatter['twitterCardType']}\">"
            if frontmatter.get('pageTitle'):
                frontmatterContent += f"\n\t<meta name=\"twitter:title\" content=\"{frontmatter['pageTitle']}\">"
            if frontmatter.get('pageDescription'):
                frontmatterContent += f"\n\t<meta name=\"twitter:description\" content=\"{frontmatter['pageDescription']}\">"
            if frontmatter.get('pageImage'):
                frontmatterContent += f"\n\t<meta name=\"twitter:image\" content=\"{frontmatter['pageImage']}\">"
            if frontmatter.get('twitterUser'):
                twitter_user = frontmatter['twitterUser']
                frontmatterContent += f"\n\t<meta name=\"twitter:site\" content=\"{twitter_user}\">"
                frontmatterContent += f"\n\t<meta name=\"twitter:creator\" content=\"{twitter_user}\">"
        
        # Add frontmatter to head content
        headContent += frontmatterContent

    # THIS MANIFEST CHECK SHOULD ALWAYS BE LAST
    # Determine if there are add_to_header items to be appended to the head
    if manifest.add_to_header:
        headContent += "\n\n"
        if verbose:
            print(f"\t{Colors.BOLD}Adding to header:{Colors.ENDC} {manifest.add_to_header}")
        for item in manifest.add_to_header:
            headContent += "\t" + item
    
    # CONVERT ATTRIBUTES TO STRINGS
    # After all manifest checks are complete, convert attribute objects to strings
    htmlAttributesStr = " ".join(htmlAttributes) if isinstance(htmlAttributes, list) else ""
    bodyAttributesStr = " ".join(bodyAttributes) if isinstance(bodyAttributes, list) else ""
    
    # APPLY TEMPLATES TO BODY CONTENT
    # Process template insertion points if templates are available
    if templates_dict is None:
        templates_dict = {}
    
    try:
        bodyContent = applyTemplates(bodyContent, templates_dict, verbose=verbose)
    except ValueError as e:
        print(f"{Colors.RED}ERROR: {e}{Colors.ENDC}", file=sys.stderr)
        print(f"{Colors.YELLOW}Skipping file: {input_path}{Colors.ENDC}", file=sys.stderr)
        return 1
    # Wrap the body content in proper HTML structure
    outputContent = f"""<!DOCTYPE html>
<html {htmlAttributesStr}>
<head>{headContent}
</head>
<body {bodyAttributesStr}>

<!-- START OF HSB TEXT -->
{bodyContent}
<!-- END OF HSB TEXT -->

</body>
</html>"""
    
    # Write the processed content to output (overwrite if exists)
    try:
        with open(outputPath, 'w', encoding='utf-8') as f:
            f.write(outputContent)
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.GREEN}Page generation completed successfully!{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Input file:{Colors.ENDC}  {absPath}")
        print(f"{Colors.BOLD}Output file:{Colors.ENDC} {outputPath}")
        print(f"{Colors.BOLD}Output size:{Colors.ENDC} {len(outputContent)} bytes")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.RED}ERROR: Failed to write output file: {outputPath}{Colors.ENDC}", file=sys.stderr)
        print(f"{Colors.RED}Reason: {e}{Colors.ENDC}", file=sys.stderr)
        return 1
    
    return 0


# ============================================================================
# MAIN ENTRY POINT AND ARGUMENT PARSING
# ============================================================================

def main():
    """Main entry point for the HCS Builder utility."""
    parser = argparse.ArgumentParser(
        description='Hammercroft Site Builder - A command line utility for building and managing sites.',
        epilog='Generated output files will need to be manually moved to your actual web server.'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--template-dir',
        type=str,
        metavar='PATH',
        help='Path to the template folder (overrides default ./templates check)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        metavar='PATH',
        help='Path to the output folder (default: ./output)'
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input file to process'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Python version: {sys.version}")
        print(f"Arguments: {args}")
    
    # Check template folder
    templatePath = None
    if args.template_dir:
        # Manual template folder specified
        templatePath = args.template_dir
        if not os.path.exists(templatePath):
            print(f"ERROR: Specified template folder does not exist: {templatePath}", file=sys.stderr)
            return 1
        if not os.path.isdir(templatePath):
            print(f"ERROR: Specified template path is not a folder: {templatePath}", file=sys.stderr)
            return 1
    else:
        # Check for default ./templates folder
        templatePath = os.path.join(os.getcwd(), 'templates')
        if not os.path.exists(templatePath) or not os.path.isdir(templatePath):
            print("\nWARNING: MISSING ./templates FOLDER, NO TEMPLATE FOLDER PROVIDED\n")
            templatePath = None
    
    # Load templates if template directory exists
    templates_dict = {}
    handler_scripts = []
    if templatePath:
        if args.verbose:
            print(f"\n{Colors.HEADER}Loading templates from: {templatePath}{Colors.ENDC}")
        templates_dict, handler_scripts = loadTemplates(templatePath, verbose=args.verbose)
        if args.verbose:
            print()  # Empty line for spacing
    
    # Process input path
    inputPath = args.input_file
    
    if not os.path.exists(inputPath):
        print(f"ERROR: Input path does not exist: {inputPath}", file=sys.stderr)
        return 1
    
    # Determine output directory
    if args.output_dir:
        outputDir = args.output_dir
    else:
        outputDir = os.path.join(os.getcwd(), 'output')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(outputDir):
        try:
            os.makedirs(outputDir)
        except OSError as e:
            print(f"ERROR: Cannot create output folder: {outputDir}", file=sys.stderr)
            print(f"Reason: {e}", file=sys.stderr)
            return 1
    
    # Check if output directory is writable
    if not os.access(outputDir, os.W_OK):
        print(f"ERROR: Output folder is read-only: {outputDir}", file=sys.stderr)
        return 1
    
    # Define allowed file extensions
    allowedExtensions = ALLOWED_EXTENSIONS
    
    # Build set of files to process
    filesToProcess = set()
    inputRoot = None
    
    if os.path.isdir(inputPath):
        # Input is a directory - batch processing
        inputRoot = os.path.abspath(inputPath)
        collectedFiles = collectFilesFromDirectory(inputPath, allowedExtensions)
        
        if not collectedFiles:
            print(f"WARNING: No files with valid extensions found in directory: {inputPath}")
            return 0
        
        filesToProcess = set(collectedFiles)
        
        if args.verbose:
            print(f"\n{Colors.BOLD}Batch processing mode:{Colors.ENDC} Found {len(filesToProcess)} file(s) to process")
            print(f"{Colors.BOLD}Input directory:{Colors.ENDC} {inputRoot}")
            print(f"{Colors.BOLD}Output directory:{Colors.ENDC} {outputDir}\n")
    else:
        # Input is a single file
        # Check file extension to ensure it's valid
        fileExt = os.path.splitext(inputPath)[1].lstrip('.')
        
        if fileExt not in allowedExtensions:
            print(f"ERROR: Invalid file extension '.{fileExt}'. Allowed extensions: {', '.join(sorted([f'.{e}' if e else '(no extension)' for e in allowedExtensions]))}", file=sys.stderr)
            return 1
        
        filesToProcess = {os.path.abspath(inputPath)}
    
    # Process each file in the set
    successCount = 0
    failCount = 0
    failedFiles = []
    
    totalFiles = len(filesToProcess)
    
    for filePath in sorted(list(filesToProcess)):
        result = processSingleFile(filePath, outputDir, templates_dict=templates_dict, input_root=inputRoot, verbose=args.verbose)
        if result == 0:
            successCount += 1
        else:
            failCount += 1
            # Compute a friendly relative path for the report if possible
            if inputRoot:
                friendlyName = os.path.relpath(filePath, inputRoot)
            else:
                friendlyName = os.path.basename(filePath)
            failedFiles.append(friendlyName)
    
    # If we processed multiple files (batch mode), print a summary
    if len(filesToProcess) > 1 or inputRoot:
        print("\n" + f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}BATCH PROCESSING SUMMARY{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Total Files:{Colors.ENDC} {totalFiles}")
        print(f"{Colors.BOLD}Successful:{Colors.ENDC}  {Colors.GREEN}{successCount}{Colors.ENDC}")
        
        # Color the failed count RED if > 0, else GREEN (or default)
        failColor = Colors.RED if failCount > 0 else Colors.GREEN
        print(f"{Colors.BOLD}Failed:{Colors.ENDC}      {failColor}{failCount}{Colors.ENDC}")
        
        if failCount > 0:
            print(f"{Colors.BOLD}{'-' * 60}{Colors.ENDC}")
            print(f"{Colors.RED}FAILED FILES:{Colors.ENDC}")
            for badFile in failedFiles:
                print(f" - {badFile}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}" + "\n")
        
        # Return 1 if there were any failures, otherwise 0
        return 1 if failCount > 0 else 0
        
    return 0


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    sys.exit(main())
