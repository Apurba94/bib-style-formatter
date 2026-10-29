"""Command-line interface for bib-style-formatter."""
import argparse
import sys

from .core import STYLES, format_bibliography, parse_bibtex


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bib-style-formatter", description="Format BibTeX as plain-text references.")
    ap.add_argument("bibfile")
    ap.add_argument("-s", "--style", choices=STYLES, default="apa")
    ap.add_argument("--plain", action="store_true", help="no Markdown italics")
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    with open(args.bibfile, encoding="utf-8") as fh:
        refs = format_bibliography(parse_bibtex(fh.read()), args.style, markdown=not args.plain)
    text = "\n\n".join(refs) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0
