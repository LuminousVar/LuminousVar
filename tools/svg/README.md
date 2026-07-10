# SVG generators

Regenerates the hand-drawn SVGs in the repo root: `bio.svg` and `quote.svg`.
Both are drawn in Excalidraw's style to match `banner.svg`.

## Usage

```bash
pip install fonttools brotli
./tools/svg/fetch_fonts.sh          # once; fonts are gitignored

cd tools/svg
python3 gen_bio.py                  # -> bio.svg
python3 gen_quote.py                # -> quote.svg
```

Output is deterministic: the sketching RNG is seeded and font subsetting is
stable, so re-running on an unchanged script reproduces the committed SVG
byte-for-byte. A diff in `git status` therefore means you actually changed
something.

## Why the SVGs are built this way

GitHub renders a README SVG as an `<img>`, which blocks every external
resource — no remote fonts, no remote images, no scripts. Anything the drawing
needs has to be embedded as a data URI. So:

- **Fonts** (`roughlib.font_faces`) are subsetted to just the glyphs a drawing
  uses, then embedded as base64 woff2. A full face would be far larger than the
  drawing itself.
- **The avatar** (`assets/avatar.jpg`) is embedded rather than linked.

Subsetting has a sharp edge: **a font only carries the glyphs it was subsetted
with.** If you add text using a character the subset lacks, the browser falls
back to a system font for that character alone, and the word renders half in one
typeface and half in another. The generators avoid this by collecting every
character they draw and subsetting to exactly that set, so just edit the text and
re-run — never hand-edit the `<text>` elements in the generated SVG.

## Files

| | |
|---|---|
| `roughlib.py` | rough.js port (double strokes + bowing), font subsetting/embedding, text measurement |
| `gen_bio.py` | the `class Bio` card with annotated arrows |
| `gen_quote.py` | the dog-eared sticky-note quote |
| `fetch_fonts.sh` | downloads the Excalidraw fonts, pinned by commit and verified by sha256 |
| `assets/avatar.jpg` | 140px avatar, embedded into `quote.svg` |

Fonts come from [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw)
(Excalifont, Comic Shanns, Lilita One, Nunito) and are not vendored here.
