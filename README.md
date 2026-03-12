# SDTS-Docs

Convert Markdown (e.g. exported from Confluence) to HTML documentation with a reusable Jinja template. Output includes **left sidebar** (site navigation), **center content**, and **right sidebar** (on-page table of contents).

## Setup

```bash
pip install -r requirements.txt
```

## Usage

**Convert a single Markdown file:**

```bash
python build_docs.py content/introduction.md
```

**Convert all Markdown files in a directory** (recommended; builds full left nav from all pages):

```bash
python build_docs.py docs -o static-docs
```

**Options:**

- `input` – Markdown file or directory containing `.md` files (recursive)
- `-o, --output` – Output directory (default: same as input, or `static-docs/` when input is a directory)
- `-t, --templates` – Path to Jinja templates (default: `templates/`)

## Documentation viewer (PyQt)

To view the generated docs in a simple Qt browser (no localhost):

```bash
python doc_viewer.py
```

The viewer loads `static-docs/home.html` and displays it; clicking sidebar links opens other pages. All content is loaded from local files under `static-docs/`.

**Documentation launcher** (text with links that open docs):

```bash
python doc_launcher.py
```

Opens a window with sample text and hyperlinks; clicking a link opens that page in the bottom dock (in-app).

## Images

Keep images in **static-docs/images/**. In Markdown, reference them with paths relative to the generated HTML, e.g. `![Description](images/sample1.jpg)`. Rebuild with `build_docs.py` after adding or changing images.

## Project layout

- `build_docs.py` – Script that converts Markdown to HTML
- `doc_viewer.py` – PyQt app to browse static HTML docs (no server)
- `doc_launcher.py` – PyQt app with text edit and links that open doc pages in the browser
- `templates/doc.html` – Reusable Jinja template (left nav, center, right TOC)
- `docs/` – Markdown source (hierarchical; matches nav tree)
- `static-docs/` – Generated HTML and assets; **mirrors the docs/ hierarchy** (e.g. `static-docs/1-rf-board-bring-up/home.html`, `static-docs/4-laboratory/laboratory.html`). All links and images use **relative paths** so pages work from any folder. Images live in `static-docs/images/`.

## Template

Edit `templates/doc.html` to change styling, branding, or layout. The same template is used for every page. Variables passed to the template: `title`, `content`, `pages`, `current_path`, `toc_entries`.
