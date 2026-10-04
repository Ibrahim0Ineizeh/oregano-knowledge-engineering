#!/usr/bin/env python3
"""Build the publication PDF from report.md and the committed PNG figures.

Usage: python scripts/build_report.py
Requires reportlab. This script does not execute the analysis notebook.
"""
from html import escape
from pathlib import Path
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    KeepTogether, Preformatted, PageBreak,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "oregano-study.pdf"
INK = colors.HexColor("#182c3b")
TEAL = colors.HexColor("#1f6b65")
MUTED = colors.HexColor("#55636b")
LIGHT = colors.HexColor("#edf3f2")
WIDTH = A4[0] - 110

STYLES = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24,
                            leading=29, textColor=INK, spaceAfter=14),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=15,
                         leading=19, textColor=TEAL, spaceBefore=15,
                         spaceAfter=8, keepWithNext=True),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11,
                         leading=15, textColor=INK, spaceBefore=10,
                         spaceAfter=6, keepWithNext=True),
    "body": ParagraphStyle("body", fontName="Times-Roman", fontSize=10.5,
                           leading=14.5, textColor=INK, spaceAfter=8,
                           allowWidows=0, allowOrphans=0),
    "caption": ParagraphStyle("caption", fontName="Helvetica", fontSize=8.5,
                              leading=11.3, textColor=MUTED, spaceAfter=12),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.1,
                           leading=10.8, textColor=INK, splitLongWords=True),
    "headcell": ParagraphStyle("headcell", fontName="Helvetica-Bold", fontSize=8.1,
                               leading=10.8, textColor=colors.white),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=7.5,
                           leading=11, textColor=INK, backColor=LIGHT,
                           borderPadding=10, spaceBefore=4, spaceAfter=12),
}


def plain(text):
    for old, new in {"–": "-", "—": "-", "−": "-", "’": "'",
                     "“": '"', "”": '"', "→": "->", "·": " | "}.items():
        text = text.replace(old, new)
    return text


def inline(text, table=False):
    """Convert the small Markdown subset used by the report to PDF markup."""
    text = escape(plain(text).replace("\\|", "|"))
    def link(match):
        href = match[2]
        if not re.match(r"[a-z]+:", href):
            href = os.path.relpath(ROOT / href, OUTPUT.parent)
        return '<link href="' + href + '" color="#1f6b65">' + match[1] + '</link>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    # Table body identifiers stay in the normal face to keep narrow cells legible.
    if table:
        text = text.replace("`", "")
    else:
        text = re.sub(r"`([^`]+)`", r'<font face="Courier" size="8.4">\1</font>', text)
    return text


def table(rows):
    n = len(rows[0])
    if n == 2:
        widths = [WIDTH * .25, WIDTH * .75]
    elif n == 3:
        widths = [WIDTH * .31, WIDTH * .35, WIDTH * .34]
    elif n == 4 and "Entity class" in rows[0][0]:
        widths = [WIDTH * .28, WIDTH * .22, WIDTH * .28, WIDTH * .22]
    elif n == 4 and "Rank 1" in rows[0][1]:
        widths = [WIDTH * .23, WIDTH * .257, WIDTH * .257, WIDTH * .256]
    else:
        widths = [WIDTH / n] * n
    cells = [
        [Paragraph(inline(x, table=True), STYLES["headcell" if i == 0 else "cell"])
         for x in row]
        for i, row in enumerate(rows)
    ]
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, -1), (-1, -1), .45, colors.HexColor("#bccdcb")),
    ]))
    return result


def story_from_markdown(text):
    lines = text.splitlines()
    story = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("# "):
            story.append(Paragraph("KNOWLEDGE ENGINEERING / COMBINED STUDY", STYLES["caption"]))
            story.append(Paragraph(inline(s[2:]), STYLES["title"]))
            i += 1
        elif s.startswith("## ") or s.startswith("### "):
            level = "h3" if s.startswith("### ") else "h2"
            label = s[4:] if level == "h3" else s[3:]
            if label.startswith("9. References"):
                story.append(PageBreak())
            story.append(Paragraph(inline(label), STYLES[level]))
            i += 1
        elif s.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(plain(lines[i]))
                i += 1
            story.append(Preformatted("\n".join(code), STYLES["code"]))
            i += 1
        elif s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [x.strip() for x in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))]
                if not all(re.fullmatch(r":?-+:?", x.replace(" ", "")) for x in row):
                    rows.append(row)
                i += 1
            block = [table(rows), Spacer(1, 10)]
            if story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("h2", "h3"):
                block.insert(0, story.pop())
            story.append(KeepTogether(block))
        elif s.startswith("!["):
            match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", s)
            path = ROOT / match[2]
            iw, ih = ImageReader(str(path)).getSize()
            w = WIDTH
            h = w * ih / iw
            if h > 440:
                w *= 440 / h
                h = 440
            fig = Image(str(path), width=w, height=h, hAlign="CENTER")
            block = [Spacer(1, 5), fig, Spacer(1, 5)]
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and lines[i].strip().startswith("*Figure "):
                block.append(Paragraph(inline(lines[i].strip().strip("*")), STYLES["caption"]))
                i += 1
            story.append(KeepTogether(block))
        else:
            paragraph = [s]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(("#", "|", "![", "```")):
                paragraph.append(lines[i].strip())
                i += 1
            story.append(Paragraph(inline(" ".join(paragraph)), STYLES["body"]))
    return story


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saved_pages = []

    def showPage(self):
        self.saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self.saved_pages)
        for state in self.saved_pages:
            self.__dict__.update(state)
            self.draw_chrome(total)
            super().showPage()
        super().save()

    def draw_chrome(self, total):
        self.saveState()
        self.setStrokeColor(colors.HexColor("#bccdcb"))
        self.setLineWidth(.5)
        self.line(55, 47, A4[0] - 55, 47)
        self.setFillColor(MUTED)
        self.setFont("Helvetica", 8)
        self.drawString(55, 33, "Ibrahim Ineizeh | OREGANO study | Archival edition, 2026")
        self.drawRightString(A4[0] - 55, 33, f"{self._pageNumber} / {total}")
        if self._pageNumber > 1:
            self.setFont("Helvetica", 8)
            self.drawString(55, A4[1] - 35, "OREGANO: graph construction, candidate paths, and Bayesian ranking")
        self.restoreState()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=55, rightMargin=55,
        topMargin=58, bottomMargin=63, title="OREGANO: from knowledge graph construction to candidate ranking",
        author="Ibrahim Ineizeh", subject="Combined Knowledge Engineering study and archival edition",
    )
    doc.build(story_from_markdown((ROOT / "report.md").read_text()), canvasmaker=NumberedCanvas)
    print(OUTPUT)


if __name__ == "__main__":
    main()
