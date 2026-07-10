"""Shared rough.js-style sketching + font embedding helpers (Excalidraw look).

GitHub loads README SVGs as <img>, which blocks every external resource, so
fonts and images have to be embedded as data URIs. Fonts are subsetted to the
glyphs each drawing actually uses -- a full face would dwarf the drawing.
"""
import base64, io, math, random, os
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(HERE, "fonts")
ASSETS_DIR = os.path.join(HERE, "assets")
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

FONT_FILES = {
    "Excalifont":   "Excalifont-Regular-a88b72a24fb54c9f94e3b5fdaa7481c9.woff2",
    "Comic Shanns": "ComicShanns-Regular-279a7b317d12eb88de06167bd672b4b4.woff2",
    "Lilita One":   "Lilita-Regular-i7dPIFZ9Zz-WBtRtedDbYEF8RXi4EwQ.woff2",
    "Nunito":       "Nunito-XRXI3I6Li01BKofiOc5wtlZ2di8HDIkhdTQ3j6zbXWjgeg.woff2",
}


def font_path(fam):
    p = os.path.join(FONTS_DIR, FONT_FILES[fam])
    if not os.path.exists(p):
        raise SystemExit(f"missing font {FONT_FILES[fam]!r} -- run tools/svg/fetch_fonts.sh first")
    return p

# Excalidraw's own stroke palette
GREY   = "#868e96"
RED    = "#e03131"
BLUE   = "#1971c2"
ORANGE = "#f08c00"
PURPLE = "#9c36b5"


class Rough:
    """Port of rough.js' _line/rectangle so shapes match Excalidraw exports."""

    def __init__(self, seed=7, roughness=1.0, bowing=1.0):
        self.rng = random.Random(seed)
        self.roughness = roughness
        self.bowing = bowing
        self.max_off = 2.0

    def _off(self, x, gain):
        return self.rng.uniform(-x, x) * self.roughness * gain

    def _line(self, x1, y1, x2, y2):
        lensq = (x1 - x2) ** 2 + (y1 - y2) ** 2
        length = math.sqrt(lensq)
        if length < 200:
            gain = 1.0
        elif length > 500:
            gain = 0.4
        else:
            gain = -0.0016668 * length + 1.233334
        offset = self.max_off
        if offset * offset * 100 > lensq:
            offset = length / 10.0
        diverge = 0.2 + self.rng.random() * 0.2
        mdx = self._off(self.bowing * self.max_off * (y2 - y1) / 200.0, gain)
        mdy = self._off(self.bowing * self.max_off * (x1 - x2) / 200.0, gain)
        o = lambda: self._off(offset, gain)
        return (f"M{x1+o():.2f} {y1+o():.2f} "
                f"C{mdx+x1+(x2-x1)*diverge+o():.2f} {mdy+y1+(y2-y1)*diverge+o():.2f}, "
                f"{mdx+x1+2*(x2-x1)*diverge+o():.2f} {mdy+y1+2*(y2-y1)*diverge+o():.2f}, "
                f"{x2+o():.2f} {y2+o():.2f}")

    def line(self, x1, y1, x2, y2):
        return self._line(x1, y1, x2, y2) + " " + self._line(x1, y1, x2, y2)

    def rect(self, x, y, w, h):
        return self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True)

    def poly(self, pts, close=False):
        segs = []
        for a, b in zip(pts, pts[1:]):
            segs.append(self.line(*a, *b))
        if close:
            segs.append(self.line(*pts[-1], *pts[0]))
        return " ".join(segs)

    def _circle_pass(self, cx, cy, r, n=10, jitter=1.6):
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            rr = r + self.rng.uniform(-jitter, jitter)
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        # Catmull-Rom -> cubic bezier, closed
        d = [f"M{pts[0][0]:.2f} {pts[0][1]:.2f}"]
        for i in range(n):
            p0 = pts[(i - 1) % n]; p1 = pts[i]; p2 = pts[(i + 1) % n]; p3 = pts[(i + 2) % n]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
            d.append(f"C{c1[0]:.2f} {c1[1]:.2f}, {c2[0]:.2f} {c2[1]:.2f}, {p2[0]:.2f} {p2[1]:.2f}")
        return " ".join(d)

    def circle(self, cx, cy, r):
        return self._circle_pass(cx, cy, r) + " " + self._circle_pass(cx, cy, r)

    def _bez(self, p0, c1, c2, p3, j):
        o = lambda: self.rng.uniform(-j, j)
        return (f"M{p0[0]+o():.2f} {p0[1]+o():.2f} "
                f"C{c1[0]+o():.2f} {c1[1]+o():.2f}, {c2[0]+o():.2f} {c2[1]+o():.2f}, "
                f"{p3[0]+o():.2f} {p3[1]+o():.2f}")

    def curve(self, p0, c1, c2, p3, j=1.6):
        return self._bez(p0, c1, c2, p3, j) + " " + self._bez(p0, c1, c2, p3, j)

    def arrowhead(self, tip, from_pt, size=13, spread=0.42):
        ang = math.atan2(tip[1] - from_pt[1], tip[0] - from_pt[0])
        out = []
        for s in (+1, -1):
            a = ang + math.pi + s * spread
            out.append(self.line(tip[0] + math.cos(a) * size, tip[1] + math.sin(a) * size, *tip))
        return " ".join(out)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _load(fam):
    return TTFont(font_path(fam))


def measure(fam, text, size):
    """Advance width of `text` at `size` px, using the real font metrics."""
    f = _load(fam)
    cmap = {}
    for t in f["cmap"].tables:
        cmap.update(t.cmap)
    hmtx, upem = f["hmtx"], f["head"].unitsPerEm
    total = 0
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            raise KeyError(f"{fam} has no glyph for {ch!r}")
        total += hmtx[g][0]
    return total / upem * size


def wrap(fam, text, size, max_width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if measure(fam, trial, size) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines


def subset_font(fam, chars):
    opts = subset.Options(flavor="woff2", desubroutinize=True, notdef_outline=True,
                          layout_features=["*"])
    font = subset.load_font(font_path(fam), opts)
    ss = subset.Subsetter(options=opts)
    ss.populate(text="".join(sorted(set(chars) | {" "})))
    ss.subset(font)
    buf = io.BytesIO()
    subset.save_font(font, buf, opts)
    return buf.getvalue()


def font_faces(used):
    """used: {family: set(chars)} -> css @font-face block + total bytes."""
    faces, total = [], 0
    for fam, chars in used.items():
        if not chars:
            continue
        raw = subset_font(fam, chars)
        total += len(raw)
        b64 = base64.b64encode(raw).decode("ascii")
        name = f'"{fam}"' if " " in fam else fam
        faces.append(f"      @font-face {{ font-family: {name}; "
                     f"src: url(data:font/woff2;base64,{b64}); }}")
        print(f"  {fam:13} {len(chars):3} chars -> {len(raw):6} bytes")
    return "\n".join(faces), total


def data_uri(path, mime):
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode("ascii")
