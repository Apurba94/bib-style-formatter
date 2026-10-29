"""Render BibTeX entries as APA, IEEE, Vancouver or Harvard references."""
from .core import parse_bibtex, parse_names, format_reference, format_bibliography, STYLES

__version__ = "0.1.0"
__all__ = ["parse_bibtex", "parse_names", "format_reference", "format_bibliography", "STYLES"]
