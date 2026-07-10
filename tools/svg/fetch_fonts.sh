#!/usr/bin/env bash
# Fetch the Excalidraw fonts the SVG generators embed.
#
# Not vendored into the repo: they are third-party fonts, and the generators
# only ever embed the handful of glyphs each drawing uses. Pinned to a commit
# rather than master so upstream regenerating its font subsets cannot silently
# swap the files underneath us.
set -euo pipefail

PIN="3b9e1c07f5d32ee11c327dc006f2050ffc6eea19"
BASE="https://raw.githubusercontent.com/excalidraw/excalidraw/${PIN}/packages/excalidraw/fonts"
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fonts"

# local name : upstream path : sha256
ASSETS=(
  "Excalifont-Regular-a88b72a24fb54c9f94e3b5fdaa7481c9.woff2:Excalifont/Excalifont-Regular-a88b72a24fb54c9f94e3b5fdaa7481c9.woff2:e4423b318e11432aff2e6e865e300b7ca270f92321a3f56632268fede01c1b48"
  "ComicShanns-Regular-279a7b317d12eb88de06167bd672b4b4.woff2:ComicShanns/ComicShanns-Regular-279a7b317d12eb88de06167bd672b4b4.woff2:fa930fceb529a4b51ba3055d590302722c27704f6a6357495873950136b1e2ea"
  "Lilita-Regular-i7dPIFZ9Zz-WBtRtedDbYEF8RXi4EwQ.woff2:Lilita/Lilita-Regular-i7dPIFZ9Zz-WBtRtedDbYEF8RXi4EwQ.woff2:8d6cd0f298738a92ca9bf6e13f54a9191afd06ce04ea00ebbf24499c017191b7"
  "Nunito-XRXI3I6Li01BKofiOc5wtlZ2di8HDIkhdTQ3j6zbXWjgeg.woff2:Nunito/Nunito-Regular-XRXI3I6Li01BKofiOc5wtlZ2di8HDIkhdTQ3j6zbXWjgeg.woff2:6d1626aac658786e37e78e0adce3ffffddbd75abc923d72e45a7168bd80053da"
)

mkdir -p "${DEST}"

for entry in "${ASSETS[@]}"; do
  IFS=":" read -r name path want <<<"${entry}"
  out="${DEST}/${name}"

  if [[ -f "${out}" ]] && [[ "$(sha256sum "${out}" | cut -d" " -f1)" == "${want}" ]]; then
    echo "ok (cached)  ${name}"
    continue
  fi

  curl -sfL "${BASE}/${path}" -o "${out}"
  got="$(sha256sum "${out}" | cut -d" " -f1)"
  if [[ "${got}" != "${want}" ]]; then
    rm -f "${out}"
    echo "checksum mismatch for ${name}" >&2
    echo "  expected ${want}" >&2
    echo "  got      ${got}" >&2
    exit 1
  fi
  echo "ok           ${name}"
done

echo
echo "fonts ready in ${DEST}"
