"""Build slides.pptx from slides.md (dark theme matching index.html)."""
import re, sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR

HERE = Path(__file__).parent
BG, SURF, LINE = RGBColor(0x0b,0x0e,0x14), RGBColor(0x13,0x18,0x22), RGBColor(0x23,0x2b,0x3a)
TEXT, MUTED, ACC, OK = RGBColor(0xe8,0xec,0xf3), RGBColor(0x8b,0x95,0xa8), RGBColor(0xff,0x6b,0x4a), RGBColor(0x3e,0xcf,0x8e)
SANS, MONO = "Calibri", "Consolas"
W, H = 13.333, 7.5
MX = 0.8

text = (HERE/"slides.md").read_text()
text = text.split("\n---\n", 2)[2] if text.startswith("---") else text
parts = re.split(r"\n---\n", text)
slides = [p.split("\n## See also")[0] for p in parts if re.search(r"^## Slide \d+ / \d+", p, re.M)]

def parse(block):
    lines = block.strip("\n").split("\n")
    m = re.match(r"## Slide (\d+) / (\d+) - (.*)", lines[0])
    d = dict(n=int(m[1]), total=int(m[2]), eyebrow=m[3], time="", items=[], notes=[])
    i = 1
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if re.fullmatch(r"\*\*\[[\d:]+\]\*\*", l.strip()):
            d["time"] = l.strip().strip("*[]"); i += 1; continue
        if l.startswith("```"):
            j = i+1; code = []
            while not lines[j].startswith("```"): code.append(lines[j]); j += 1
            d["items"].append(("code", "\n".join(code))); i = j+1; continue
        if l.startswith(">"):
            while i < len(lines) and lines[i].startswith(">"):
                d["notes"].append(re.sub(r"^>\s?(\*\*Speaker notes:\*\*\s*)?", "", lines[i])); i += 1
            continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.fullmatch(r"\|[-| ]+\|", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            d["items"].append(("table", rows)); continue
        if l.startswith("# "): d["items"].append(("h1", l[2:])); i += 1; continue
        if l.startswith("## "): d["items"].append(("h2", l[3:])); i += 1; continue
        if l.startswith("- "):
            b = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("  ")):
                if lines[i].startswith("- "): b.append(lines[i][2:])
                else: b[-1] += " " + lines[i].strip()
                i += 1
            d["items"].append(("bullets", b)); continue
        para = [l.strip()]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"(```|>|\||- |#)", lines[i]):
            para.append(lines[i].strip()); i += 1
        d["items"].append(("p", " ".join(para)))
    return d

def runs(p, s, size, color=TEXT, font=SANS, bold=False):
    for tok in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)", s):
        if not tok: continue
        r = p.add_run(); f = r.font; f.size = Pt(size); f.name = font; f.color.rgb = color; f.bold = bold
        if tok.startswith("**"): r.text = tok[2:-2]; f.bold = True
        elif tok.startswith("`"): r.text = tok[1:-1]; f.name = MONO; f.color.rgb = ACC
        elif tok.startswith("*"): r.text = tok[1:-1]; f.italic = True
        else: r.text = tok

def est_lines(s, size, width_in):
    cpl = max(10, width_in*72/(size*0.5))
    return sum(max(1, -(-len(x)//int(cpl))) for x in s.split("\n"))

def box(sl, x, y, w, h, fill=None, line=None):
    sh = sl.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    else: sh.fill.background()
    if line: sh.line.color.rgb = line; sh.line.width = Pt(1)
    else: sh.line.fill.background()
    sh.shadow.inherit = False
    return sh

def tb(sl, x, y, w, h):
    t = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = t.text_frame
    tf.word_wrap = True
    for a in ("margin_left","margin_right","margin_top","margin_bottom"): setattr(tf, a, 0)
    return tf

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(W), Inches(H)
blank = prs.slide_layouts[6]
CW = W - 2*MX

COLS = {9, 13, 14}

def render(sl, d, S):
    first = d["n"] == 1
    tf = tb(sl, MX, 0.4, 9, 0.3); runs(tf.paragraphs[0], d["eyebrow"].upper(), 11, ACC, MONO)
    tf = tb(sl, W-MX-3, 0.4, 3, 0.3); runs(tf.paragraphs[0], f'{d["time"]}  ·  {d["n"]}/{d["total"]}', 11, MUTED, MONO)
    tf.paragraphs[0].alignment = 3
    items = d["items"]
    y = 0.9 if not first else 2.2
    # split into heading, columns group, tail
    if d["n"] in COLS:
        hi = [k for k, (a, b) in enumerate(items) if a == "h2"][0]
        pre, rest = items[:hi+1], items[hi+1:]
        y = place(sl, d, pre, MX, y, CW, S)
        groups, cur, tail = [], None, []
        for it in rest:
            if it[0] == "p" and re.fullmatch(r"\*\*[^*]+\*\*", it[1]): cur = [it]; groups.append(cur)
            elif cur is not None and not tail and not (it[0] == "p" and it[1].startswith(("Private", "Does not", "*Source"))) and not (it[0]=="code"):
                cur.append(it)
            else: tail.append(it)
        gw = (CW-0.4)/2; ys = []
        for gi, g in enumerate(groups):
            x = MX + gi*(gw+0.4)
            ye = place(sl, d, g, x+0.25, y+0.2, gw-0.5, S, col=True)
            ys.append(ye)
        bot = max(ys)+0.2
        for gi in range(len(groups)):
            x = MX + gi*(gw+0.4)
            b = box(sl, x, y, gw, bot-y, None, OK if gi else ACC)
            if d["n"] == 9: b.line.color.rgb = ACC if gi else OK
            if d["n"] == 13: b.line.color.rgb = OK if gi else ACC
            if d["n"] == 14: b.line.color.rgb = LINE
            sp = b._element; sp.getparent().remove(sp); sl.shapes._spTree.insert(2, sp)
        y = place(sl, d, tail, MX, bot+0.25, CW, S)
    else:
        y = place(sl, d, items, MX, y, CW, S)
    return y

def place(sl, d, items, X, y, CWd, S, col=False):
    for kind, val in items:
        if kind in ("h1", "h2"):
            size = (44 if kind == "h1" else (32 if est_lines(val, 32, CWd) <= 2 else 28))*S
            n = est_lines(val, size, CWd*0.95); h = n*size*1.2/72
            tf = tb(sl, X, y, CWd, h); runs(tf.paragraphs[0], val, size, TEXT, SANS, True); y += h + 0.25*S
        elif kind == "p":
            size, col_ = 22*S, TEXT
            if val.startswith("*Source"): size, col_ = 11*S, MUTED
            big = re.fullmatch(r"\*\*[^*]+\*\*", val) and len(val) < 20 and not col
            if big: size, col_ = 60*S, ACC
            if re.fullmatch(r"\*\*[^*]+\*\*", val) and col: size = 22*S
            if val.startswith("Lewis Sawe"): col_ = MUTED
            h = est_lines(val, size, CWd)*size*1.35/72
            tf = tb(sl, X, y, CWd, h); runs(tf.paragraphs[0], val, size, col_, SANS, bool(big)); y += h + 0.18*S
        elif kind == "bullets":
            fs = 24*S; tf = tb(sl, X, y, CWd, 1); h = 0
            for k, b in enumerate(val):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                p.space_after = Pt(8*S)
                runs(p, "→  ", fs, ACC, MONO); runs(p, b, fs)
                h += est_lines("→  "+b, fs, CWd)*fs*1.3/72 + 8*S/72
            y += h + 0.15*S
        elif kind == "code":
            sz = (18 if len(val.split("\n")) <= 8 else 14)*S
            lines_n = sum(max(1, -(-len(x)//int((CWd-0.6)*72/(sz*0.6)))) for x in val.split("\n"))
            h = lines_n*sz*1.35/72 + 0.4
            box(sl, X, y, CWd, h, SURF, LINE)
            tf = tb(sl, X+0.25, y+0.2, CWd-0.5, h-0.4)
            inb = False
            for k, ln in enumerate(val.split("\n")):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                if "<IMPORTANT>" in ln: inb = True
                c = MUTED if ln.strip().startswith("#") else (ACC if d["n"] == 5 and inb else TEXT)
                if "</IMPORTANT>" in ln: inb = False
                runs(p, ln or " ", sz, c, MONO)
            y += h + 0.2*S
        elif kind == "table":
            rows, cols = len(val), len(val[0])
            wts = [1.2, 3.6, 1.0] if (cols == 3 and d["n"] == 10) else [1.0]*cols
            tot = sum(wts); sz = (14 if d["n"] == 10 else 18)*S
            rh = (0.62 if d["n"] == 10 else 0.5)*S
            gt = sl.shapes.add_table(rows, cols, Inches(X), Inches(y), Inches(CWd), Inches(rh*rows))
            tbl = gt.table
            tblPr = gt._element.graphic.graphicData.tbl.tblPr
            tblPr.set("bandRow", "0"); tblPr.set("firstRow", "0")
            for c in range(cols): tbl.columns[c].width = Inches(CWd*wts[c]/tot)
            from pptx.oxml.ns import qn
            from lxml import etree
            for r in range(rows):
                tbl.rows[r].height = Inches(rh)
                for c in range(cols):
                    cell = tbl.cell(r, c); cell.fill.solid()
                    cell.fill.fore_color.rgb = SURF if r else LINE
                    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                    cell.margin_left = cell.margin_right = Inches(0.1)
                    cell.margin_top = cell.margin_bottom = Inches(0.03)
                    tcPr = cell._tc.get_or_add_tcPr()
                    for tag in ("a:lnL","a:lnR","a:lnT","a:lnB"):
                        ln = etree.SubElement(tcPr, qn(tag), w="9525")
                        sf = etree.SubElement(ln, qn("a:solidFill")); etree.SubElement(sf, qn("a:srgbClr"), val="232B3A")
                    tcPr.insert(0, tcPr[-4]) if False else None
                    p = cell.text_frame.paragraphs[0]; cell.text_frame.word_wrap = True
                    runs(p, val[r][c], sz, MUTED if r == 0 else TEXT, SANS, r == 0)
            y += rh*rows + 0.25*S
    return y

for blk in slides:
    d = parse(blk)
    S = 1.0
    while S > 0.55:
        scratch = Presentation(); scratch.slide_width, scratch.slide_height = Inches(W), Inches(H)
        if render(scratch.slides.add_slide(blank), d, S) <= H - 0.45: break
        S -= 0.05
    sl = prs.slides.add_slide(blank)
    sl.background.fill.solid(); sl.background.fill.fore_color.rgb = BG
    y = render(sl, d, S)
    if S < 1: print(f"slide {d['n']}: scale {S:.2f}, y={y:.1f}")
    sl.notes_slide.notes_text_frame.text = "\n".join(d["notes"])

out = HERE/"slides.pptx"; prs.save(out); print("saved", out, len(slides), "slides")
