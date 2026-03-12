# SDTS Reference

Reference information for the SDTS documentation builder.

## Command-Line Options

| Option | Description |
|--------|-------------|
| `input` | Markdown file or directory |
| `-o, --output` | Output file or directory |
| `-t, --templates` | Path to Jinja templates directory |

## Template Variables

The `doc.html` Jinja template receives:

- **title** – Page title (from first H1 or filename)
- **content** – Rendered HTML from Markdown
- **pages** – List of `{title, path}` for left navigation
- **current_path** – Current page filename (for highlighting active nav)
- **toc_entries** – List of `{level, id, name}` for right-side TOC

## File Structure

A typical project layout:

```
SDTS-Docs/
  build_docs.py
  requirements.txt
  templates/
    doc.html
  content/
    introduction.md
    getting-started.md
    reference.md
  output/          # or alongside each .md
    introduction.html
    getting-started.html
    reference.html
```

## Customization

Edit `templates/doc.html` to change styles, add a logo, or adjust the three-column layout. The template is reused for every generated page.
