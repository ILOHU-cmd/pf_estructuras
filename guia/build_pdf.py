#!/usr/bin/env python3
"""Construye la guía de código y defensa en PDF a partir de los archivos Markdown."""

from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

BASE = Path(__file__).resolve().parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
OUT_DEFAULT = BASE.parent / "Guia_codigo_y_defensa.pdf"

PAGE_W, PAGE_H = A4
MARGIN_X = 50
CONTENT_W = PAGE_W - 2 * MARGIN_X
GREEN = HexColor("#14532D")
GREEN_2 = HexColor("#2F6B3A")
INK = HexColor("#1F2937")
MUTED = HexColor("#6B7280")
AMBER = HexColor("#D97706")
BLUE = HexColor("#2563EB")
LIGHT_GREEN = HexColor("#F1F8F2")
LIGHT_AMBER = HexColor("#FFF8E7")
LIGHT_BLUE = HexColor("#EEF4FB")
GRID = HexColor("#D7E1D7")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_DIR / "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", FONT_DIR / "DejaVuSans-Bold.ttf"))
    # No hay DejaVuSans-Oblique instalada; se usa la regular como sustituto.
    pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", FONT_DIR / "DejaVuSans.ttf"))
    pdfmetrics.registerFont(
        TTFont("DejaVuSans-BoldOblique", FONT_DIR / "DejaVuSans-Bold.ttf")
    )
    pdfmetrics.registerFont(TTFont("DejaVuSansMono", FONT_DIR / "DejaVuSansMono.ttf"))
    pdfmetrics.registerFont(
        TTFont("DejaVuSansMono-Bold", FONT_DIR / "DejaVuSansMono-Bold.ttf")
    )
    pdfmetrics.registerFont(TTFont("DejaVuSerif", FONT_DIR / "DejaVuSerif.ttf"))
    pdfmetrics.registerFontFamily(
        "DejaVuSans",
        normal="DejaVuSans",
        bold="DejaVuSans-Bold",
        italic="DejaVuSans-Oblique",
        boldItalic="DejaVuSans-BoldOblique",
    )
    pdfmetrics.registerFontFamily(
        "DejaVuSansMono",
        normal="DejaVuSansMono",
        bold="DejaVuSansMono-Bold",
        italic="DejaVuSansMono",
        boldItalic="DejaVuSansMono-Bold",
    )


# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
BODY = ParagraphStyle(
    "Body",
    fontName="DejaVuSans",
    fontSize=9.3,
    leading=13.35,
    textColor=INK,
    alignment=TA_JUSTIFY,
    spaceAfter=5,
)
BODY_LEFT = ParagraphStyle("BodyLeft", parent=BODY, alignment=TA_LEFT)
H1 = ParagraphStyle(
    "H1",
    fontName="DejaVuSans-Bold",
    fontSize=19.5,
    leading=23.5,
    textColor=GREEN,
    spaceBefore=10,
    spaceAfter=4,
    keepWithNext=True,
)
H2 = ParagraphStyle(
    "H2",
    fontName="DejaVuSans-Bold",
    fontSize=12.8,
    leading=16.2,
    textColor=GREEN_2,
    spaceBefore=12,
    spaceAfter=4,
    keepWithNext=True,
)
H3 = ParagraphStyle(
    "H3",
    fontName="DejaVuSans-Bold",
    fontSize=10.6,
    leading=13.6,
    textColor=INK,
    spaceBefore=9,
    spaceAfter=3,
    keepWithNext=True,
)
BULLET = ParagraphStyle(
    "Bullet",
    parent=BODY,
    alignment=TA_LEFT,
    leftIndent=13,
    bulletIndent=2,
    spaceAfter=2.5,
)
NUMBER = ParagraphStyle(
    "Number",
    parent=BODY,
    alignment=TA_LEFT,
    leftIndent=18,
    bulletIndent=2,
    spaceAfter=2.5,
)
CHECK = ParagraphStyle(
    "Check",
    parent=BULLET,
    leftIndent=22,
    bulletIndent=2,
    spaceAfter=2.5,
)
CALLOUT = ParagraphStyle(
    "Callout",
    fontName="DejaVuSans",
    fontSize=8.9,
    leading=12.5,
    textColor=INK,
    alignment=TA_LEFT,
    spaceAfter=0,
)
CAPTION = ParagraphStyle(
    "Caption",
    fontName="DejaVuSerif",
    fontSize=7.7,
    leading=10.2,
    textColor=MUTED,
    alignment=TA_CENTER,
    spaceBefore=2,
    spaceAfter=6,
)
TOC_TITLE = ParagraphStyle(
    "TOCTitle",
    fontName="DejaVuSans-Bold",
    fontSize=18,
    leading=22,
    textColor=GREEN,
    spaceAfter=10,
)
TOC1 = ParagraphStyle(
    "TOC1",
    fontName="DejaVuSans-Bold",
    fontSize=9.7,
    leading=14.2,
    textColor=GREEN,
    spaceBefore=3,
)
TOC2 = ParagraphStyle(
    "TOC2",
    fontName="DejaVuSans",
    fontSize=8.6,
    leading=11.25,
    textColor=HexColor("#374151"),
    leftIndent=14,
)
TABLE_HEAD = ParagraphStyle(
    "TableHead",
    fontName="DejaVuSans-Bold",
    fontSize=7.6,
    leading=9.6,
    textColor=colors.white,
)
TABLE_BODY = ParagraphStyle(
    "TableBody",
    fontName="DejaVuSans",
    fontSize=7.6,
    leading=9.7,
    textColor=INK,
)
TABLE_HEAD_SMALL = ParagraphStyle("TableHeadSmall", parent=TABLE_HEAD, fontSize=7.2, leading=9.0)
TABLE_BODY_SMALL = ParagraphStyle("TableBodySmall", parent=TABLE_BODY, fontSize=7.2, leading=9.0)


# ---------------------------------------------------------------------------
# Markdown inline -> ReportLab XML
# ---------------------------------------------------------------------------
CODE_FONT = "DejaVuSansMono"
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline_plain(text: str) -> str:
    text = _escape(text)
    text = LINK_RE.sub(r'<link href="\2" color="#1D4ED8">\1</link>', text)
    text = BOLD_RE.sub(r"<b>\1</b>", text)
    text = ITALIC_RE.sub(r"<i>\1</i>", text)
    return text


def inline(text: str, code_color: str = "#0F5132") -> str:
    """Convierte `code`, **bold**, *italic* y links, escapando XML.

    Los spans de código se sustituyen por marcadores antes de aplicar negrita o
    cursiva para que un `**...**` que contenga código siga funcionando.
    """
    placeholders: dict[str, str] = {}

    def _code_repl(match: re.Match) -> str:
        key = f"@@CODE{len(placeholders)}@@"
        placeholders[key] = (
            f'<font name="{CODE_FONT}" size="8.1" color="{code_color}">'
            f"{_escape(match.group(1))}</font>"
        )
        return key

    text = re.sub(r"`([^`]*)`", _code_repl, text)
    text = _inline_plain(text)
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def strip_markup(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = LINK_RE.sub(r"\1", text)
    return text


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
class GuideDoc(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        self.current_section = ""

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            name = flowable.style.name
            if name == "H1":
                text = flowable.getPlainText()
                self.current_section = text
                self.notify("TOCEntry", (0, text, self.page))
            elif name == "H2":
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))


def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(HexColor("#F4F8F4"))
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Banda superior
    canvas.setFillColor(GREEN)
    canvas.rect(0, PAGE_H - 235, PAGE_W, 235, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#F59E0B"))
    canvas.rect(0, PAGE_H - 240, PAGE_W, 5, fill=1, stroke=0)

    # Motivo de red
    nodes = [
        (392, 720), (438, 770), (484, 712), (528, 762), (566, 704),
        (454, 672), (410, 760), (512, 690), (548, 728), (470, 805),
        (586, 770), (372, 690),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 6),
        (6, 7), (7, 2), (1, 8), (8, 3), (5, 9), (9, 10), (10, 8),
        (11, 0), (11, 6),
    ]
    canvas.setStrokeColor(colors.white)
    canvas.setStrokeAlpha(0.22)
    canvas.setLineWidth(0.8)
    for a, b in edges:
        canvas.line(nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1])
    canvas.setFillColor(colors.white)
    canvas.setFillAlpha(0.55)
    for x, y in nodes:
        canvas.circle(x, y, 4.2, fill=1, stroke=0)
    canvas.setFillAlpha(1)
    canvas.setStrokeAlpha(1)

    # Título
    canvas.setFillColor(colors.white)
    canvas.setFont("DejaVuSans-Bold", 29)
    canvas.drawString(MARGIN_X, PAGE_H - 85, "Guía completa de código")
    canvas.drawString(MARGIN_X, PAGE_H - 122, "y defensa del proyecto")

    canvas.setFont("DejaVuSans", 11.5)
    canvas.setFillColor(HexColor("#D1FAE5"))
    canvas.drawString(
        MARGIN_X, PAGE_H - 156,
        "Red de transferencias Ethereum ERC-20 · Teoría de Grafos",
    )
    canvas.setFont("DejaVuSans", 9.5)
    canvas.drawString(
        MARGIN_X, PAGE_H - 176,
        "Universidad Industrial de Santander · Proyecto final",
    )

    # Badge
    badge = "4 tareas  ·  4 algoritmos propios  ·  0 Dijkstra"
    canvas.setFont("DejaVuSans-Bold", 8.6)
    tw = canvas.stringWidth(badge, "DejaVuSans-Bold", 8.6)
    canvas.setFillColor(HexColor("#F59E0B"))
    canvas.roundRect(MARGIN_X, PAGE_H - 211, tw + 22, 20, 4, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#111827"))
    canvas.drawString(MARGIN_X + 11, PAGE_H - 205, badge)

    # Cuerpo de portada
    y = PAGE_H - 290
    canvas.setFillColor(INK)
    canvas.setFont("DejaVuSans-Bold", 15)
    canvas.drawString(MARGIN_X, y, "Qué encontrarás aquí")

    bullets = [
        ("Explicación celda por celda", "de las 17 celdas de código del notebook."),
        ("Argumentos de correctitud", "y complejidad de cada algoritmo."),
        ("Resultados y figuras", "con la interpretación que debes dar."),
        ("Guion de 8:40", "y un banco de 58 preguntas de defensa."),
    ]
    y -= 26
    for head, rest in bullets:
        canvas.setFillColor(HexColor("#F59E0B"))
        canvas.circle(MARGIN_X + 3, y + 3, 2.6, fill=1, stroke=0)
        canvas.setFillColor(INK)
        canvas.setFont("DejaVuSans-Bold", 10.2)
        canvas.drawString(MARGIN_X + 14, y, head)
        w = canvas.stringWidth(head, "DejaVuSans-Bold", 10.2)
        canvas.setFont("DejaVuSans", 10.2)
        canvas.setFillColor(HexColor("#374151"))
        canvas.drawString(MARGIN_X + 18 + w, y, rest)
        y -= 24

    # Caja de cita
    quote = (
        "“Si puedes explicar por qué cada línea existe,\n"
        "puedes defender el proyecto.”"
    )
    canvas.setFillColor(HexColor("#E8F3E9"))
    canvas.roundRect(MARGIN_X, y - 56, CONTENT_W, 62, 5, fill=1, stroke=0)
    canvas.setFillColor(GREEN)
    canvas.rect(MARGIN_X, y - 56, 4, 62, fill=1, stroke=0)
    canvas.setFont("DejaVuSerif", 11.5)
    canvas.setFillColor(GREEN)
    canvas.drawString(MARGIN_X + 16, y - 23, quote.split("\n")[0])
    canvas.drawString(MARGIN_X + 16, y - 41, quote.split("\n")[1])

    # Resultados en cifras
    stats = [
        ("36.618", "componentes USDC"),
        ("0,0904", "PageRank Binance 1"),
        ("13", "comunidades · Q 0,614"),
        ("USD 56,85 M", "flujo máximo"),
    ]
    canvas.setFillColor(GREEN)
    canvas.setFont("DejaVuSans-Bold", 13)
    canvas.drawString(MARGIN_X, 315, "Resultados en cifras")
    gap = 9
    card_w = (CONTENT_W - 3 * gap) / 4
    card_h = 78
    top = 293
    for i, (value, label) in enumerate(stats):
        x = MARGIN_X + i * (card_w + gap)
        canvas.setFillColor(colors.white)
        canvas.setStrokeColor(HexColor("#CBD5C8"))
        canvas.setLineWidth(0.7)
        canvas.roundRect(x, top - card_h, card_w, card_h, 5, fill=1, stroke=1)
        canvas.setFillColor(HexColor("#F59E0B"))
        canvas.rect(x, top - 4, card_w, 4, fill=1, stroke=0)
        canvas.setFillColor(GREEN)
        canvas.setFont("DejaVuSans-Bold", 13.5)
        canvas.drawCentredString(x + card_w / 2, top - 33, value)
        canvas.setFillColor(HexColor("#4B5563"))
        canvas.setFont("DejaVuSans", 7.3)
        canvas.drawCentredString(x + card_w / 2, top - 52, label)
    canvas.setFillColor(MUTED)
    canvas.setFont("DejaVuSans", 8)
    canvas.drawString(
        MARGIN_X, 190,
        "Cifras de la ejecución guardada del notebook · 4 tareas · 4 algoritmos propios",
    )

    # Pie
    canvas.setStrokeColor(HexColor("#CBD5C8"))
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN_X, 58, PAGE_W - MARGIN_X, 58)
    canvas.setFont("DejaVuSans", 8.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 42, "Documento de estudio · Noviembre de 2026")
    canvas.drawRightString(
        PAGE_W - MARGIN_X, 42,
        "No sustituye al notebook, al póster ni al video",
    )
    canvas.restoreState()


def draw_body_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(HexColor("#D1D5DB"))
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, PAGE_H - 42, PAGE_W - MARGIN_X, PAGE_H - 42)
    canvas.setFont("DejaVuSans", 7.3)
    canvas.setFillColor(MUTED)
    canvas.drawString(
        MARGIN_X, PAGE_H - 36,
        "Teoría de Grafos · Universidad Industrial de Santander",
    )
    canvas.drawRightString(
        PAGE_W - MARGIN_X, PAGE_H - 36,
        "Guía de código y defensa",
    )

    canvas.line(MARGIN_X, 38, PAGE_W - MARGIN_X, 38)
    canvas.drawString(
        MARGIN_X, 26,
        "Proyecto final — Red de transferencias Ethereum ERC-20",
    )
    canvas.drawRightString(PAGE_W - MARGIN_X, 26, f"Página {doc.page}")
    canvas.restoreState()


def on_page(canvas, doc):
    if doc.page == 1:
        draw_cover(canvas, doc)
    else:
        draw_body_header_footer(canvas, doc)


# ---------------------------------------------------------------------------
# Constructores de flowables
# ---------------------------------------------------------------------------
class Builder:
    def __init__(self):
        self.story = []
        self.warnings = []

    def heading(self, level: int, text: str):
        # Evita que un título quede solo al final de la página.
        self.story.append(CondPageBreak(160 if level == 1 else 100))
        if level == 1:
            self.story.append(Paragraph(inline(text), H1))
            self.story.append(
                HRFlowable(
                    width="100%", thickness=1.8, color=GREEN,
                    spaceBefore=2, spaceAfter=9,
                )
            )
        elif level == 2:
            self.story.append(Paragraph(inline(text), H2))
        else:
            self.story.append(Paragraph(inline(text), H3))

    def paragraph(self, text: str):
        self.story.append(Paragraph(inline(text), BODY))

    def bullets(self, items: list[str], ordered: bool = False):
        for idx, item in enumerate(items, start=1):
            check = item.startswith("[ ] ")
            if check:
                item = item[4:]
            if check:
                style, marker = CHECK, "[ ]"
            else:
                style = NUMBER if ordered else BULLET
                marker = f"{idx}." if ordered else "\u2022"
            self.story.append(
                Paragraph(inline(item), style, bulletText=marker)
            )
        self.story.append(Spacer(1, 3))

    def callout(self, text: str):
        low = text.lower()
        if low.startswith("**ojo") or low.startswith("**cuidado"):
            bg, border = LIGHT_AMBER, AMBER
        elif low.startswith("**idea"):
            bg, border = LIGHT_GREEN, GREEN_2
        elif low.startswith("**si preguntan"):
            bg, border = LIGHT_BLUE, BLUE
        else:
            bg, border = LIGHT_GREEN, GREEN_2

        cell = Paragraph(inline(text), CALLOUT)
        t = Table([[cell]], colWidths=[CONTENT_W])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), bg),
                    ("BOX", (0, 0), (-1, -1), 0.4, border),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, border),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        self.story.append(KeepTogether([t, Spacer(1, 6)]))

    def code(self, code: str):
        lines = code.rstrip("\n").split("\n")
        chunk_size = 38
        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        for ci, chunk in enumerate(chunks):
            text = "\n".join(chunk)
            max_len = max((len(line) for line in chunk), default=1)
            size = 7.15
            usable = CONTENT_W - 14
            if max_len * 0.602 * size > usable:
                size = max(5.55, usable / (0.602 * max_len))
            st = ParagraphStyle(
                f"Code{ci}",
                fontName="DejaVuSansMono",
                fontSize=size,
                leading=size * 1.26,
                textColor=HexColor("#1F2937"),
            )
            pre = Preformatted(text, st)
            t = Table([[pre]], colWidths=[CONTENT_W])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F5F8F4")),
                        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
                        ("LINEBEFORE", (0, 0), (0, -1), 2.6, GREEN_2),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            t.hAlign = "LEFT"
            self.story.append(t)
            if ci < len(chunks) - 1:
                self.story.append(
                    Paragraph("<i>(continúa en el siguiente bloque)</i>", CAPTION)
                )
            self.story.append(Spacer(1, 5))

    def table(self, rows: list[str]):
        if not rows:
            return
        parsed = []
        has_header = False
        for idx, row in enumerate(rows):
            cells = [
                c.strip().replace("\\|", "|")
                for c in re.split(r"(?<!\\)\|", row.strip().strip("|"))
            ]
            if idx == 1 and all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                has_header = True
                continue
            parsed.append(cells)
        if not parsed:
            return
        ncols = max(len(r) for r in parsed)
        norm = [r + [""] * (ncols - len(r)) for r in parsed]
        small = ncols >= 6

        # Anchos proporcionales al contenido, con topes
        maxlens = []
        for c in range(ncols):
            lens = [len(strip_markup(r[c])) for r in norm]
            maxlens.append(max(6, min(44, max(lens) if lens else 6)))
        total = sum(maxlens)
        widths = [CONTENT_W * m / total for m in maxlens]

        # Evitar que una palabra se parta a la mitad: reservar el ancho de la
        # palabra más larga de cada columna.
        font_size = 7.2 if small else 7.6
        required = []
        for c in range(ncols):
            words = []
            for r in norm:
                words.extend(re.split(r"[\s/]+", strip_markup(r[c])))
            maxword = max((len(w) for w in words if w), default=4)
            required.append(maxword * 0.68 * font_size + 9)

        widths = [max(w, req) for w, req in zip(widths, required)]
        if sum(widths) > CONTENT_W:
            excess = sum(widths) - CONTENT_W
            slack = [max(0.0, w - req) for w, req in zip(widths, required)]
            total_slack = sum(slack)
            if total_slack > 0:
                widths = [
                    w - excess * (s / total_slack)
                    for w, s in zip(widths, slack)
                ]
            else:
                scale = CONTENT_W / sum(widths)
                widths = [w * scale for w in widths]
        # Ajuste final por redondeo
        scale = CONTENT_W / sum(widths)
        widths = [w * scale for w in widths]

        small = ncols >= 6
        head_style = TABLE_HEAD_SMALL if small else TABLE_HEAD
        body_style = TABLE_BODY_SMALL if small else TABLE_BODY

        data = []
        for ri, row in enumerate(norm):
            is_head = has_header and ri == 0
            style = head_style if is_head else body_style
            code_color = "#FFFFFF" if is_head else "#0F5132"
            data.append(
                [Paragraph(inline(c, code_color), style) if c else "" for c in row]
            )

        t = LongTable(data, colWidths=widths, repeatRows=1 if has_header else 0, hAlign="LEFT")
        style_cmds = [
            ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#D1D5DB")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ]
        if has_header:
            style_cmds += [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ]
            for ri in range(1, len(data)):
                if ri % 2 == 0:
                    style_cmds.append(("BACKGROUND", (0, ri), (-1, ri), HexColor("#F7FAF7")))
        t.setStyle(TableStyle(style_cmds))
        self.story.append(t)
        self.story.append(Spacer(1, 7))

    def image(self, caption: str, path: str):
        full = (BASE / path).resolve()
        if not full.exists():
            self.warnings.append(f"No existe la imagen: {full}")
            return
        iw, ih = ImageReader(str(full)).getSize()
        width = CONTENT_W
        height = width * ih / iw
        if height > 300:
            height = 300
            width = height * iw / ih
        img = Image(str(full), width=width, height=height)
        cap = Paragraph("<i>" + inline(caption) + "</i>", CAPTION)
        self.story.append(KeepTogether([Spacer(1, 3), img, Spacer(1, 1), cap, Spacer(1, 8)]))


# ---------------------------------------------------------------------------
# Parser Markdown
# ---------------------------------------------------------------------------
def parse(builder: Builder, paths: list[Path]):
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            raw = lines[i]
            s = raw.strip()
            if not s:
                i += 1
                continue
            if s == "<!-- pagebreak -->":
                # Solo salta de página si queda poco espacio; así se evitan
                # páginas casi vacías al final de una sección.
                builder.story.append(CondPageBreak(300))
                i += 1
                continue
            if s.startswith("```"):
                code = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code.append(lines[i])
                    i += 1
                i += 1
                builder.code("\n".join(code))
                continue
            if s.startswith("#"):
                level = len(s) - len(s.lstrip("#"))
                builder.heading(level, s[level:].strip())
                i += 1
                continue
            if s.startswith("|"):
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    rows.append(lines[i].strip())
                    i += 1
                builder.table(rows)
                continue
            if s.startswith(">"):
                quote = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote.append(lines[i].strip()[1:].strip())
                    i += 1
                builder.callout(" ".join(quote))
                continue
            if s.startswith("- "):
                items = []
                while i < len(lines) and lines[i].strip().startswith("- "):
                    items.append(lines[i].strip()[2:].strip())
                    i += 1
                builder.bullets(items, ordered=False)
                continue
            if re.match(r"^\d+\.\s", s):
                items = []
                while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                    items.append(re.sub(r"^\d+\.\s", "", lines[i].strip()))
                    i += 1
                builder.bullets(items, ordered=True)
                continue
            if s == "---":
                builder.story.append(
                    HRFlowable(
                        width="100%", thickness=0.6, color=HexColor("#D1D5DB"),
                        spaceBefore=5, spaceAfter=7,
                    )
                )
                i += 1
                continue
            if s.startswith("!["):
                m = re.match(r"!\[(.*?)\]\((.*?)\)", s)
                if m:
                    builder.image(m.group(1), m.group(2))
                    i += 1
                    continue

            para = [s]
            i += 1
            while i < len(lines):
                nxt = lines[i].strip()
                if (
                    not nxt
                    or nxt.startswith(("#", "|", ">", "- ", "```", "![", "<!--"))
                    or nxt == "---"
                    or re.match(r"^\d+\.\s", nxt)
                ):
                    break
                para.append(nxt)
                i += 1
            builder.paragraph(" ".join(para))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args()

    register_fonts()
    builder = Builder()

    # Portada: página vacía dibujada por on_page
    builder.story.append(Spacer(1, 1))
    builder.story.append(PageBreak())

    # Tabla de contenido
    toc = TableOfContents()
    toc.levelStyles = [TOC1, TOC2]
    toc.dotsMinLevel = 0
    builder.story.append(Paragraph("Tabla de contenido", TOC_TITLE))
    builder.story.append(toc)
    builder.story.append(PageBreak())

    parts = [
        "00_intro.md",
        "01_dataset.md",
        "02_t1.md",
        "03_t2.md",
        "04_t3.md",
        "05_t4.md",
        "06_global.md",
        "07_presentacion.md",
        "08_qa.md",
        "09_apendices.md",
    ]
    parse(builder, [BASE / p for p in parts])

    doc = GuideDoc(
        str(args.out),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=62,
        bottomMargin=52,
        title="Guía completa de código y defensa — Proyecto final Teoría de Grafos",
        author="Proyecto final — Universidad Industrial de Santander",
        subject="Red de transferencias Ethereum ERC-20: cuatro tareas de teoría de grafos",
        creator="Guía generada con ReportLab",
    )
    frame = Frame(
        MARGIN_X,
        52,
        CONTENT_W,
        PAGE_H - 62 - 52,
        id="normal",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=on_page)])
    doc.multiBuild(builder.story)

    if builder.warnings:
        print("Advertencias:")
        for w in builder.warnings:
            print(" -", w)
    print(f"PDF generado: {args.out.resolve()}")


if __name__ == "__main__":
    main()
