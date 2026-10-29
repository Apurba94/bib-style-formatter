import unittest

from bib_style_formatter.core import format_bibliography, format_reference, initials, parse_bibtex, parse_names

BIB = r"""
@article{w,
  author = {Watson, James D. and Crick, Francis H. C.},
  title = {Molecular Structure of Nucleic Acids},
  journal = {Nature},
  year = {1953},
  volume = {171},
  number = {4356},
  pages = {737--738},
  doi = {10.1038/171737a0}
}
@book{k,
  author = {Donald E. Knuth},
  title = {The Art of Computer Programming},
  publisher = {Addison-Wesley},
  year = {1968}
}
@inproceedings{v,
  author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and others},
  title = {Attention is All you Need},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2017},
  pages = {5998--6008}
}
"""
E = {e["key"]: e for e in parse_bibtex(BIB)}


class NameTests(unittest.TestCase):
    def test_parse_names_formats(self):
        self.assertEqual(parse_names("Knuth, Donald E. and Ludwig van Beethoven"),
                         [("Knuth", ["Donald", "E."]), ("van Beethoven", ["Ludwig"])])

    def test_initials(self):
        self.assertEqual(initials(["Jean-Paul", "Charles"]), "J.-P. C.")
        self.assertEqual(initials(["Francis", "H.", "C."], sep=""), "FHC")

    def test_latex_accents_cleaned(self):
        e = parse_bibtex(r"@misc{a, author={Erd{\H o}s, P and G{\"o}del, Kurt}, title={Caf{\'e}}}")[0]
        self.assertIn("G\u00f6del", e["fields"]["author"])
        self.assertEqual(e["fields"]["title"], "Caf\u00e9")


class StyleTests(unittest.TestCase):
    def test_apa_article(self):
        self.assertEqual(format_reference(E["w"], "apa"),
                         "Watson, J. D., & Crick, F. H. C. (1953). Molecular Structure of Nucleic Acids. "
                         "*Nature*, *171*(4356), 737\u2013738. https://doi.org/10.1038/171737a0")

    def test_ieee_article_and_etal(self):
        self.assertEqual(format_reference(E["w"], "ieee"),
                         "J. D. Watson and F. H. C. Crick, \u201cMolecular Structure of Nucleic Acids,\u201d *Nature*, "
                         "vol. 171, no. 4356, pp. 737\u2013738, 1953. doi: 10.1038/171737a0.")
        self.assertTrue(format_reference(E["v"], "ieee").startswith("A. Vaswani et al., "))

    def test_vancouver(self):
        self.assertEqual(format_reference(E["w"], "vancouver"),
                         "Watson JD, Crick FHC. Molecular Structure of Nucleic Acids. Nature. 1953;171(4356):737-738. "
                         "doi:10.1038/171737a0")

    def test_harvard_book(self):
        self.assertEqual(format_reference(E["k"], "harvard"),
                         "Knuth, D. E. (1968) *The Art of Computer Programming*. Addison-Wesley.")

    def test_apa_book_and_proceedings(self):
        self.assertEqual(format_reference(E["k"], "apa"),
                         "Knuth, D. E. (1968). *The Art of Computer Programming*. Addison-Wesley.")
        self.assertIn("In *Advances in Neural Information Processing Systems* (pp. 5998\u20136008).",
                      format_reference(E["v"], "apa"))

    def test_bibliography_ordering(self):
        apa = format_bibliography(list(E.values()), "apa", markdown=False)
        self.assertTrue(apa[0].startswith("Knuth"))
        self.assertNotIn("*", apa[0])
        ieee = format_bibliography(list(E.values()), "ieee")
        self.assertTrue(ieee[0].startswith("[1] J. D. Watson"))

    def test_unknown_style(self):
        with self.assertRaises(ValueError):
            format_reference(E["w"], "chicago")


if __name__ == "__main__":
    unittest.main()
