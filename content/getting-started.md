# Getting Started with SDTS

Follow these steps to convert your Markdown files to HTML.

## Prerequisites

- Python 3.8 or later
- pip (or your preferred package manager)

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Running the Build

Convert a single Markdown file:

```bash
python build_docs.py content/introduction.md
```

Convert all Markdown files in a directory:

```bash
python build_docs.py content -o output
```

## Output Layout

The generated HTML includes:

1. **Left sidebar** – Links to all documentation pages
2. **Center** – Rendered Markdown content
3. **Right sidebar** – Table of contents for the current page

## Next Steps

- Add your own Markdown files under `content/`
- Customize `templates/doc.html` to match your branding
- Use the same script for Confluence-exported Markdown
