#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
md2pdf.py — Markdown -> styled HTML -> Chromium page.pdf() publishing pipeline
for consulting deliverables.

No LaTeX, no pandoc. Requires: markdown, pymdown-extensions, beautifulsoup4,
playwright (MS Edge channel), pymupdf.

Key capabilities
----------------
* Section selection driven by config (include/exclude H2 and H3 by number),
  so one Markdown source yields several deliverables without editing it.
* Cover page, generated TOC **with real page numbers**, running header
  (title left / current section right), footer (page X of Y).
* Wide-table auto-fit: every table is measured (column count + per-column
  content width against the page's character budget) and assigned a density
  tier, so 7-12 column tables shrink to fit instead of clipping.
* Page-break discipline: no split table rows, no orphaned headings, decision
  cards kept whole, repeating table header rows.
* Figures: picks up diagrams/<prefix>_fig<N>_*.svg automatically, one per
  landscape page, fitted, with a caption.

How the TOC page numbers are solved
-----------------------------------
Chromium has no paged-media TOC. Each heading carries a zero-width,
transparent marker span (`@@MKnn@@`) that is still painted into the PDF
content stream, so PyMuPDF can report exactly which page it landed on.
The document is rendered, the markers are located, the TOC page numbers are
substituted, and the document is re-rendered. Because TOC page-number cells
are fixed-width tabular figures, substituting them cannot reflow anything;
the loop nevertheless iterates to a fixed point (the map is recomputed from
the re-rendered PDF and compared) and only stops when the numbers printed in
the TOC are the numbers the PDF actually has.

Usage
-----
    python md2pdf.py --source CASE.md --out OUT.pdf --page A3 --landscape \
        --title "..." --client "..." [--config-json '{...}']

Usually driven from build.py instead.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import re
import sys
import unicodedata

import fitz  # PyMuPDF
import markdown
from bs4 import BeautifulSoup, Comment, NavigableString
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_CSS = HERE / "style.css"

# --------------------------------------------------------------------------
# Page geometry
# --------------------------------------------------------------------------
# name -> (portrait width mm, portrait height mm)
PAGE_SIZES = {
    "A5": (148.0, 210.0),
    "A4": (210.0, 297.0),
    "A3": (297.0, 420.0),
    "A2": (420.0, 594.0),
    "LETTER": (215.9, 279.4),
    "TABLOID": (279.4, 431.8),
}

MM_PER_PT = 25.4 / 72.0


class Geometry:
    """Resolved page geometry plus the derived typographic scale."""

    def __init__(self, page="A4", landscape=False, margins=None, columns=None,
                 body_pt=None, leading=None, section_page_break=True):
        key = page.upper()
        if key not in PAGE_SIZES:
            raise SystemExit(f"unknown page size {page!r}; known: {sorted(PAGE_SIZES)}")
        w, h = PAGE_SIZES[key]
        self.page_name = key
        self.landscape = bool(landscape)
        self.page_w, self.page_h = (h, w) if landscape else (w, h)

        default_m = {"top": 17.0, "bottom": 15.0, "left": 15.0, "right": 15.0}
        if self.page_w >= 400:  # A3 landscape and wider
            default_m = {"top": 18.0, "bottom": 16.0, "left": 17.0, "right": 17.0}
        self.margin = dict(default_m)
        if margins:
            self.margin.update(margins)

        self.content_w = self.page_w - self.margin["left"] - self.margin["right"]
        self.content_h = self.page_h - self.margin["top"] - self.margin["bottom"]

        # Column count: keep the text measure between ~85 and ~115mm.
        if columns:
            self.columns = int(columns)
        else:
            self.columns = max(1, min(3, round(self.content_w / 105.0)))
        self.column_gap = 11.0 if self.columns > 1 else 0.0
        self.measure = (self.content_w - self.column_gap * (self.columns - 1)) / self.columns

        # Type scale, tuned to the measure.
        if body_pt:
            self.body_pt = float(body_pt)
        elif self.measure >= 150:
            self.body_pt = 10.2
        elif self.measure >= 120:
            self.body_pt = 9.8
        else:
            self.body_pt = 9.3
        self.leading = float(leading) if leading else 1.42
        self.section_page_break = bool(section_page_break)
        self.table_pt = round(self.body_pt * 0.895, 2)
        self.h2_pt = round(self.body_pt * 1.86, 2)
        self.h3_pt = round(self.body_pt * 1.26, 2)
        self.h4_pt = round(self.body_pt * 1.06, 2)
        self.cover_title_pt = round(self.body_pt * 3.5, 2)
        self.cover_sub_pt = round(self.body_pt * 1.45, 2)
        self.toc_columns = max(1, self.columns)
        self.fig_caption_h = 17.0 if self.content_h < 200 else 20.0

        # How many characters of table text fit across the full content width
        # at the base table size. ~0.50 em average advance for this family.
        self.table_char_budget = self.content_w / (self.table_pt * MM_PER_PT * 0.50)

    def pdf_margins(self):
        return {k: f"{v}mm" for k, v in self.margin.items()}

    def css_vars(self):
        return f""":root {{
  --leading: {self.leading};
  --section-break: {'page' if self.section_page_break else 'auto'};
  --content-w: {self.content_w:.2f}mm;
  --content-h: {self.content_h:.2f}mm;
  --measure: {self.measure:.2f}mm;
  --body-columns: {self.columns};
  --toc-columns: {self.toc_columns};
  --column-gap: {self.column_gap:.1f}mm;
  --body-size: {self.body_pt}pt;
  --table-size: {self.table_pt}pt;
  --h2-size: {self.h2_pt}pt;
  --h3-size: {self.h3_pt}pt;
  --h4-size: {self.h4_pt}pt;
  --cover-title-size: {self.cover_title_pt}pt;
  --cover-sub-size: {self.cover_sub_pt}pt;
  --fig-caption-h: {self.fig_caption_h:.1f}mm;
}}"""

    def describe(self):
        o = "landscape" if self.landscape else "portrait"
        return (f"{self.page_name} {o} {self.page_w:.0f}x{self.page_h:.0f}mm, "
                f"content {self.content_w:.0f}x{self.content_h:.0f}mm, "
                f"{self.columns} col (measure {self.measure:.0f}mm), "
                f"body {self.body_pt}pt, table budget {self.table_char_budget:.0f} chars")


# --------------------------------------------------------------------------
# Markdown structure: split into H2 sections with H3 subsections
# --------------------------------------------------------------------------
H2_RE = re.compile(r"^##\s+(?!#)(.*)$")
H3_RE = re.compile(r"^###\s+(?!#)(.*)$")
FENCE_RE = re.compile(r"^(```|~~~)")


def split_sections(md_text: str):
    """-> (front_matter_lines, [ {title, key, intro:[lines], subs:[{title,key,lines}]} ])"""
    lines = md_text.split("\n")
    front, sections = [], []
    cur = None
    cur_sub = None
    in_fence = False

    for line in lines:
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
        if not in_fence:
            m2 = H2_RE.match(line)
            if m2:
                cur = {"title": m2.group(1).strip(), "key": heading_key(m2.group(1)),
                       "intro": [], "subs": []}
                sections.append(cur)
                cur_sub = None
                continue
            m3 = H3_RE.match(line)
            if m3 and cur is not None:
                cur_sub = {"title": m3.group(1).strip(), "key": heading_key(m3.group(1)),
                           "lines": []}
                cur["subs"].append(cur_sub)
                continue
        if cur is None:
            front.append(line)
        elif cur_sub is None:
            cur["intro"].append(line)
        else:
            cur_sub["lines"].append(line)
    return front, sections


def heading_key(title: str) -> str:
    """Leading identifier of a heading: '5.3', '12', 'UC-4', else '' ."""
    t = strip_md(title).strip()
    m = re.match(r"^(\d+(?:\.\d+)*)\s*[.)]?\s", t + " ")
    if m:
        return m.group(1)
    m = re.match(r"^([A-Z]{1,4}-\d+)", t)
    if m:
        return m.group(1)
    return ""


def strip_md(s: str) -> str:
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]*)\*", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s.strip()


def key_exact(pattern: str, key: str, title: str) -> bool:
    """Strict heading match: '5.' matches section 5 but NOT 5.1."""
    p = (pattern or "").rstrip(".")
    if key and key == p:
        return True
    return strip_md(title).lower().startswith(p.lower() + " ") or         strip_md(title).lower() == p.lower()


def key_matches(pattern: str, key: str, title: str) -> bool:
    if pattern in ("*", "all"):
        return True
    p = pattern.rstrip(".")
    if key:
        if key == p:
            return True
        if key.startswith(p + "."):
            return True
    return strip_md(title).lower().startswith(pattern.lower())


def select_markdown(md_text: str, include, drop_front_sections=(), figures_after=None,
                    drop_front_matter=False):
    """Assemble the Markdown for one deliverable.

    include: None  -> everything
             list of entries:
               "3."                      -> whole H2 section 3
               {"h2": "5.", "h3": ["5.1","5.8"]}  -> intro + those H3s
               {"h2": "2.", "h3": ["2.1"], "intro": False}
    Returns (markdown_text, [(level, title) ...]) ; the figures placeholder
    paragraph `[[FIGURES]]` is inserted after `figures_after`.
    """
    front, sections = split_sections(md_text)
    out = [] if drop_front_matter else list(front)

    def emit_figs_if(keyish):
        if figures_after and key_matches(figures_after, keyish[0], keyish[1]):
            out.extend(["", "[[FIGURES]]", ""])
            return True
        return False

    if include is None:
        spec = [{"h2": s["key"] or s["title"], "h3": "*"} for s in sections
                if strip_md(s["title"]) not in drop_front_sections]
    else:
        spec = []
        for e in include:
            spec.append({"h2": e, "h3": "*"} if isinstance(e, str) else dict(e))

    placed = False
    for item in spec:
        pat = item["h2"]
        sec = next((s for s in sections if key_matches(pat, s["key"], s["title"])), None)
        if sec is None:
            print(f"  ! include pattern {pat!r} matched no H2 section", file=sys.stderr)
            continue
        out.append("")
        out.append("## " + sec["title"])
        if item.get("intro", True):
            out.extend(sec["intro"])
        h3spec = item.get("h3", "*")
        for sub in sec["subs"]:
            if h3spec in ("*", "all"):
                keep = True
            elif not h3spec:
                keep = False
            else:
                keep = any(key_matches(p, sub["key"], sub["title"]) for p in h3spec)
            if not keep:
                continue
            out.append("### " + sub["title"])
            out.extend(sub["lines"])
            if figures_after and key_exact(figures_after, sub["key"], sub["title"]):
                out.extend(["", "[[FIGURES]]", ""]); placed = True
        if figures_after and not placed and key_exact(figures_after, sec["key"], sec["title"]):
            out.extend(["", "[[FIGURES]]", ""]); placed = True

    if figures_after and not placed:
        out.extend(["", "[[FIGURES]]", ""])
    return "\n".join(out)


# --------------------------------------------------------------------------
# Markdown -> HTML
# --------------------------------------------------------------------------
MD_EXTENSIONS = [
    "tables", "fenced_code", "attr_list", "def_list", "abbr",
    "sane_lists", "md_in_html", "footnotes",
    "pymdownx.betterem", "pymdownx.caret", "pymdownx.tilde",
    "pymdownx.smartsymbols", "pymdownx.escapeall",
]
MD_CONFIG = {"pymdownx.escapeall": {"hardbreak": False, "nbsp": True}}


def slugify(text, used=None):
    s = unicodedata.normalize("NFKD", strip_md(text))
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s) or "section"
    if used is not None:
        base, n = s, 2
        while s in used:
            s = f"{base}-{n}"; n += 1
        used.add(s)
    return s


# --------------------------------------------------------------------------
# Table auto-fit
# --------------------------------------------------------------------------
TIERS = [("", 1.00), ("t-med", 0.94), ("t-wide", 0.87), ("t-xwide", 0.79), ("t-xxwide", 0.70)]


def fit_table(table, budget, report):
    """Measure a table and assign a density class. Returns a report dict."""
    rows = table.find_all("tr")
    if not rows:
        return None
    head = table.find("thead")
    headers = [c.get_text(" ", strip=True) for c in (head.find_all(["th", "td"]) if head else rows[0].find_all(["th", "td"]))]
    ncols = max(len(r.find_all(["th", "td"])) for r in rows)

    # per-column widest cell (in characters), which is what drives wrapping
    widths = [0] * ncols
    body_rows = 0
    for r in rows:
        cells = r.find_all(["th", "td"])
        if r.find("td"):
            body_rows += 1
        for i, c in enumerate(cells[:ncols]):
            widths[i] = max(widths[i], len(c.get_text(" ", strip=True)))
    natural = sum(widths) + ncols * 3  # + padding/borders expressed in chars

    pressure = natural / budget if budget else 0.0
    # Column-count floor (hard requirement: >7 columns must be denser)
    if ncols >= 10:
        tier_i = 4
    elif ncols >= 8:
        tier_i = 3
    elif ncols == 7:
        tier_i = 2
    elif ncols == 6:
        tier_i = 1
    else:
        tier_i = 0
    # Content-pressure floor: aim for <= ~2.3 wrapped lines in the widest cell
    if pressure > 3.4:
        tier_i = max(tier_i, 4)
    elif pressure > 2.6:
        tier_i = max(tier_i, 3)
    elif pressure > 1.9:
        tier_i = max(tier_i, 2)
    elif pressure > 1.35:
        tier_i = max(tier_i, 1)

    cls, factor = TIERS[tier_i]
    classes = table.get("class", [])
    if cls:
        classes.append(cls)
    # first column acts as a row header when the header's first cell is blank
    if headers and not headers[0]:
        classes.append("rowhead")
    # Markdown needs a header row even when the author wanted none ("| | |").
    # An empty navy band reads as a rendering fault, so drop it.
    if head is not None and headers and not any(h.strip() for h in headers):
        head.decompose()
        classes.append("noheader")
    table["class"] = classes

    wrap = table.parent
    if body_rows > 7 and wrap is not None and "table-wrap" in (wrap.get("class") or []):
        wrap["class"] = wrap.get("class", []) + ["tall"]

    rep = {"ncols": ncols, "rows": body_rows, "natural_chars": natural,
           "pressure": round(pressure, 2), "tier": cls or "base",
           "effective_chars": round(budget / factor),
           "fits": natural <= budget / factor * 2.4,
           "headers": headers[:12]}
    report.append(rep)
    return rep


# --------------------------------------------------------------------------
# HTML assembly
# --------------------------------------------------------------------------
def transform_body(html, geo, report):
    soup = BeautifulSoup(html, "html.parser")
    used = set()
    headings = []  # (level, title, id, marker)

    for el in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        # headings inside a blockquote callout are decoration, not structure
        if el.find_parent("blockquote"):
            continue
        lvl = int(el.name[1])
        if lvl > 3:
            continue
        title = el.get_text(" ", strip=True)
        hid = slugify(title, used)
        el["id"] = hid
        idx = len(headings)
        marker = f"@@MK{idx:03d}@@"
        span = soup.new_tag("span")
        span["class"] = ["pgmark"]
        span.string = marker
        el.append(span)
        headings.append({"level": lvl, "title": title, "id": hid,
                         "marker": marker, "key": heading_key(title)})

    # blockquotes -> decision cards / illustrative note / generic callout
    for bq in soup.find_all("blockquote"):
        txt = bq.get_text(" ", strip=True)
        classes = bq.get("class", [])
        m = re.match(r"^DECISION\s+([A-Z]{1,3}-\d+)", txt)
        if m:
            classes.append("decision")
            first_strong = bq.find("strong")
            if first_strong:
                tag = soup.new_tag("span")
                tag["class"] = ["decision-tag"]
                tag.string = m.group(1)
                # strip the "DECISION D-xx — " prefix from the bold lead-in
                lead = first_strong.get_text()
                lead = re.sub(r"^DECISION\s+[A-Z]{1,3}-\d+\s*[—:-]\s*", "", lead)
                first_strong.string = lead
                first_strong["class"] = first_strong.get("class", []) + ["decision-head"]
                first_strong.insert_before(tag)
            for st in bq.find_all("strong"):
                if st.get_text(strip=True).lower().startswith("rejected"):
                    st["class"] = st.get("class", []) + ["rejected"]
        elif "illustrative" in txt[:120].lower() or "please read first" in txt[:160].lower():
            classes.append("note-illustrative")
        else:
            classes.append("callout")
        bq["class"] = classes

    # wrap tables so break-inside control has something to bite on, then fit
    for table in soup.find_all("table"):
        wrap = soup.new_tag("div")
        wrap["class"] = ["table-wrap"]
        table.wrap(wrap)
    for table in soup.find_all("table"):
        fit_table(table, geo.table_char_budget, report)

    # ASCII-art code blocks must not soft-wrap
    for pre in soup.find_all("pre"):
        body = pre.get_text()
        if any(ch in body for ch in "├└│┌┐┘─"):
            pre["class"] = pre.get("class", []) + ["ascii-art"]

    # Keep a heading with the block that follows it. Only short blocks are
    # bound in, so this never creates a large unbreakable island.
    for h in soup.find_all(["h3", "h4"]):
        nxt = h.find_next_sibling()
        if nxt is None or nxt.name in ("h2", "h3", "h4", "hr"):
            continue
        if nxt.name == "div" and "table-wrap" in (nxt.get("class") or []):
            if "tall" in (nxt.get("class") or []):
                continue
        elif nxt.name not in ("p", "ul", "ol", "blockquote"):
            continue
        if len(nxt.get_text(" ", strip=True)) > 620:
            continue
        keep = soup.new_tag("div")
        keep["class"] = ["keep"]
        h.insert_before(keep)
        keep.append(h.extract())
        keep.append(nxt.extract())

    # a horizontal rule right before a section band is noise
    for hr in list(soup.find_all("hr")):
        nxt = hr.find_next_sibling()
        if nxt is not None and nxt.name in ("h2",):
            hr.decompose()

    return soup, headings


SVG_ROOT_RE = re.compile(r"<svg\b([^>]*)>", re.I | re.S)


def prepare_svg(raw: str):
    """Make an SVG fill its container, without going through an HTML parser.

    BeautifulSoup lower-cases `viewBox` to `viewbox` and will happily leave
    both spellings on the element, so the root tag is rewritten here with
    plain string surgery and the result is injected as raw markup.
    """
    raw = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", raw)
    raw = re.sub(r"^\s*<!DOCTYPE[^>]*>\s*", "", raw, flags=re.I)
    m = SVG_ROOT_RE.search(raw)
    if not m:
        return None
    attrs = m.group(1)

    def attr(name):
        a = (re.search(r'\b' + name + r'\s*=\s*"([^"]*)"', attrs, re.I)
             or re.search(r"\b" + name + r"\s*=\s*'([^']*)'", attrs, re.I))
        return a.group(1) if a else None

    vb = attr("viewBox")
    w, h = attr("width"), attr("height")
    if not vb and w and h:
        try:
            vw = float(re.sub(r"[a-z%]+$", "", w.strip(), flags=re.I))
            vh = float(re.sub(r"[a-z%]+$", "", h.strip(), flags=re.I))
            vb = f"0 0 {vw:.6g} {vh:.6g}"
        except ValueError:
            vb = None

    # drop the attributes this function is about to re-state
    for name in ("width", "height", "viewBox", "preserveAspectRatio",
                 "style", "class"):
        attrs = re.sub(r'\s\b' + name + r'\s*=\s*"[^"]*"', "", attrs, flags=re.I)
        attrs = re.sub(r"\s\b" + name + r"\s*=\s*'[^']*'", "", attrs, flags=re.I)

    head = ("<svg" + attrs
            + (f' viewBox="{vb}"' if vb else "")
            + ' preserveAspectRatio="xMidYMid meet"'
            + ' class="fig-svg" style="width:100%;height:100%;display:block">')
    return head + raw[m.end():]


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_figures_html(figdir, prefix, captions, geo, only=None):
    """Raw HTML for the Figures section: one fitted, captioned figure per page.

    Returns (html, [(number, caption, filename), ...]). When no SVG is present
    a visible placeholder is emitted and the next build picks the files up
    with no configuration change.
    """
    svgs = []
    if figdir.is_dir():
        svgs = sorted(figdir.glob(f"{prefix}_fig*.svg"),
                      key=lambda p: (int(re.search(r"_fig(\d+)", p.name).group(1))
                                     if re.search(r"_fig(\d+)", p.name) else 999, p.name))
        if only:
            keep = set(only)
            svgs = [p for p in svgs
                    if re.search(r"_fig(\d+)", p.name)
                    and int(re.search(r"_fig(\d+)", p.name).group(1)) in keep]

    if not svgs:
        want = f"{prefix}_fig1…fig6.svg"
        return (f'<div class="figures-block"><div class="figures-missing">'
                f'<strong>Figures — pending.</strong> The diagram set for this case '
                f'(<code>{_esc(want)}</code>) was not present in '
                f'<code>{_esc(figdir.as_posix())}</code> when this document was built. '
                f'The pipeline picks the SVGs up automatically and lays them out one per '
                f'landscape page, fitted, with captions, on the next build — no change '
                f'to this document or to its configuration is needed.'
                f'</div></div>', [])

    parts = ['<div class="figures-block">']
    placed = []
    for i, svg_path in enumerate(svgs, start=1):
        mnum = re.search(r"_fig(\d+)", svg_path.name)
        num = int(mnum.group(1)) if mnum else i
        body = prepare_svg(svg_path.read_text(encoding="utf-8", errors="replace"))
        if body is None:
            print(f"  ! {svg_path.name}: no <svg> root, skipped", file=sys.stderr)
            continue
        fallback = re.sub(r"^.*?_fig\d+_?", "", svg_path.stem).replace("_", " ").strip()
        title = captions.get(num) or (fallback[:1].upper() + fallback[1:]) or f"Diagram {num}"
        parts.append(
            f'<div class="figure-page"><div class="figure-frame">{body}</div>'
            f'<div class="figure-caption"><span class="fig-no">Figure {num}</span>'
            f'— {_esc(title)}<span class="fig-src">{_esc(svg_path.name)}</span>'
            f'</div></div>')
        placed.append((num, title, svg_path.name))
    parts.append("</div>")
    return "".join(parts), placed


def extract_figure_captions(md_text):
    """Pull diagram names out of the '§13 What we would draw next' table."""
    caps = {}
    # Scoped to that one section: a whole-document scan matches any numbered
    # table and yields captions like "Figure 1 - Owner".
    _front, _secs = split_sections(md_text)
    body = None
    for sec in _secs:
        t = strip_md(sec["title"]).lower()
        if "draw next" in t or "diagram" in t:
            body = "\n".join(sec["intro"]
                             + [l for sub in sec["subs"] for l in sub["lines"]])
            break
    if body is None:
        return caps
    for line in body.split("\n"):
        m = re.match(r"^\|\s*(\d{1,2})\s*\|\s*\*\*(.+?)\*\*\s*\|", line.strip())
        if m:
            n = int(m.group(1))
            if 1 <= n <= 12 and n not in caps:
                caps[n] = strip_md(m.group(2))
    return caps


def cover_html(meta, geo):
    def esc(s):
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    fields = []
    for label, value in meta.get("cover_fields", []):
        if value:
            fields.append(f"<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>")
    return f"""<section class="cover">
  <div>
    <div class="cover-bar"></div>
    <div class="cover-rule-dots"><span></span><span></span><span></span><span></span><span></span></div>
  </div>
  <div class="cover-mid">
    <div class="cover-eyebrow">{esc(meta.get('eyebrow', 'Solution design'))}</div>
    <h1>{esc(meta['title'])}</h1>
    <div class="cover-sub">{esc(meta.get('subtitle',''))}</div>
    <dl class="cover-meta">{''.join(fields)}</dl>
  </div>
  <div class="cover-foot">
    <div class="cover-illustrative">{meta.get('illustrative_html','')}</div>
    <div class="cover-imprint"><span>{esc(meta.get('imprint_left',''))}</span>
      <span>{esc(meta.get('imprint_right',''))}</span></div>
  </div>
</section>"""


def toc_html(headings, pagemap, geo, note):
    rows = []
    for h in headings:
        pg = pagemap.get(h["marker"])
        pgtxt = str(pg) if pg else "&nbsp;&nbsp;"
        cls = "toc-l1" if h["level"] <= 2 else "toc-l2"
        title = h["title"].replace("&", "&amp;").replace("<", "&lt;")
        rows.append(
            f'<a class="toc-entry {cls}" href="#{h["id"]}">'
            f'<span class="toc-txt">{title}</span>'
            f'<span class="toc-dots"></span>'
            f'<span class="toc-pg">{pgtxt}</span></a>')
    return (f'<section class="toc"><h2 class="toc-title">Contents</h2>'
            f'<div class="toc-note">{note}</div>'
            f'<div class="toc-list">{"".join(rows)}</div></section>')


def assemble(md_text, meta, geo, figdir, figprefix, captions, pagemap, css,
             fig_only=None):
    html_body = markdown.markdown(md_text, extensions=MD_EXTENSIONS,
                                  extension_configs=MD_CONFIG, output_format="html5")
    report = []
    soup, headings = transform_body(html_body, geo, report)

    # Figures: leave a comment token in the tree and splice raw SVG markup into
    # the serialised HTML, so BeautifulSoup never touches the SVG source.
    figures_placed = []
    figures_html = ""
    token = "<!--FIGURES-->"
    for el in soup.find_all(string=re.compile(r"\[\[FIGURES\]\]")):
        host = el.parent
        figures_html, figures_placed = build_figures_html(
            figdir, figprefix, captions, geo, only=fig_only)
        marker = Comment("FIGURES")
        if host.name in ("p", "div") and host.get_text(strip=True) == "[[FIGURES]]":
            host.replace_with(marker)
        else:
            el.replace_with(marker)
        break

    # a trailing rule left by the last '---' in the source is noise
    while soup.contents and getattr(soup.contents[-1], "name", None) in ("hr", None):
        last = soup.contents[-1]
        if getattr(last, "name", None) == "hr":
            last.decompose()
        elif not str(last).strip():
            last.extract()
        else:
            break

    doc_div = soup.new_tag("div")
    doc_div["class"] = ["doc"]
    for child in list(soup.contents):
        doc_div.append(child.extract())
    body_html = str(doc_div)
    if figures_html:
        body_html = body_html.replace(token, figures_html, 1)

    body_class = "compact" if meta.get("compact") else ""
    note = (f"Page numbers are the PDF page numbers of this document "
            f"({geo.page_name} {'landscape' if geo.landscape else 'portrait'}), "
            f"resolved by measuring the rendered output.")
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{meta['title']}</title>
<style id="page-geometry">{geo.css_vars()}</style>
<style id="house-style">{css}</style>
</head><body class="{body_class}">
{cover_html(meta, geo)}
{toc_html(headings, pagemap, geo, note)}
{body_html}
<div class="colophon"><div class="colophon-bar"></div>
<div class="colophon-text"><strong>End of document.</strong> {meta['title']} &middot;
{meta.get('doc_kind', 'Solution design')} &middot; {meta.get('date_text', '')} &middot;
Illustrative &mdash; fictional client; all figures illustrative.</div></div>
</body></html>"""
    return page, headings, report, figures_placed


# --------------------------------------------------------------------------
# Render + measure
# --------------------------------------------------------------------------
HDR_SECT_TOKEN = "@@SECT@@"


def header_template(meta, geo):
    pad = geo.margin["left"]
    return (f'<div style="width:100%;font-family:\'Segoe UI\',Arial,sans-serif;'
            f'font-size:7.4pt;color:#74839A;padding:0 {pad}mm;'
            f'-webkit-print-color-adjust:exact;">'
            f'<div style="border-bottom:0.2mm solid #D6DCE6;padding-bottom:1.4mm;'
            f'display:flex;justify-content:space-between;">'
            f'<span style="letter-spacing:0.06em;">{meta["running_title"]}</span>'
            f'<span style="letter-spacing:0.08em;text-transform:uppercase;">{HDR_SECT_TOKEN}</span>'
            f'</div></div>')


def footer_template(meta, geo):
    pad = geo.margin["left"]
    return (f'<div style="width:100%;font-family:\'Segoe UI\',Arial,sans-serif;'
            f'font-size:7.4pt;color:#74839A;padding:0 {pad}mm;'
            f'-webkit-print-color-adjust:exact;">'
            f'<div style="border-top:0.2mm solid #D6DCE6;padding-top:1.4mm;'
            f'display:flex;justify-content:space-between;">'
            f'<span style="letter-spacing:0.05em;">{meta["footer_left"]}</span>'
            f'<span style="font-variant-numeric:tabular-nums;">Page '
            f'<span class="pageNumber"></span> of <span class="totalPages"></span></span>'
            f'</div></div>')


def render_pdf(page_obj, html_path, out_pdf, meta, geo):
    page_obj.goto(html_path.as_uri(), wait_until="load")
    page_obj.wait_for_timeout(500)
    page_obj.evaluate("() => document.fonts ? document.fonts.ready : true")
    page_obj.pdf(
        path=str(out_pdf),
        width=f"{geo.page_w}mm", height=f"{geo.page_h}mm",
        print_background=True,
        display_header_footer=True,
        header_template=header_template(meta, geo),
        footer_template=footer_template(meta, geo),
        margin=geo.pdf_margins(),
        prefer_css_page_size=False,
    )


def measure_pages(pdf_path, headings):
    """marker -> 1-based page number, by locating the transparent markers."""
    doc = fitz.open(str(pdf_path))
    pagemap = {}
    remaining = {h["marker"] for h in headings}
    for pno in range(doc.page_count):
        if not remaining:
            break
        text = doc[pno].get_text()
        for mk in list(remaining):
            if mk in text:
                pagemap[mk] = pno + 1
                remaining.discard(mk)
    n = doc.page_count
    doc.close()
    return pagemap, n


def stamp_pdf(pdf_path, headings, pagemap, meta, geo):
    """Replace the header's @@SECT@@ token with the running section name, and
    clear the header/footer furniture from the cover page."""
    doc = fitz.open(str(pdf_path))
    # page -> section title (last level-2 heading at or before this page)
    order = sorted(((pagemap[h["marker"]], h) for h in headings
                    if h["level"] == 2 and h["marker"] in pagemap), key=lambda t: t[0])
    def section_for(pno):
        name = "Contents"
        for start, h in order:
            if start <= pno:
                name = strip_md(h["title"])
            else:
                break
        return name

    for pno in range(doc.page_count):
        page = doc[pno]
        hits = page.search_for(HDR_SECT_TOKEN)
        if pno == 0:
            # cover: remove the header and footer furniture (text and rules)
            top = fitz.Rect(0, 0, page.rect.x1, geo.margin["top"] / MM_PER_PT * 0.98)
            bot = fitz.Rect(0, page.rect.y1 - geo.margin["bottom"] / MM_PER_PT * 0.98,
                            page.rect.x1, page.rect.y1)
            for r in (top, bot):
                page.add_redact_annot(r)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            continue
        if not hits:
            continue
        r = hits[0]
        name = section_for(pno + 1).upper()
        if len(name) > 62:
            name = name[:60].rstrip() + "…"
        # drop the placeholder token without disturbing the header rule
        page.add_redact_annot(fitz.Rect(r.x0 - 0.8, r.y0 - 1.0, r.x1 + 0.8, r.y1 + 1.0))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        box = fitz.Rect(r.x1 - 340, r.y0 - 1.0, r.x1, r.y1 + 4.0)
        page.insert_textbox(box, name, fontsize=7.2, fontname="helv",
                            color=(0.455, 0.514, 0.604), align=fitz.TEXT_ALIGN_RIGHT)
    tmp = pathlib.Path(str(pdf_path) + ".stamp.tmp")
    doc.save(str(tmp), garbage=3, deflate=True)
    doc.close()
    tmp.replace(pdf_path)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def build(cfg, browser=None, verbose=True):
    src = pathlib.Path(cfg["source"]).resolve()
    out = pathlib.Path(cfg["out"]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    md_text = src.read_text(encoding="utf-8")

    geo = Geometry(cfg.get("page", "A4"), cfg.get("landscape", False),
                   cfg.get("margins"), cfg.get("columns"),
                   body_pt=cfg.get("body_pt"), leading=cfg.get("leading"),
                   section_page_break=cfg.get("section_page_break", True))
    css = pathlib.Path(cfg.get("css", DEFAULT_CSS)).read_text(encoding="utf-8")
    captions = extract_figure_captions(md_text)
    figdir = pathlib.Path(cfg.get("figures_dir", ROOT / "diagrams")).resolve()
    figprefix = cfg.get("figure_prefix", "case01")

    selected = select_markdown(md_text, cfg.get("include"),
                               cfg.get("drop_front_sections", ()),
                               cfg.get("figures_after"),
                               cfg.get("drop_front_matter", False))

    today = cfg.get("date") or _dt.date.today().strftime("%d %B %Y")
    meta = {
        "title": cfg["title"],
        "subtitle": cfg.get("subtitle", ""),
        "eyebrow": cfg.get("eyebrow", "Solution design"),
        "running_title": cfg.get("running_title", cfg["title"]),
        "footer_left": cfg.get("footer_left", f"{cfg.get('client','')} · Solution design · {today}"),
        "cover_fields": cfg.get("cover_fields") or [
            ("Client", cfg.get("client", "")),
            ("Document", cfg.get("doc_kind", "Solution design")),
            ("Date", today),
            ("Version", cfg.get("version", "1.0")),
            ("Status", cfg.get("status", "For review")),
        ],
        "illustrative_html": cfg.get("illustrative_html",
            "<strong>Illustrative — fictional client; all figures illustrative.</strong> "
            "Every number in this document (revenue, volumes, timelines, benefits, effort "
            "and cost) exists to make the reasoning concrete and checkable. Nothing here is "
            "a quotation, a commitment, or a statement about any real organisation's estate."),
        "compact": cfg.get("compact", False),
        "date_text": today,
        "doc_kind": cfg.get("doc_kind", "Solution design"),
        "imprint_left": cfg.get("imprint_left", "Lakehouse Design Pattern series"),
        "imprint_right": cfg.get("imprint_right", out.name),
    }

    workdir = out.parent / "_work"
    workdir.mkdir(exist_ok=True)
    html_path = workdir / (out.stem + ".html")

    if verbose:
        print(f"\n=== {out.name}")
        print(f"  source   : {src}")
        print(f"  geometry : {geo.describe()}")

    pagemap = {}
    headings = report = figures_placed = None
    npages = 0
    passes = 0

    def _run(browser):
        nonlocal pagemap, headings, report, figures_placed, npages, passes
        pg = browser.new_page(viewport={"width": 1400, "height": 1000})
        try:
            for attempt in range(1, 7):
                html, headings, report, figures_placed = assemble(
                    selected, meta, geo, figdir, figprefix, captions, pagemap, css,
                    fig_only=cfg.get("figure_numbers"))
                html_path.write_text(html, encoding="utf-8")
                render_pdf(pg, html_path, out, meta, geo)
                newmap, npages = measure_pages(out, headings)
                passes = attempt
                changed = sum(1 for k, v in newmap.items() if pagemap.get(k) != v)
                if verbose:
                    print(f"  pass {attempt}: {npages} pages, "
                          f"{len(newmap)}/{len(headings)} headings located, "
                          f"{changed} TOC number(s) changed")
                if changed == 0 and attempt > 1:
                    break
                pagemap = newmap
            else:
                print("  ! TOC page numbers did not reach a fixed point", file=sys.stderr)
        finally:
            pg.close()

    if browser is None:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="msedge")
            try:
                _run(b)
            finally:
                b.close()
    else:
        _run(browser)

    stamp_pdf(out, headings, pagemap, meta, geo)

    missing = [h["title"] for h in headings if h["marker"] not in pagemap]
    if missing and verbose:
        print(f"  ! headings not located: {missing[:5]}", file=sys.stderr)

    tight = [r for r in report if not r["fits"]]
    if verbose:
        widest = sorted(report, key=lambda r: -r["ncols"])[:3]
        print(f"  tables   : {len(report)}; widest "
              f"{[(r['ncols'], r['tier']) for r in widest]}; "
              f"{sum(1 for r in report if r['tier'] != 'base')} down-tiered; "
              f"{len(tight)} still tight")
        if figures_placed:
            print(f"  figures  : {len(figures_placed)} embedded "
                  f"({', '.join(str(n) for n, _, _ in figures_placed)})")
        else:
            print(f"  figures  : none found in {figdir} (prefix {figprefix}_fig*.svg) "
                  f"— placeholder emitted; will be picked up automatically next run")
        print(f"  -> {out}  ({npages} pages, {passes} render pass(es))")

    return {"out": out, "pages": npages, "headings": headings, "pagemap": pagemap,
            "tables": report, "figures": figures_placed, "passes": passes, "geo": geo}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--page", default="A4")
    ap.add_argument("--landscape", action="store_true")
    ap.add_argument("--columns", type=int)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--client", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--status", default="For review")
    ap.add_argument("--doc-kind", default="Solution design")
    ap.add_argument("--figures-dir", default=str(ROOT / "diagrams"))
    ap.add_argument("--figure-prefix", default="case01")
    ap.add_argument("--figures-after", default=None,
                    help="heading key after which the Figures section is inserted")
    ap.add_argument("--include", default=None,
                    help="JSON list of section include specs; omit for the whole document")
    ap.add_argument("--config-json", default=None, help="full config as JSON (overrides flags)")
    a = ap.parse_args(argv)

    if a.config_json:
        cfg = json.loads(a.config_json)
    else:
        cfg = {k: v for k, v in vars(a).items() if v not in (None, "", False)}
        cfg["doc_kind"] = a.doc_kind
        if a.include:
            cfg["include"] = json.loads(a.include)
        cfg.pop("config_json", None)
        cfg["figures_dir"] = a.figures_dir
        cfg["figure_prefix"] = a.figure_prefix
        cfg["figures_after"] = a.figures_after
    build(cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
