#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convertit guide-crash-course-ia.md en PDF A4 soigné (fpdf2), avec pagination des tableaux."""
import re

from fpdf import FPDF

SRC = "guide-crash-course-ia.md"
OUT = "guide-crash-course-ia.pdf"

F_REG  = "C:/Windows/Fonts/segoeui.ttf"
F_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
F_ITAL = "C:/Windows/Fonts/segoeuii.ttf"
F_MONO = "C:/Windows/Fonts/cour.ttf"
F_EMOJI= "C:/Windows/Fonts/seguiemj.ttf"

INK    = (31, 41, 55)
MUTED  = (107, 114, 128)
PRIMARY= (30, 58, 95)
ACCENT = (217, 119, 6)
LIGHT  = (241, 245, 249)
BORDER = (222, 226, 231)
CODEBG = (243, 244, 246)
PAGEBOT = 272  # bas utile avant déclenchement saut de page

# ------------------------------------------------------------------ parsing
EMOJIS = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2190-\u21FF\uFE0F\u200D]"
)

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+`|\[[^\]]*\]\([^)]+\))", re.S)

def split_emoji(text):
    """Découpe un texte en segments (emoji / non-emoji). Chaque segment garde son style."""
    parts, buf, cur = [], "", None
    for ch in text:
        is_e = bool(EMOJIS.match(ch))
        if cur is None or is_e != cur:
            if buf:
                parts.append((buf, cur))
            buf, cur = "", is_e
        buf += ch
    if buf:
        parts.append((buf, cur))
    return parts

def inline_runs(text):
    """Renvoie [(texte, style)] ; style ∈ {'', 'B', 'I', 'CODE'}. Les émojis restent dans le texte."""
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append((part[2:-2], "B"))
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            out.append((part[1:-1], "I"))
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append((part[1:-1], "CODE"))
        elif part.startswith("[") and "](" in part:
            out.append((part[1:part.index("]")], ""))
        else:
            out.append((part, ""))
    return out

def strip_md(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text

def strip_emoji(text):
    return re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u2190-\u21FF]", "", text).strip(" \u2014\u2013-\ufeff")

def html_unescape(s):
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

def parse_blocks(md_lines):
    blocks, i, n = [], 0, len(md_lines)
    while i < n:
        line = md_lines[i]
        if line.startswith("```"):
            j = i + 1
            while j < n and not md_lines[j].startswith("```"):
                j += 1
            blocks.append(("code", "\n".join(md_lines[i+1:j])))
            i = j + 1; continue
        if line.startswith("#"):
            h = len(line) - len(line.lstrip("#"))
            blocks.append(("h", (h, line[h:].strip()))); i += 1; continue
        if line.startswith("|"):
            rows = []
            while i < n and md_lines[i].startswith("|"):
                rows.append([c.strip() for c in md_lines[i].strip().strip("|").split("|")])
                i += 1
            if len(rows) > 1 and set(rows[1].__str__()) <= set("-: "):
                rows = rows[:1] + rows[2:]
            blocks.append(("table", rows)); continue
        if line.startswith(">"):
            lines = []
            while i < n and md_lines[i].startswith(">"):
                lines.append(md_lines[i][1:].strip()); i += 1
            blocks.append(("quote", " ".join(lines))); continue
        if re.match(r"^ {0,3}(- |\+ |\d+\.) ", line):
            items, j = [], i
            while j < n and re.match(r"^ {0,3}(- |\+ |\d+\.) ", md_lines[j]):
                m = re.match(r"^( {0,3})(?:- |\+ |(\d+\.) )(.*)$", md_lines[j])
                items.append((len(m.group(1)) // 2, bool(m.group(2)), m.group(3)))
                j += 1
            blocks.append(("list", items)); i = j; continue
        if set(line.strip()) == {"-"}:
            i += 1; continue
        if line.strip() == "":
            i += 1; continue
        blocks.append(("p", line.strip())); i += 1
    # fusionne les paragraphes adjacents non rares
    merged, buf = [], ""
    for kind, payload in blocks:
        if kind == "p":
            buf = (buf + " " + payload).strip()
        else:
            if buf:
                merged.append(("p", buf)); buf = ""
            merged.append((kind, payload))
    if buf:
        merged.append(("p", buf))
    return merged

# ------------------------------------------------------------------ rendu
class Doc(FPDF):
    def __init__(self):
        super().__init__(unit="mm", format="A4")
        self.add_font("G", "", F_REG, uni=True)
        self.add_font("G", "B", F_BOLD, uni=True)
        self.add_font("G", "I", F_ITAL, uni=True)
        self.add_font("C", "", F_MONO, uni=True)
        self.add_font("E", "", F_EMOJI, uni=True)
        self.set_margins(18, 20, 18)
        self.set_auto_page_break(True, margin=22)

    def font(self, style):
        if style == "CODE":
            self.set_font("C", "", 8.4)
        elif style == "B":
            self.set_font("G", "B", 10)
        elif style == "I":
            self.set_font("G", "I", 10)
        else:
            self.set_font("G", "", 10)
        self.set_text_color(*INK)

    def footer(self):
        if self.page == 1:
            return
        self.set_y(-14)
        self.set_draw_color(*BORDER); self.set_line_width(0.3)
        self.line(18, self.get_y(), 210 - 18, self.get_y())
        self.set_font("G", "", 8); self.set_text_color(*MUTED)
        self.cell(0, 8, "Guide Crash Course IA — du zéro à la salle de classe", align="L")
        self.cell(0, 8, f"Page {self.page}", align="R")

def tok_w(pdf, tt, style):
    pdf.font(style)
    if any(EMOJIS.match(c) for c in tt):
        pdf.set_font("E", "", 9.5)
    w = pdf.get_string_width(tt)
    pdf.font(style)
    return w

def wrap_lines(runs, max_w, pdf):
    tokens = []
    for t, s in runs:
        for p in re.split(r"( )", t):
            if p:
                tokens.append((p, s))
    lines, cur, cur_w = [], [], 0
    for tt, s in tokens:
        w = tok_w(pdf, tt, s)
        if cur and cur_w + w > max_w:
            lines.append(cur); cur, cur_w = [], 0
        cur.append((tt, s)); cur_w += w
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(pdf, runs, x, y, max_w, line_h=4.9):
    lines = wrap_lines(runs, max_w, pdf)
    cy = y
    for line in lines:
        cx = x
        for tt, s in line:
            pdf.font(s)
            w = tok_w(pdf, tt, s)
            pdf.set_xy(cx, cy - line_h + 3.3)
            if any(EMOJIS.match(c) for c in tt):
                pdf.set_font("E", "", 9.5)
            pdf.cell(w, line_h, tt, new_x="LMARGIN", new_y="TOP")
            cx += w
        cy += line_h
    pdf.set_xy(x, cy)
    return line_h * len(lines)

def cell_h(pdf, text, w, size=9.5):
    pdf.set_font("G", "", size)
    words = text.split(" ") or [""]
    lines, cur = 1, ""
    for word in words:
        trial = (cur + " " + word).strip()
        if pdf.get_string_width(trial) <= w - 3:
            cur = trial
        else:
            lines += 1; cur = word
    return lines * 4.55 + 3.2

def row_height(pdf, row, widths):
    return max(cell_h(pdf, strip_md(html_unescape(row[ci] if ci < len(row) else "")), widths[ci])
               for ci in range(len(widths)))

def table_widths(rows, ncols):
    frame = 210 - 36
    m = [0] * ncols
    for r in rows:
        for ci in range(ncols):
            c = r[ci] if ci < len(r) else ""
            m[ci] = max(m[ci], len(strip_md(html_unescape(c))))
    tot = sum(m) or 1
    return [frame * x / tot for x in m]

def draw_row_cells(pdf, row, widths, y_abs, bold=False):
    cx = 18
    for ci in range(len(widths)):
        cell = row[ci] if ci < len(row) else ""
        pdf.font("B" if bold else "")
        if bold:
            pdf.set_font("G", "B", 9.3); pdf.set_text_color(*PRIMARY)
        else:
            pdf.set_font("G", "", 9.3); pdf.set_text_color(*INK)
        draw_wrapped(pdf, inline_runs(strip_md(html_unescape(cell))),
                     cx + 1.7, y_abs + 1.6, widths[ci] - 3.4, line_h=4.5)
        cx += widths[ci]

def draw_table(pdf, rows):
    """Tableau paginé avec répétition de l'en-tête et bordures par segment."""
    ncols = max(len(r) for r in rows)
    widths = table_widths(rows, ncols)
    fw = sum(widths)
    header, body = rows[0], rows[1:]

    def frame_seg(y0, y1, header_row=False):
        pdf.set_draw_color(*BORDER); pdf.set_line_width(0.25)
        pdf.line(18, y0, 18 + fw, y0)
        pdf.line(18, y1, 18 + fw, y1)
        pdf.line(18, y0, 18, y1)
        pdf.line(18 + fw, y0, 18 + fw, y1)
        cx = 18
        for w in widths[:-1]:
            cx += w
            pdf.line(cx, y0, cx, y1)
        if header_row:
            pdf.set_draw_color(*PRIMARY); pdf.set_line_width(0.5)
            pdf.line(18, y1, 18 + fw, y1)

    def render_header(y0):
        hh = row_height(pdf, header, widths)
        pdf.set_fill_color(*LIGHT)
        pdf.rect(18, y0, fw, hh, "DF")
        cur_y = pdf.get_y()
        draw_row_cells(pdf, header, widths, y0, bold=True)
        pdf.set_y(cur_y)
        return hh

    # en-tête initial
    if pdf.get_y() + 6 > PAGEBOT:
        pdf.add_page()
    y_top = pdf.get_y()
    seg = render_header(y_top)
    seg_bottom = y_top + seg

    for ri, r in enumerate(body):
        hh = row_height(pdf, r, widths)
        if seg_bottom + hh > PAGEBOT:
            frame_seg(y_top, seg_bottom, header_row=True)
            pdf.add_page()
            y_top = pdf.get_y()
            seg = render_header(y_top)
            seg_bottom = y_top + seg
        if ri % 2 == 1:
            pdf.set_fill_color(249, 250, 252)
            pdf.rect(18, seg_bottom, fw, hh, "F")
        cur_y = pdf.get_y()
        draw_row_cells(pdf, r, widths, seg_bottom)
        pdf.set_y(cur_y)
        seg_bottom += hh
    frame_seg(y_top, seg_bottom)
    pdf.set_y(seg_bottom + 3.5)
    pdf.set_text_color(*INK)

def render_blocks(pdf, blocks, log=None):
    if log is None:
        log = []
    for kind, payload in blocks:
        if kind == "h":
            level, text = payload
            t = strip_md(text)
            if "GUIDE CRASH COURSE" in strip_emoji(t).upper():
                continue
            if level == 1:
                pdf.add_page()
                pdf.set_font("G", "B", 14); pdf.set_text_color(*ACCENT)
                pdf.cell(0, 9, t, new_x="LMARGIN", new_y="NEXT"); pdf.ln(4.5)
                pdf.set_font("G", "", 10); pdf.set_text_color(*INK)
                log.append((t, pdf.page))
            elif level == 2:
                if pdf.get_y() > 60:
                    pdf.add_page()
                pdf.ln(4)
                pdf.set_font("G", "B", 11.5); pdf.set_text_color(*PRIMARY)
                pdf.cell(0, 7.2, t, new_x="LMARGIN", new_y="NEXT"); pdf.ln(1.5)
                pdf.set_text_color(*INK)
                log.append((t, pdf.page))
            else:
                pdf.ln(2.5)
                pdf.set_font("G", "B", 10.5); pdf.set_text_color(*INK)
                pdf.cell(0, 6, t, new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(*PRIMARY)
                pdf.set_font("G", "", 10)
        elif kind == "p":
            runs = inline_runs(payload)
            draw_wrapped(pdf, runs, pdf.get_x(), pdf.get_y(), 210 - 36)
            pdf.ln(1.8)
        elif kind == "list":
            for depth, ordered, text in payload:
                x = 18 + 6 + depth * 7
                pdf.set_x(x)
                pdf.set_font("G", "", 10)
                pdf.set_text_color(*ACCENT if not ordered else MUTED)
                pdf.cell(4.2, 4.9, "•" if not ordered else "–", new_x="RIGHT")
                pdf.set_text_color(*INK)
                draw_wrapped(pdf, inline_runs(text), x + 4.2, pdf.get_y(), 210 - 18 - (x + 4.2))
                pdf.ln(0.8)
            pdf.ln(1.4)
        elif kind == "quote":
            runs = inline_runs(payload)
            lines = wrap_lines(runs, pdf.w - 36 - 8, pdf)
            h = len(lines) * 4.9 + 4
            if pdf.get_y() + h > PAGEBOT:
                pdf.add_page()
            y0 = pdf.get_y()
            pdf.set_fill_color(246, 250, 246); pdf.set_draw_color(190, 230, 190)
            pdf.rect(18, y0 + 0.6, pdf.w - 36, h, style="DF")
            draw_wrapped(pdf, runs, 18 + 4, y0 + 2.2, pdf.w - 36 - 8)
        elif kind == "code":
            clines = payload.split("\n")
            lh = 4.35
            h = len(clines) * lh + 5.6
            if pdf.get_y() + h > PAGEBOT + 8:
                pdf.add_page()
            y0 = pdf.get_y()
            pdf.set_fill_color(*CODEBG)
            pdf.rect(18, y0, 210 - 36, h, "F")
            pdf.set_xy(18 + 3.4, y0 + 2.9)
            pdf.set_font("C", "", 8.4); pdf.set_text_color(40, 54, 72)
            for cl in clines:
                if pdf.get_x() > 150:
                    pdf.ln()
                pdf.cell(0, lh, cl, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*INK)
            pdf.set_y(y0 + h + 3)
        elif kind == "table":
            draw_table(pdf, payload)

def cover_and_summary(pdf, toc):
    # page de garde
    pdf.add_page()
    pdf.set_fill_color(*PRIMARY)
    pdf.rect(0, 0, 210, 66, "F")
    pdf.set_xy(18, 40)
    pdf.set_font("G", "B", 27); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Guide Crash Course IA")
    pdf.set_font("G", "", 13); pdf.set_text_color(210, 222, 235); pdf.ln(7)
    pdf.cell(0, 8, "Du zéro à la salle de classe — ML, vibe coding, MCP, CLI, agents, théorie des jeux")
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 66, 210, 2.2, "F")
    pdf.set_xy(18, 96)
    pdf.set_text_color(*MUTED); pdf.set_font("G", "", 10.5)
    for l in ["•  Niveau : débutant (aucune maths lourdes)",
              "•  ~60 concepts expliqués simplement + glossaire A–Z",
              "•  Plan d'étude de 4 semaines inclus"]:
        pdf.cell(0, 6.5, l, new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(18, 118)
    pdf.set_text_color(*PRIMARY); pdf.set_font("G", "B", 11)
    pdf.cell(0, 7, "Ce qu'il y a dedans", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*INK); pdf.set_font("G", "", 9.5)
    items = [("Module 0", "Carte du territoire"),
             ("Module 1", "IA / Machine Learning / Deep Learning"),
             ("Module 2", "Les modèles de langage (LLM)"),
             ("Module 3", "Vibe coding"),
             ("Module 4", "MCP — les connecteurs de l'IA"),
             ("Module 5", "CLI — la sacoche de survie"),
             ("Module 6", "Agents et agentic"),
             ("Module 7", "Théorie des jeux (2 minutes)"),
             ("+", "Sommaire, glossaire A–Z, ressources gratuites")]
    for t, d in items:
        pdf.set_x(18); pdf.set_font("G", "B", 9.5); pdf.set_text_color(*PRIMARY)
        pdf.cell(30, 5.4, t, new_x="RIGHT")
        pdf.set_font("G", "", 9.5); pdf.set_text_color(*INK)
        pdf.cell(0, 5.4, d, new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(18, 265)
    pdf.set_font("G", "", 8.5); pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, "Mis à jour octobre 2026 · source : guide-crash-course-ia.md", new_x="LMARGIN", new_y="NEXT")

    # sommaire
    pdf.add_page()
    pdf.set_font("G", "B", 20); pdf.set_text_color(*PRIMARY)
    pdf.cell(0, 11, "Sommaire", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*BORDER); pdf.set_line_width(0.4)
    y = pdf.get_y() + 2
    pdf.set_y(y)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y()); pdf.ln(5)
    for title, page in toc:
        pdf.set_xy(18, pdf.get_y())
        pdf.set_text_color(*INK); pdf.set_font("G", "", 10)
        w = pdf.get_string_width(strip_emoji(title))
        # titre (emoji retraité)
        pdf.set_font("G", "", 10)
        pdf.cell(w, 5.8, strip_emoji(title), new_x="RIGHT", new_y="TOP")
        yline = pdf.get_y() + 4.1
        pdf.set_draw_color(205, 213, 222); pdf.set_line_width(0.25)
        pdf.line(pdf.get_x() + 2, yline, 190, yline)
        pn = str(page)
        pdf.set_font("G", "B", 10); pdf.set_text_color(*PRIMARY)
        pdf.set_x(190 - pdf.get_string_width(pn) - 1)
        pdf.cell(pdf.get_string_width(pn) + 1, 5.8, pn, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*INK)
    pdf.ln(4)
    pdf.set_font("G", "I", 9.5); pdf.set_text_color(*MUTED)
    pdf.multi_cell(0, 5.2, "Astuce : dans ton lecteur PDF, Ctrl+F (Chercher) pour retrouver un terme en une seconde. "
                           "Le glossaire commence à la page marquée « Glossaire ».")

# ------------------------------------------------------------------ build
with open(SRC, encoding="utf-8") as f:
    BLOCKS = parse_blocks(f.read().split("\n"))

pdf_pass1 = Doc()
pdf_pass1.add_page()
LOG = []
render_blocks(pdf_pass1, BLOCKS, log=LOG)
P1 = [(t, p) for t, p in LOG if strip_emoji(t).startswith(("Module", "Glossaire", "Plan", "Ressources"))]

final_toc = [(t, p + 2) for t, p in P1]
for t, p in final_toc:
    print("  %-58s -> %d" % (strip_emoji(t), p))

pdf = Doc()
cover_and_summary(pdf, final_toc)
LOG2 = []
render_blocks(pdf, BLOCKS, log=None)
pdf.output(OUT)
print("PDF OK ->", OUT, "| pages:", pdf.page)
