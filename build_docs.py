#!/usr/bin/env python3
"""
Convert Markdown files to HTML using a reusable Jinja template.
Output mirrors the docs/ folder hierarchy; all links and images use relative paths.
"""

import argparse
import os
import re
from pathlib import Path
import sys
from typing import Dict, List

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


def extract_toc_tokens(toc_tokens):
    """Flatten toc_tokens from markdown extension into a list of {level, id, name}."""
    entries = []
    for token in toc_tokens:
        entries.append({
            "level": token.get("level", 1),
            "id": token.get("id", ""),
            "name": token.get("name", ""),
        })
        entries.extend(extract_toc_tokens(token.get("children", [])))
    return entries


def _output_path_for_md(md_path: Path, input_dir: Path, output_dir: Path) -> Path:
    """Path where this .md file's HTML should be written (mirrors hierarchy)."""
    rel = md_path.relative_to(input_dir)
    return output_dir / rel.with_suffix(".html")


def _fix_content_paths(
    content_html: str,
    output_path: Path,
    output_dir: Path,
    nav_links: Dict[str, str],
) -> str:
    """Rewrite image src and in-content hrefs to be relative to output_path."""
    # Depth from output_dir root (0 = file in output_dir, 1 = one subdir, etc.)
    try:
        rel_parts = output_path.relative_to(output_dir).parts
        depth = len(rel_parts) - 1
    except ValueError:
        depth = 0
    image_prefix = "../" * depth if depth > 0 else ""

    # Fix img src="images/..." -> src="../.../images/..."
    content_html = re.sub(r'src="images/', r'src="' + image_prefix + 'images/', content_html)

    # Fix in-content links (e.g. Back to Home href="home.html")
    for name, href in nav_links.items():
        content_html = content_html.replace('href="' + name + '"', 'href="' + href + '"')

    return content_html


def md_to_html(
    md_path: Path,
    input_dir: Path,
    output_dir: Path,
    env: Environment,
    filename_to_rel_path: Dict[str, str],
    output_path: Path,
) -> Path:
    """Convert one markdown file to HTML and write to output_path (hierarchy preserved)."""
    md_path = md_path.resolve()
    output_dir = output_dir.resolve()
    text = md_path.read_text(encoding="utf-8")

    md_instance = markdown.Markdown(extensions=["toc", "fenced_code", "tables"])
    content_html = md_instance.convert(text)
    toc_tokens = getattr(md_instance, "toc_tokens", [])
    toc_entries = extract_toc_tokens(toc_tokens)

    title = md_path.stem.replace("-", " ").replace("_", " ").title()
    if toc_tokens and toc_tokens[0].get("level") == 1:
        title = toc_tokens[0].get("name", title)

    current_dir = output_path.parent
    nav_links = {}
    for name, rel_path in filename_to_rel_path.items():
        target = (output_dir / rel_path).resolve()
        cur = current_dir.resolve()
        href = os.path.relpath(target, cur)
        nav_links[name] = href.replace("\\", "/")

    content_html = _fix_content_paths(content_html, output_path, output_dir, nav_links)

    current_page_key = output_path.name

    template = env.get_template("doc.html")
    html = template.render(
        title=title,
        content=content_html,
        nav_links=nav_links,
        current_page_key=current_page_key,
        toc_entries=toc_entries,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def collect_md_files(path: Path) -> List[Path]:
    """Collect .md files from a file or directory (recursive for dirs), sorted by path."""
    path = path.resolve()
    if path.is_file():
        return [path] if path.suffix.lower() == ".md" else []
    if path.is_dir():
        return sorted(path.rglob("*.md"), key=lambda p: str(p))
    return []


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to HTML with left nav, content, and right TOC."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Markdown file or directory containing .md files",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output file or directory (default: same as input, with .html)",
    )
    parser.add_argument(
        "-t", "--templates",
        type=Path,
        default=Path(__file__).parent / "templates",
        help="Directory containing Jinja templates (default: ./templates)",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()
    if not input_path.exists():
        print(f"Error: input does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    md_files = collect_md_files(input_path)
    if not md_files:
        print("Error: no Markdown files found.", file=sys.stderr)
        sys.exit(1)

    if args.output is not None:
        output_dir = args.output.resolve()
        if output_dir.suffix == ".html":
            output_dir = output_dir.parent
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
    else:
        if input_path.is_file():
            output_dir = input_path.parent
        else:
            output_dir = input_path / "static-docs"
            output_dir.mkdir(parents=True, exist_ok=True)

    input_dir = input_path if input_path.is_dir() else input_path.parent

    # Map filename (e.g. "home.html") -> path relative to output_dir (e.g. "1-rf-board-bring-up/home.html")
    filename_to_rel_path = {}
    for md_path in md_files:
        out_path = _output_path_for_md(md_path, input_dir, output_dir)
        name = out_path.name
        rel = out_path.relative_to(output_dir)
        filename_to_rel_path[name] = str(rel).replace("\\", "/")

    template_dir = args.templates.resolve()
    if not template_dir.is_dir():
        print(f"Error: templates directory not found: {template_dir}", file=sys.stderr)
        sys.exit(1)

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(("html", "xml")),
    )

    for md_path in md_files:
        output_path = _output_path_for_md(md_path, input_dir, output_dir)
        out_path = md_to_html(
            md_path,
            input_dir,
            output_dir,
            env,
            filename_to_rel_path,
            output_path,
        )
        print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()
