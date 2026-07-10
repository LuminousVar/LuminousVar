#!/usr/bin/env python3
"""Excalidraw-style sticky-note quote card for the LuminousVar profile README."""
import os
from roughlib import (Rough, esc, measure, font_faces, data_uri,
                      ASSETS_DIR, REPO_ROOT, GREY, BLUE, ORANGE)

OUT = os.path.join(REPO_ROOT, "quote.svg")

EX  = "Excalifont, Segoe UI Emoji, sans-serif"
NUN = "Nunito, sans-serif"

QUOTE = "I'm not the most skilled one out there, but I level up every single day."
NAME  = "LuminousVar"
DATE  = "16 Agu 2025"

W, H = 600, 272
# note box (pre-rotation)
NX, NY, NW, NH = 32, 24, 532, 208
NR, NB = NX + NW, NY + NH          # right / bottom
FOLD = 42                          # dog-ear size

QSIZE, LEAD = 23, 36
TEXT_X = 74
MAXW = NR - TEXT_X - 34

# break on the comma rather than greedy-wrapping: "…one out / there, but…" reads badly
head, tail = QUOTE.split(", ", 1)
lines = ["“" + head + ",", tail + "”"]
for ln in lines:
    print(f"  line {measure('Excalifont', ln, QSIZE):6.1f}px / {MAXW}px  {ln!r}")
assert all(measure("Excalifont", l, QSIZE) <= MAXW for l in lines), "quote line overflows note"

used = {"Excalifont": set("".join(lines)) | set(DATE), "Nunito": set(NAME)}

r = Rough(seed=4242, roughness=1.8, bowing=1.0)
arc = Rough(seed=77, roughness=1.2, bowing=1.0)

body = []

# --- sticky note outline with a dog-eared bottom-right corner -----------------
outline = r.poly([(NX, NY), (NR, NY), (NR, NB - FOLD),
                  (NR - FOLD, NB), (NX, NB)], close=True)
body.append(f'    <path d="{outline}" stroke="{GREY}" stroke-width="2.4" '
            f'fill="none" stroke-linecap="round"/>\n')
# the folded flap: two legs meeting at the inner corner
flap = r.poly([(NR - FOLD, NB), (NR - FOLD, NB - FOLD), (NR, NB - FOLD)])
body.append(f'    <path d="{flap}" stroke="{GREY}" stroke-width="2.2" '
            f'fill="none" stroke-linecap="round" opacity="0.75"/>\n')

# --- quote lines --------------------------------------------------------------
y = 76
for i, ln in enumerate(lines):
    body.append(f'    <text x="{TEXT_X}" y="{y}" font-family="{EX}" font-size="{QSIZE}px" '
                f'fill="{GREY}" xml:space="preserve" style="white-space:pre">{esc(ln)}</text>\n')
    y += LEAD

# hand-drawn emphasis underline: span exactly "level up every single day"
LAST = lines[-1]
EMPH = "level up every single day"
assert EMPH in LAST, LAST
u0 = TEXT_X + measure("Excalifont", LAST[:LAST.index(EMPH)], QSIZE)
u1 = u0 + measure("Excalifont", EMPH, QSIZE)
und_y = y - LEAD + 15   # clear the p/y/g descenders
span = u1 - u0
body.append(f'    <path d="{arc.curve((u0, und_y), (u0 + span*0.33, und_y + 6), (u0 + span*0.68, und_y - 5), (u1, und_y + 2), j=1.4)}" '
            f'stroke="{ORANGE}" stroke-width="3" fill="none" stroke-linecap="round"/>\n')
print(f"  underline {u0:.0f}..{u1:.0f} under {EMPH!r}")

# --- signature: avatar + name + date -----------------------------------------
# avatar left edge aligns with the text column
AVR = 30
AVX, AVY = TEXT_X + AVR, 178
avatar = data_uri(os.path.join(ASSETS_DIR, "avatar.jpg"), "image/jpeg")
body.append(f'    <clipPath id="avaClip"><circle cx="{AVX}" cy="{AVY}" r="{AVR}"/></clipPath>\n')
body.append(f'    <image href="{avatar}" x="{AVX-AVR}" y="{AVY-AVR}" '
            f'width="{AVR*2}" height="{AVR*2}" clip-path="url(#avaClip)" '
            f'preserveAspectRatio="xMidYMid slice"/>\n')
body.append(f'    <path d="{arc.circle(AVX, AVY, AVR + 2)}" stroke="{GREY}" '
            f'stroke-width="2.4" fill="none"/>\n')

SIG_X = AVX + AVR + 18
body.append(f'    <text x="{SIG_X}" y="175" font-family="{NUN}" font-size="22px" '
            f'fill="{BLUE}" font-weight="700">{esc(NAME)}</text>\n')
body.append(f'    <text x="{SIG_X}" y="199" font-family="{EX}" font-size="15px" '
            f'fill="{GREY}">{esc(DATE)}</text>\n')

faces, total = font_faces(used)

svg = (
    '<?xml version="1.0" standalone="no"?>\n'
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
    f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
    '  <!-- Excalidraw-style sticky-note quote for LuminousVar -->\n'
    f'  <defs>\n    <style class="style-fonts">\n{faces}\n    </style>\n  </defs>\n'
    f'  <g transform="rotate(-1.6 {W/2:.0f} {H/2:.0f})">\n'
    + "".join(body) +
    '  </g>\n</svg>\n'
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"\nfonts {total} B | wrote {OUT} ({len(svg)} B)")
