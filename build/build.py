#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build.py — build every configured consulting deliverable in one run.

    python build/build.py                # build everything
    python build/build.py --only brief   # substring filter on the output name
    python build/build.py --list         # show the configured deliverables

Each entry in DELIVERABLES is a config dict consumed by md2pdf.build().
Section selection is config-driven: `include` is a list of either
  "3."                                     -> the whole H2 section
  {"h2": "5.", "h3": ["5.1", "5.8"]}       -> section intro + named H3s
so a second deliverable never requires editing the Markdown source.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright  # noqa: E402

import md2pdf  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
PDF = ROOT / "pdf"
DIAGRAMS = ROOT / "diagrams"

CASE01 = CASES / "01_Global_Omnichannel_Retail_Lakehouse.md"
CASE02 = CASES / "02_Global_Bank_Regulated_Lakehouse.md"

TODAY = _dt.date.today().strftime("%d %B %Y")

# --------------------------------------------------------------------------
# The executive brief's contents, as a list of headings — not a second copy
# of the Markdown. Front matter (title block + illustrative note) is always
# carried; "How to read this document" is dropped from the brief.
# --------------------------------------------------------------------------
BRIEF_SECTIONS = [
    "1.",                                             # Executive summary, in full
    {"h2": "2.", "h3": ["2.1", "2.2", "2.4"]},        # Current state, condensed
    "4.",                                             # Use cases and value
    {"h2": "5.", "h3": ["5.1", "5.8"]},               # Architecture overview + decisions
    "8.",                                             # Delivery plan
    # Cost: drivers, the profile, the construct and the payback. 10.2 "how we
    # estimate" and 10.3 "how we control cost" are method detail that belongs
    # in the annex, and dropping them is what keeps the brief inside 20 pages.
    {"h2": "10.", "h3": ["10.1", "10.4", "10.5", "10.6"]},
    "12.",                                            # Success metrics
]

DELIVERABLES = [
    # ---------------------------------------------------------------- annex
    dict(
        name="annex-case01",
        source=CASE01,
        out=PDF / "Meridian_Retail_Solution_Design.pdf",
        page="A3", landscape=True, columns=2,
        title="Meridian Retail Group — Global Omnichannel Lakehouse",
        subtitle="Full technical annex: current state, data inventory, target "
                 "architecture, governance, delivery, commercials and risk.",
        eyebrow="Solution design · Technical annex",
        running_title="Meridian Retail Group — Global Omnichannel Lakehouse",
        client="Meridian Retail Group (fictional)",
        doc_kind="Solution design — technical annex",
        version="1.0", status="For decision",
        date=TODAY,
        include=None,                                  # everything
        figures_after="5.",                            # Figures section after §5
        figures_dir=DIAGRAMS, figure_prefix="case01",
        footer_left=f"Meridian Retail Group · Solution design (technical annex) · {TODAY} · Illustrative",
        imprint_right="Meridian_Retail_Solution_Design.pdf",
    ),
    # ---------------------------------------------------------------- brief
    dict(
        name="brief-case01",
        source=CASE01,
        out=PDF / "Meridian_Retail_Executive_Brief.pdf",
        page="A4", landscape=True, columns=2,
        body_pt=8.8, leading=1.31, compact=True, section_page_break=False,
        margins={"top": 14.0, "bottom": 12.5, "left": 13.0, "right": 13.0},
        title="Meridian Retail Group — Global Omnichannel Lakehouse",
        subtitle="Executive brief: the problem, the value, the architecture in "
                 "one page, the plan, the cost and how success is measured.",
        eyebrow="Solution design · Executive brief",
        running_title="Meridian Retail — Executive brief",
        client="Meridian Retail Group (fictional)",
        doc_kind="Solution design — executive brief",
        version="1.0", status="For decision",
        date=TODAY,
        include=BRIEF_SECTIONS,
        drop_front_sections=("How to read this document",),
        figures_after="5.8",                           # after the architecture section
        figures_dir=DIAGRAMS, figure_prefix="case01",
        # a pitch carries the two diagrams an executive reads: the end-to-end
        # flow and the delivery timeline. The annex carries all six.
        figure_numbers=[1, 6],
        drop_front_matter=True,                        # the cover already says this
        footer_left=f"Meridian Retail Group · Executive brief · {TODAY} · Illustrative",
        imprint_right="Meridian_Retail_Executive_Brief.pdf",
    ),
    # ------------------------------------------------- case 02 (same pipeline)
    dict(
        name="annex-case02",
        source=CASE02,
        out=PDF / "Case02_Global_Bank_Solution_Design.pdf",
        page="A3", landscape=True, columns=2,
        title="Global bank — regulated lakehouse",
        subtitle="Full technical annex.",
        eyebrow="Solution design · Technical annex",
        running_title="Global bank — regulated lakehouse",
        client="Fictional global bank",
        doc_kind="Solution design — technical annex",
        version="1.0", status="Draft",
        date=TODAY,
        include=None,
        figures_after="5.",
        figures_dir=DIAGRAMS, figure_prefix="case02",
        enabled=False,   # switch on when case 02 is ready to publish
    ),
]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="substring filter on the deliverable name")
    ap.add_argument("--all", action="store_true", help="include entries marked enabled=False")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)

    todo = [d for d in DELIVERABLES
            if (a.all or d.get("enabled", True))
            and (not a.only or a.only.lower() in d["name"].lower()
                 or a.only.lower() in pathlib.Path(d["out"]).name.lower())]

    if a.list:
        for d in DELIVERABLES:
            flag = "" if d.get("enabled", True) else "  (disabled)"
            print(f"{d['name']:<16} {d['page']}"
                  f"{' landscape' if d.get('landscape') else ' portrait':<11} "
                  f"-> {pathlib.Path(d['out']).name}{flag}")
        return 0

    if not todo:
        print("nothing to build", file=sys.stderr)
        return 1

    PDF.mkdir(parents=True, exist_ok=True)
    if not DIAGRAMS.is_dir():
        print(f"note: {DIAGRAMS} does not exist yet — figures will be placeholders")

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        try:
            for cfg in todo:
                cfg = {k: v for k, v in cfg.items() if k not in ("name", "enabled")}
                cfg["source"] = str(cfg["source"])
                cfg["out"] = str(cfg["out"])
                cfg["figures_dir"] = str(cfg["figures_dir"])
                results.append(md2pdf.build(cfg, browser=browser))
        finally:
            browser.close()

    print("\n" + "=" * 72)
    for r in results:
        nfig = len(r["figures"] or [])
        print(f"{pathlib.Path(r['out']).name:<48} {r['pages']:>4} pages   "
              f"{nfig} figure(s)")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
