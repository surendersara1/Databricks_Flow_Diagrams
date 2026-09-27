#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify.py — check a built PDF instead of assuming it is right.

    python build/verify.py pdf/X.pdf --png 1,2,4,9 --outdir _check

Checks: page count, cover text, TOC page numbers against where the headings
actually landed, running header / footer presence, blank pages, code-block
and table overflow (text painted outside the content box), and the widest
table's cell text against the Markdown source row.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import fitz

MM = 25.4 / 72.0


def norm(s):
    return re.sub(r"\s+", " ", s.replace("—", "-").replace("–", "-")
                  .replace("’", "'").replace("\xa0", " ")).strip().lower()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--png", default="", help="comma separated 1-based pages to rasterise")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--source", default=None, help="Markdown source, for table round-trip")
    ap.add_argument("--margins", default="", help="t,b,l,r in mm, for the overflow check")
    a = ap.parse_args(argv)

    path = pathlib.Path(a.pdf)
    doc = fitz.open(str(path))
    print(f"### {path.name}")
    print(f"pages: {doc.page_count}   size: "
          f"{doc[0].rect.width*MM:.0f}x{doc[0].rect.height*MM:.0f} mm")

    # ---- cover ----------------------------------------------------------
    cover = doc[0].get_text()
    print("\n-- cover page 1 --")
    print("  " + "\n  ".join(l for l in cover.split("\n") if l.strip())[:900])
    for probe in ["Illustrative", "fictional", "Solution design", "Client", "Date"]:
        print(f"  cover contains {probe!r}: {probe.lower() in cover.lower()}")

    # ---- TOC vs reality --------------------------------------------------
    toc_pages = [i for i in range(min(6, doc.page_count))
                 if "CONTENTS" in doc[i].get_text().upper()[:4000]
                 and doc[i].get_text().count(".") > 20]
    # TOC rows are flex boxes (title / dots / number), so pair words by line
    entries = []
    for i in toc_pages:
        pg = doc[i]
        body = fitz.Rect(0, 40, pg.rect.x1, pg.rect.y1 - 40)   # skip header/footer
        words = [w for w in pg.get_text("words")
                 if fitz.Rect(w[:4]).intersects(body)]
        lines = {}
        for w in words:
            key = w[5]
            lines.setdefault(key, []).append(w)
        for key, ws in lines.items():
            ws.sort(key=lambda w: w[0])
            if len(ws) < 2:
                continue
            last = ws[-1][4]
            if not re.fullmatch(r"\d{1,3}", last):
                continue
            title = " ".join(w[4] for w in ws[:-1])
            if len(title) > 4 and not title.lower().startswith("page numbers"):
                entries.append((title, int(last)))
    print(f"\n-- TOC (pages {[p+1 for p in toc_pages]}): {len(entries)} entries parsed --")

    page_text = [norm(p.get_text()) for p in doc]
    bad = ok = 0
    misses = []
    for title, claimed in entries:
        t = norm(title)
        if len(t) < 5 or not (1 <= claimed <= doc.page_count):
            continue
        hit = t in page_text[claimed - 1]
        if hit:
            ok += 1
        else:
            where = [j + 1 for j, pt in enumerate(page_text) if t in pt and j + 1 not in
                     [p + 1 for p in toc_pages]]
            bad += 1
            misses.append((title, claimed, where[:3]))
    print(f"  TOC entries whose heading text IS on the claimed page: {ok}")
    print(f"  mismatches: {bad}")
    for m in misses[:12]:
        print(f"    ! {m[0][:58]!r} says p{m[1]}, found on {m[2]}")

    # ---- header / footer / blank ----------------------------------------
    no_hdr, no_ftr, blanks, short = [], [], [], []
    for i, p in enumerate(doc):
        t = p.get_text()
        if i == 0:
            continue
        if not re.search(r"Page \d+ of \d+", t):
            no_ftr.append(i + 1)
        head_band = p.get_text("text", clip=fitz.Rect(0, 0, p.rect.x1, 46))
        if len(head_band.strip()) < 6:
            no_hdr.append(i + 1)
        body = re.sub(r"Page \d+ of \d+", "", t)
        if len(body.strip()) < 120:
            (blanks if len(body.strip()) < 40 else short).append(i + 1)
    print(f"\n-- furniture --\n  pages missing footer 'Page X of Y': {no_ftr or 'none'}")
    print(f"  pages missing header text: {no_hdr or 'none'}")
    print(f"  near-blank pages (<40 chars of body): {blanks or 'none'}")
    print(f"  sparse pages (<120 chars, e.g. figure pages): {short or 'none'}")

    # ---- overflow: any text painted outside the content box --------------
    if a.margins:
        t, b, l, r = [float(x) for x in a.margins.split(",")]
        for i, p in enumerate(doc):
            box = fitz.Rect(l / MM - 2, t / MM - 14, p.rect.x1 - r / MM + 2,
                            p.rect.y1 - b / MM + 14)
            for blk in p.get_text("blocks"):
                rr = fitz.Rect(blk[:4])
                if rr.x1 > box.x1 + 1.5 or rr.x0 < box.x0 - 1.5:
                    print(f"  ! overflow p{i+1}: {blk[4][:60]!r} x=[{rr.x0:.0f},{rr.x1:.0f}] "
                          f"box=[{box.x0:.0f},{box.x1:.0f}]")

    # ---- widest table round-trip ----------------------------------------
    if a.source:
        src = pathlib.Path(a.source).read_text(encoding="utf-8")
        rows = [l for l in src.split("\n") if l.strip().startswith("|")]
        widest = max(rows, key=lambda l: len(l.strip().strip("|").split("|")))
        ncol = len(widest.strip().strip("|").split("|"))
        # find the table with that column count and test every cell of a data row
        cands = [l for l in rows if len(l.strip().strip("|").split("|")) == ncol
                 and "---" not in l]
        print(f"\n-- widest table ({ncol} columns), {len(cands)} rows in source --")
        alltext = " || ".join(page_text)
        missing_cells = 0
        checked = 0
        for row in cands:
            for cell in row.strip().strip("|").split("|"):
                c = norm(cell)
                if len(c) < 4 or c.startswith("**"):
                    continue
                checked += 1
                if norm(re.sub(r"\*+", "", cell)) not in alltext:
                    missing_cells += 1
                    if missing_cells <= 8:
                        print(f"    ! cell not found in PDF text: {cell.strip()[:70]!r}")
        print(f"  cells checked: {checked}, not found: {missing_cells}")

    # ---- rasterise -------------------------------------------------------
    if a.png:
        out = pathlib.Path(a.outdir or (path.parent / "_check"))
        out.mkdir(parents=True, exist_ok=True)
        for n in [int(x) for x in a.png.split(",") if x.strip()]:
            if not (1 <= n <= doc.page_count):
                continue
            pix = doc[n - 1].get_pixmap(dpi=a.dpi)
            f = out / f"{path.stem}_p{n:03d}.png"
            pix.save(str(f))
            print(f"  raster -> {f}  ({pix.width}x{pix.height})")
    doc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
