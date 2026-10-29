"""BibTeX parsing, name handling and four reference styles."""
import re

_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,")
_LATEX_ACCENTS = {"\\'e": "\u00e9", "\\'a": "\u00e1", "\\'o": "\u00f3", "\\'i": "\u00ed", "\\'u": "\u00fa",
                  '\\"o': "\u00f6", '\\"u': "\u00fc", '\\"a': "\u00e4", "\\`e": "\u00e8", "\\`a": "\u00e0",
                  "\\~n": "\u00f1", "\\c{c}": "\u00e7", "\\ss": "\u00df", "\\&": "&"}


def clean(value):
    """Convert common LaTeX accents and strip braces."""
    for k, v in _LATEX_ACCENTS.items():
        value = value.replace("{" + k + "}", v).replace(k, v)
    value = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", value)
    return " ".join(value.replace("{", "").replace("}", "").replace("--", "\u2013").split())


def parse_bibtex(text):
    entries = []
    for m in _ENTRY.finditer(text):
        if m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        i, depth = text.index("{", m.start()), 0
        for j in range(i, len(text)):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            if depth == 0:
                break
        body = text[m.end():j]
        fields = {}
        for fm in re.finditer(r"([\w-]+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\"[^\"]*\"|\d+)", body):
            v = fm.group(2)
            fields[fm.group(1).lower()] = clean(v[1:-1] if v[0] in "{\"" else v)
        entries.append({"type": m.group(1).lower(), "key": m.group(2), "fields": fields})
    return entries


def parse_names(author_field):
    """Split a BibTeX author field into (last, [given names]) tuples."""
    people = []
    for raw in re.split(r"\s+and\s+", author_field.strip()):
        raw = raw.strip()
        if not raw:
            continue
        if raw.lower() == "others":
            people.append(("others", []))
        elif "," in raw:
            last, given = raw.split(",", 1)
            people.append((last.strip(), given.split()))
        else:
            parts = raw.split()
            idx = next((k for k, p in enumerate(parts[:-1]) if p[:1].islower()), len(parts) - 1)
            people.append((" ".join(parts[idx:]), parts[:idx]))
    return people


def initials(given, sep=". ", end="."):
    out = []
    for g in given:
        # hyphenated given names keep the hyphen: Jean-Paul -> J.-P.
        out.append("-".join(p[0] + "." for p in g.split("-") if p) if "-" in g else g[0])
    if sep == ". ":
        return " ".join(o if o.endswith(".") else o + "." for o in out)
    return "".join(o.replace(".", "").replace("-", "") for o in out)


def _join(items, last_sep, sep=", "):
    if len(items) <= 1:
        return "".join(items)
    return sep.join(items[:-1]) + last_sep + items[-1]


def _authors(people, style):
    etal = people and people[-1][0] == "others"
    people = [p for p in people if p[0] != "others"]
    if style == "apa":
        names = ["%s, %s" % (l, initials(g)) if g else l for l, g in people]
        if len(names) > 20:
            names = names[:19] + ["... " + names[-1]]
            return ", ".join(names)
        return _join(names, ", & ") + (", et al." if etal else "") if len(names) > 1 else (names[0] if names else "")
    if style == "ieee":
        names = ["%s %s" % (initials(g), l) if g else l for l, g in people]
        if len(names) > 6 or etal:
            return names[0] + " et al."
        return _join(names, ", and ") if len(names) > 2 else " and ".join(names)
    if style == "vancouver":
        names = ["%s %s" % (l, initials(g, sep="")) if g else l for l, g in people]
        if len(names) > 6:
            names = names[:6] + ["et al"]
        return ", ".join(names)
    if style == "harvard":
        names = ["%s, %s" % (l, initials(g)) if g else l for l, g in people]
        if len(names) > 3:
            return names[0] + " et al."
        return _join(names, " and ")
    raise ValueError(style)


def _end(s, ch="."):
    s = s.rstrip()
    return s if s.endswith((".", "?", "!")) else s + ch


def format_reference(entry, style="apa"):
    """Format one parsed entry in the given style (apa, ieee, vancouver, harvard)."""
    if style not in STYLES:
        raise ValueError("unknown style %r; choose from %s" % (style, ", ".join(STYLES)))
    f = entry["fields"]
    t = entry["type"]
    people = parse_names(f.get("author") or f.get("editor", ""))
    au = _authors(people, style) if people else ""
    year = f.get("year", "n.d.")
    title = f.get("title", "")
    venue = f.get("journal") or f.get("booktitle") or ""
    vol, num, pages = f.get("volume", ""), f.get("number", ""), f.get("pages", "")
    doi = f.get("doi", "")
    pub = f.get("publisher", "")

    if style == "apa":
        s = "%s (%s). %s" % (_end(au, "") if au else title, year, _end(title) if au else "")
        if t == "article":
            s += " *%s*" % venue + (", *%s*" % vol if vol else "") + ("(%s)" % num if num else "") + (", %s" % pages if pages else "") + "."
        elif t in ("inproceedings", "incollection", "conference"):
            s += " In *%s*" % venue + (" (pp. %s)" % pages if pages else "") + "." + (" %s." % pub if pub else "")
        elif t == "book":
            s = s.rstrip(".").rstrip()
            s = "%s (%s). *%s*. %s" % (au, year, title, _end(pub) if pub else "")
        elif pub:
            s += " %s." % pub
        if doi:
            s += " https://doi.org/%s" % doi
        return " ".join(s.split())
    if style == "ieee":
        s = "%s, \u201c%s,\u201d " % (au, title) if t != "book" else "%s, *%s*. " % (au, title)
        if t == "article":
            s += "*%s*" % venue + (", vol. %s" % vol if vol else "") + (", no. %s" % num if num else "") + (", pp. %s" % pages if pages else "") + ", %s." % year
        elif t in ("inproceedings", "conference", "incollection"):
            s += "in *%s*, %s" % (venue, year) + (", pp. %s" % pages if pages else "") + "."
        else:
            s += (pub + ", " if pub else "") + year + "."
        if doi:
            s += " doi: %s." % doi
        return " ".join(s.split())
    if style == "vancouver":
        s = "%s. %s. " % (au, _end(title, "").rstrip("."))
        if t == "article":
            s += "%s. %s" % (venue, year) + (";%s" % vol if vol else "") + ("(%s)" % num if num else "") + (":%s" % pages.replace("\u2013", "-") if pages else "") + "."
        elif t == "book":
            s += "%s; %s." % (pub, year) if pub else "%s." % year
        else:
            s += "In: %s; %s" % (venue, year) + (". p. %s" % pages.replace("\u2013", "-") if pages else "") + "."
        if doi:
            s += " doi:%s" % doi
        return " ".join(s.split())
    # harvard
    s = "%s (%s) " % (au, year)
    if t == "article":
        s += "'%s', *%s*" % (title, venue) + (", %s" % vol if vol else "") + ("(%s)" % num if num else "") + (", pp. %s" % pages if pages else "") + "."
    elif t == "book":
        s += "*%s*. %s" % (title, _end(pub) if pub else "")
    else:
        s += "'%s', in *%s*" % (title, venue) + (", pp. %s" % pages if pages else "") + "."
    if doi:
        s += " doi:%s." % doi
    return " ".join(s.split())


STYLES = ("apa", "ieee", "vancouver", "harvard")


def _sort_key(e):
    people = parse_names(e["fields"].get("author", ""))
    return ((people[0][0].lower() if people else e["fields"].get("title", "").lower()), e["fields"].get("year", ""))


def format_bibliography(entries, style="apa", markdown=True):
    """Format a whole bibliography: alphabetical for APA/Harvard, numbered in input order for IEEE/Vancouver."""
    refs = []
    if style in ("ieee", "vancouver"):
        for i, e in enumerate(entries, 1):
            refs.append(("[%d] " if style == "ieee" else "%d. ") % i + format_reference(e, style))
    else:
        refs = [format_reference(e, style) for e in sorted(entries, key=_sort_key)]
    if not markdown:
        refs = [r.replace("*", "") for r in refs]
    return refs
