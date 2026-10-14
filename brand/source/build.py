"""PostShor identity: symbol, wordmark (Geist SemiBold outlines), lockups, avatar, social preview."""
import math, pathlib, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

OUT = pathlib.Path(sys.argv[1]); FONTS = OUT / "fonts"; ASSETS = OUT / "assets"; ASSETS.mkdir(exist_ok=True)
MIDNIGHT, DAYBREAK, PAPER, SLATE, GRID = "#0B0E14", "#FFA630", "#F4F1EA", "#6B7385", "#161B26"
ANGLE = 20.0; SHEAR = math.tan(math.radians(ANGLE)); K = 0.42   # stroke weight in lattice units

# ---------------------------------------------------------------- symbol
def symbol(ox, oy, u, fg, accent):
    """Leaning P on a 20-degree lattice. (ox, oy) = origin (bottom-left), u = lattice unit in px.
    Total height = (2 + K) * u. The counter is exactly one lattice cell; the origin cell is Daybreak."""
    def pt(x, y): return (ox + (x + y*SHEAR)*u, oy - y*u)
    def path(pts): return "M" + " L".join(f"{a:.2f},{b:.2f}" for a, b in map(lambda p: pt(*p), pts)) + " Z"
    outer = [(0,0),(K,0),(K,1),(1+K,1),(1+K,2+K),(0,2+K)]
    hole = [(K,1+K),(1,1+K),(1,2),(K,2)]
    foot = [(0,0),(K,0),(K,K),(0,K)]
    return (f'<path d="{path(outer)} {path(hole)}" fill="{fg}" fill-rule="evenodd"/>'
            f'<path d="{path(foot)}" fill="{accent}"/>')

def symbol_width(u): return (1 + K + (2 + K)*SHEAR) * u
def symbol_height(u): return (2 + K) * u

# ---------------------------------------------------------------- wordmark
src = TTFont(FONTS / "Geist[wght].ttf")
semibold = instantiateVariableFont(src, {"wght": 600}); semibold.save(OUT / "Geist-SemiBold.ttf")
regular = instantiateVariableFont(TTFont(FONTS / "Geist[wght].ttf"), {"wght": 400}); regular.save(OUT / "Geist-Regular.ttf")
mono = instantiateVariableFont(TTFont(FONTS / "GeistMono[wght].ttf"), {"wght": 500}); mono.save(OUT / "GeistMono-Medium.ttf")
FACES = {"semibold": (semibold, "Geist-SemiBold.ttf"), "regular": (regular, "Geist-Regular.ttf"), "mono": (mono, "GeistMono-Medium.ttf")}
UPM = semibold["head"].unitsPerEm
CAP = semibold["OS/2"].sCapHeight
gs = semibold.getGlyphSet()

def wordmark(text, x, baseline, cap_px, fill, tracking=-0.015, weight="semibold"):
    """Shape with HarfBuzz (real kerning), emit glyph outlines as one SVG path."""
    ttf, fname = FACES[weight]; gs = ttf.getGlyphSet(); CAP = ttf["OS/2"].sCapHeight; UPM = ttf["head"].unitsPerEm
    face = hb.Face(hb.Blob.from_file_path(str(OUT / fname))); font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(font, buf, {"kern": True, "liga": True})
    s = cap_px / CAP; pen_x = 0.0; d = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = ttf.getGlyphName(info.codepoint)
        sp = SVGPathPen(gs)
        gs[name].draw(TransformPen(sp, (s, 0, 0, -s, x + (pen_x + pos.x_offset)*s, baseline - pos.y_offset*s)))
        d.append(sp.getCommands())
        pen_x += pos.x_advance + tracking*UPM
    return f'<path d="{" ".join(d)}" fill="{fill}"/>', pen_x*s

def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{rect}{body}</svg>'

# ---------------------------------------------------------------- lockup geometry (the alignment system)
# Wordmark cap height = lattice unit u: the "Shor" cap S and the symbol's bowl are the same height.
# Symbol baseline = wordmark baseline. Gap between symbol and wordmark = 2 x origin cell (2K u).
def lockup(u, fg, accent, pad):
    """Alignment system: wordmark cap height = 1 lattice cell (u); wordmark optically centred on the
    symbol (cap-height centre = symbol centre); gap = 1 origin cell (K u) from the symbol's widest point."""
    sw, sh = symbol_width(u), symbol_height(u)
    cap = u
    sym_base = pad + sh
    baseline = sym_base - sh/2 + cap/2
    gap = K*u
    word, ww = wordmark("PostShor", pad + sw + gap, baseline, cap, fg)
    w = pad + sw + gap + ww + pad
    return w, sh + 2*pad, symbol(pad, sym_base, u, fg, accent) + word

def lattice_texture(w, h, u, ox, oy, color=GRID, width=1.2):
    """Faint 20-degree lattice lines: the brand pattern."""
    lines = []
    for i in range(-40, 60):
        x = ox + i*u
        lines.append(f'<line x1="{x - 2*h*SHEAR:.1f}" y1="{oy + 2*h:.1f}" x2="{x + 2*h*SHEAR:.1f}" y2="{oy - 2*h:.1f}" stroke="{color}" stroke-width="{width}"/>')
    for j in range(-20, 20):
        y = oy - j*u
        lines.append(f'<line x1="0" y1="{y:.1f}" x2="{w}" y2="{y:.1f}" stroke="{color}" stroke-width="{width}"/>')
    return "".join(lines)

files = {}
# symbol (square, light & dark) and avatar
for name, bg, fg in (("symbol-dark", MIDNIGHT, PAPER), ("symbol-light", PAPER, MIDNIGHT)):
    u = 150; sw, sh = symbol_width(u), symbol_height(u)
    files[name] = svg(512, 512, symbol((512-sw)/2, (512+sh)/2, u, fg, DAYBREAK), bg)
files["symbol-transparent"] = svg(round(symbol_width(100)), round(symbol_height(100)), symbol(0, symbol_height(100), 100, MIDNIGHT, DAYBREAK))
files["avatar"] = files["symbol-dark"]

# lockups
for name, bg, fg in (("lockup-dark", MIDNIGHT, PAPER), ("lockup-light", PAPER, MIDNIGHT)):
    w, h, body = lockup(60, fg, DAYBREAK, pad=60)
    files[name] = svg(round(w), round(h), body, bg)
w, h, body = lockup(60, MIDNIGHT, DAYBREAK, pad=0); files["lockup-transparent"] = svg(math.ceil(w), math.ceil(h), body)

# wordmark only
word, ww = wordmark("PostShor", 0, 100, 100, MIDNIGHT); files["wordmark"] = svg(math.ceil(ww), 100, word)

# social preview 1280x640
texture = lattice_texture(1280, 640, 64, 0, 640)
u = 64
w, h, body = lockup(u, PAPER, DAYBREAK, pad=0)
lx, ly = 112, 158
t1 = wordmark("Find quantum-vulnerable cryptography.", lx, ly + h + 86, 30, "#C9CEDA", tracking=0, weight="regular")[0]
t2 = wordmark("Plan the migration to post-quantum.", lx, ly + h + 134, 30, "#C9CEDA", tracking=0, weight="regular")[0]
cmd = wordmark("$ pip install postshor", lx, 548, 19, DAYBREAK, tracking=0, weight="mono")[0]
url, uw = wordmark("github.com/postshor", 0, 548, 17, "#9AA1B0", tracking=0, weight="regular")
files["social-preview"] = svg(1280, 640, texture + f'<g transform="translate({lx},{ly})">{body}</g>' + t1 + t2 + cmd
                              + f'<g transform="translate({1168 - uw:.1f},0)">{url}</g>', MIDNIGHT)

for name, content in files.items():
    (ASSETS / f"{name}.svg").write_text(content, encoding="utf-8")
    (ASSETS / f"{name}.html").write_text(f'<!doctype html><body style="margin:0;background:transparent">{content}</body>', encoding="utf-8")
print("\n".join(f"{n} {c[c.index('width=')+7:c.index(chr(34), c.index('width=')+7)]}x{c[c.index('height=')+8:c.index(chr(34), c.index('height=')+8)]}" for n, c in files.items()))

# ---------------------------------------------------------------- construction diagram
def construction():
    u = 132; W, H = 1040, 560; ox, oy = 150, 450
    def pt(x, y): return (ox + (x + y*SHEAR)*u, oy - y*u)
    grid, dots, notes = [], [], []
    for i in range(-1, 5):
        a, b = pt(i, -0.5), pt(i, 2.95)
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    for j in (0, 1, 2, 2+K, K, 1+K):
        a, b = pt(-0.9, j), pt(3.6 - j*SHEAR, j)
        dash = ' stroke-dasharray="6 6"' if j not in (0, 1, 2) else ""
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"{dash}/>')
    for i in range(0, 4):
        for j in range(0, 3):
            x, y = pt(i, j); dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5"/>')
    o, e1, e2 = pt(0, 0), pt(1, 0), pt(0, 1)
    vec = "".join(f'<line x1="{o[0]:.1f}" y1="{o[1]:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E5484D" stroke-width="3.5" marker-end="url(#arr)"/>' for x, y in (e1, e2))
    vec += f'<text x="{e1[0]-8:.1f}" y="{e1[1]+36:.1f}" fill="#E5484D">b₁</text><text x="{e2[0]-44:.1f}" y="{e2[1]+8:.1f}" fill="#E5484D">b₂</text>'
    top = pt(0, 2.75)
    vec += f'<line x1="{o[0]:.1f}" y1="{o[1]:.1f}" x2="{o[0]:.1f}" y2="{top[1]:.1f}" stroke="#6B7385" stroke-width="2" stroke-dasharray="4 6"/>'
    vec += f'<text x="{o[0]-58:.1f}" y="{top[1]+24:.1f}" fill="#6B7385">20°</text>'
    legend = [("u", "lattice unit: one cell"), ("20°", "forward shear: the signature angle"), ("K = 0.42 u", "stroke weight"),
              ("1 cell", "the counter (inner space)"), ("K × K", "origin cell, in Daybreak"), ("b₁, b₂", "basis vectors of the lattice")]
    lx = 700
    for n, (k, v) in enumerate(legend):
        y = 120 + n*58
        notes.append(f'<text x="{lx}" y="{y}" font-weight="600" fill="{MIDNIGHT}">{k}</text><text x="{lx}" y="{y+24}" fill="#6B7385" font-size="19">{v}</text>')
    defs = '<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#E5484D"/></marker></defs>'
    body = (defs + symbol(ox, oy, u, MIDNIGHT, DAYBREAK)
            + '<clipPath id="area"><rect width="660" height="560"/></clipPath>'
            + f'<g clip-path="url(#area)" stroke="#9C968A" stroke-width="1.2" opacity="0.75">{"".join(grid)}</g>'
            + f'<g fill="#9C968A">{"".join(dots)}</g>'
            + f'<g font-family="Geist, sans-serif" font-size="22">{vec}{"".join(notes)}</g>')
    return svg(W, H, body, PAPER)

c = construction()
(ASSETS / "construction.svg").write_text(c, encoding="utf-8")
(ASSETS / "construction.html").write_text(f'<!doctype html><body style="margin:0">{c}</body>', encoding="utf-8")


# ---------------------------------------------------------------- misuse sheet ("don't")
def misuse():
    u = 52; cw, ch = 300, 230
    def tile(n, inner, label):
        x = 20 + (n % 4)*(cw + 20)
        return (f'<g transform="translate({x},20)"><rect width="{cw}" height="{ch}" rx="10" fill="{PAPER}"/>{inner}'
                f'<line x1="{cw-46}" y1="16" x2="{cw-16}" y2="46" stroke="#E5484D" stroke-width="5"/><line x1="{cw-16}" y1="16" x2="{cw-46}" y2="46" stroke="#E5484D" stroke-width="5"/>'
                f'<text x="16" y="{ch-18}" font-family="Geist, sans-serif" font-size="19" fill="{MIDNIGHT}">{label}</text></g>')
    sym = lambda fg=MIDNIGHT, acc=DAYBREAK: symbol(110, 165, u, fg, acc)
    grad = '<defs><linearGradient id="bad" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#20D39B"/><stop offset="1" stop-color="#4D7CFF"/></linearGradient></defs>'
    tiles = [
        tile(0, grad + sym("url(#bad)", "url(#bad)"), "No gradients or glow"),
        tile(1, f'<g transform="translate(150,105) rotate(-25) translate(-150,-105)">{sym()}</g>', "Don’t rotate or re-angle"),
        tile(2, f'<g transform="translate(-60,0) scale(1.6,0.8) translate(0,40)">{sym()}</g>', "Don’t stretch"),
        tile(3, sym(MIDNIGHT, "#4D7CFF"), "Origin cell is always Daybreak"),
    ]
    return svg(1320, 270, "".join(tiles), "#E2DDD3")

m = misuse()
(ASSETS / "misuse.svg").write_text(m, encoding="utf-8")
(ASSETS / "misuse.html").write_text(f'<!doctype html><body style="margin:0">{m}</body>', encoding="utf-8")


# ---------------------------------------------------------------- palette sheet
def palette():
    sw = [("Midnight", "#0B0E14", "Primary background. The hour before Q-day.", PAPER),
          ("Paper", "#F4F1EA", "Primary light background and text on Midnight.", MIDNIGHT),
          ("Daybreak", "#FFA630", "Signature accent: the origin cell, highlights. Never text on Paper.", MIDNIGHT),
          ("Ember", "#A84E08", "Accent for text and links on Paper (4.95:1).", PAPER),
          ("Mist", "#9AA1B0", "Secondary text on Midnight (7.45:1).", MIDNIGHT),
          ("Ash", "#5F6677", "Secondary text on Paper (5.10:1).", PAPER),
          ("Slate", "#6B7385", "Lines, grids and the lattice pattern only.", PAPER)]
    W, cw = 1430, 190; out = []
    for n, (name, hx, note, ink) in enumerate(sw):
        x = 20 + n*(cw + 10); r, g, b = (int(hx[i:i+2], 16) for i in (1, 3, 5))
        out.append(f'<rect x="{x}" y="20" width="{cw}" height="200" rx="10" fill="{hx}" stroke="#D8D3C8"/>')
        out.append(f'<text x="{x+16}" y="56" font-size="22" font-weight="600" fill="{ink}">{name}</text>')
        out.append(f'<text x="{x+16}" y="176" font-size="17" fill="{ink}" font-family="Consolas, monospace">{hx}</text>')
        out.append(f'<text x="{x+16}" y="200" font-size="14" fill="{ink}" font-family="Consolas, monospace" opacity="0.85">RGB {r} {g} {b}</text>')
        words, line, lines = note.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 24: lines.append(line); line = wd
            else: line = (line + " " + wd).strip()
        lines.append(line)
        for k, ln in enumerate(lines):
            out.append(f'<text x="{x}" y="{252 + k*22}" font-size="16" fill="{MIDNIGHT}">{ln}</text>')
    return svg(W, 340, f'<g font-family="Geist, Segoe UI, sans-serif">{"".join(out)}</g>', PAPER)

pal = palette()
(ASSETS / "palette.svg").write_text(pal, encoding="utf-8")
(ASSETS / "palette.html").write_text(f'<!doctype html><body style="margin:0">{pal}</body>', encoding="utf-8")

# ---------------------------------------------------------------- transparent variants for light/dark UIs
for name, fg in (("lockup-on-light", MIDNIGHT), ("lockup-on-dark", PAPER)):
    w, h, body = lockup(60, fg, DAYBREAK, pad=0)
    (ASSETS / f"{name}.svg").write_text(svg(math.ceil(w), math.ceil(h), body), encoding="utf-8")
for name, fg in (("symbol-on-light", MIDNIGHT), ("symbol-on-dark", PAPER)):
    (ASSETS / f"{name}.svg").write_text(svg(round(symbol_width(100)), round(symbol_height(100)), symbol(0, symbol_height(100), 100, fg, DAYBREAK)), encoding="utf-8")
