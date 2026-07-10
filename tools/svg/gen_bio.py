#!/usr/bin/env python3
"""Generate bio.svg -- an Excalidraw-style `class Bio` card with annotated arrows."""
import os
from roughlib import (Rough, esc, font_faces, REPO_ROOT,
                      GREY, RED, BLUE, ORANGE, PURPLE)

OUT = os.path.join(REPO_ROOT, "bio.svg")

EX  = "Excalifont, Segoe UI Emoji, sans-serif"
CS  = "Comic Shanns, ui-monospace, monospace"
LIL = "Lilita One, sans-serif"

used = {"Excalifont": set(), "Comic Shanns": set(), "Lilita One": set()}


def text_el(x, y, family, size, fill, content, key):
    used[key].update(content)
    return (f'  <text x="{x}" y="{y}" font-family="{family}" font-size="{size}px" '
            f'fill="{fill}" text-anchor="start" xml:space="preserve" '
            f'style="white-space:pre">{esc(content)}</text>\n')


def code_line(x, y, size, runs):
    """runs: [(text, colour)] rendered as flowing tspans in the monospace face."""
    parts = []
    for t, c in runs:
        used["Comic Shanns"].update(t)
        parts.append(f'<tspan fill="{c}">{esc(t)}</tspan>')
    return (f'  <text x="{x}" y="{y}" font-family="{CS}" font-size="{size}px" '
            f'xml:space="preserve" style="white-space:pre">{"".join(parts)}</text>\n')


def arrow(r, p0, c1, c2, p3, color, sw=3.2):
    return (f'  <g stroke="{color}" stroke-width="{sw}" fill="none" stroke-linecap="round">\n'
            f'    <path d="{r.curve(p0, c1, c2, p3)}"/>\n'
            f'    <path d="{r.arrowhead(p3, c2)}"/>\n  </g>\n')


W, H = 785, 478
r = Rough(seed=20260710, roughness=1.15, bowing=1.4)

body = []
body.append(text_el(52, 58, CS, 30, RED, "class Bio:", "Comic Shanns"))

# --- card ---------------------------------------------------------------------
CX, CY, CW, CH = 50, 80, 462, 272
# rough.js damps its wobble on long edges, so sketch the card with a rougher pen
# than the arrows or it reads as a plain rectangle
card = Rough(seed=99, roughness=1.8, bowing=1.0)
body.append(f'  <path d="{card.rect(CX, CY, CW, CH)}" stroke="{GREY}" '
            f'stroke-width="2.4" fill="none" stroke-linecap="round"/>\n')

x0, fs = 76, 18
body.append(code_line(x0, 122, fs, [("self.username  ", GREY), ("= ", GREY), ('"LuminousVar"', BLUE)]))
body.append(code_line(x0, 156, fs, [("self.role      ", GREY), ("= ", GREY), ('"404 Threat Not Found"', RED)]))
body.append(code_line(x0, 190, fs, [("self.languages ", GREY), ("= ", GREY), ('["id", "en"]', ORANGE)]))
body.append(code_line(x0, 246, fs, [("def ", PURPLE), ("say_hi", BLUE), ("(self):", GREY)]))
body.append(code_line(x0 + 30, 280, fs, [("print", BLUE), ("(", GREY), ('"Hi! Thanks for visiting"', ORANGE), (")", GREY)]))
body.append(code_line(x0 + 30, 314, fs, [("print", BLUE), ("(", GREY), ('"Yoroshiku onegai shimasu"', ORANGE), (")", GREY)]))

# --- the call, below the card --------------------------------------------------
body.append(code_line(76, 410, 17, [("me ", GREY), ("= ", GREY), ("Bio", BLUE), ("()", GREY)]))
body.append(code_line(76, 438, 17, [("me", GREY), (".say_hi", BLUE), ("()", GREY)]))

# --- handwritten annotations ---------------------------------------------------
body.append(text_el(600, 112, EX, 19, GREY, "yep, that's me!", "Excalifont"))
body.append(arrow(r, (596, 120), (570, 136), (558, 112), (516, 122), GREY))

body.append(text_el(600, 168, EX, 19, GREY, "totally harmless", "Excalifont"))
body.append(text_el(600, 192, EX, 19, GREY, "(probably)", "Excalifont"))
body.append(arrow(r, (594, 162), (564, 156), (552, 160), (516, 152), GREY))

body.append(text_el(600, 248, EX, 19, GREY, "id & en,", "Excalifont"))
body.append(text_el(600, 272, EX, 19, GREY, "take your pick", "Excalifont"))
body.append(arrow(r, (596, 240), (564, 228), (550, 204), (516, 192), GREY))

body.append(text_el(598, 330, EX, 19, GREY, "the fun part", "Excalifont"))
body.append(arrow(r, (594, 322), (562, 310), (550, 292), (516, 278), GREY))

body.append(text_el(268, 424, LIL, 24, RED, "RUN IT!", "Lilita One"))
body.append(arrow(r, (262, 418), (232, 406), (222, 430), (192, 434), RED, sw=3.0))

body.append(text_el(52, 382, EX, 18, GREY, "and yes, it actually runs:", "Excalifont"))

faces, total = font_faces(used)

svg = (
    '<?xml version="1.0" standalone="no"?>\n'
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'width="{W}" height="{H}">\n'
    '  <!-- Excalidraw-style bio card for LuminousVar -->\n'
    f'  <defs>\n    <style class="style-fonts">\n{faces}\n    </style>\n  </defs>\n'
    + "".join(body) +
    '</svg>\n'
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"\nfonts {total} B | wrote {OUT} ({len(svg)} B)")
