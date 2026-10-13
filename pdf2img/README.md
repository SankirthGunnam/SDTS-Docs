# pdf2img

Render PDF pages to PNG images (for OCR or vision-model conversion to Markdown).

## Install

```bash
pip install -r requirements.txt
```

## Usage

Single file:

```bash
python pdf_to_images.py input.pdf -o out
```

Folder of PDFs:

```bash
python pdf_to_images.py ./pdfs -o out
```

Custom DPI:

```bash
python pdf_to_images.py input.pdf -o out --dpi 300
```

Password-protected PDF:

```bash
python pdf_to_images.py secret.pdf -o out --password YOUR_PASSWORD
```

Custom output directory (`-o`):

```bash
python pdf_to_images.py input.pdf -o /path/to/out
```

## Output layout

```
out/<pdf name>/page_0001.png
out/<pdf name>/page_0002.png
...
```

## Authorization

Only process PDFs you are authorized to convert.
