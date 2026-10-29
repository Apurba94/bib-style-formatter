# bib-style-formatter

**Turn a `.bib` file into formatted APA 7, IEEE, Vancouver or Harvard reference lists,
without LaTeX, Word or a reference manager.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Grant applications, reports, CVs, posters and e-mails need formatted references, but the
bibliography lives in BibTeX. Running LaTeX just to copy a reference list is clumsy, and pasting into
Word reference managers loses control. This tool formats references directly from BibTeX.

## Features

- APA 7 (alphabetical, `&`, DOI as URL), IEEE (numbered, "et al." beyond 6), Vancouver
  (numbered, compact initials, up to 6 authors) and Harvard
- Handles `Last, First` and `First von Last` names, hyphenated initials, `and others`
- Converts common LaTeX accents and `--` to an en dash
- Markdown italics (default) or plain text

## Usage

```bash
pip install .
bib-style-formatter refs.bib -s apa
bib-style-formatter refs.bib -s ieee --plain -o references.txt
```

```python
from bib_style_formatter import parse_bibtex, format_bibliography
print("\n".join(format_bibliography(parse_bibtex(open("refs.bib").read()), "vancouver")))
```

Styles cover articles, books and proceedings/chapters; check the output against your target
journal's guide for edge cases.

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
