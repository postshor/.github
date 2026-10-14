# Regenerating brand assets

All logo geometry, colours and layouts are defined in `build.py`. Edit the constants at the top (colours, `ANGLE`, `K`) rather than editing SVG files by hand.

```
python -m pip install fonttools uharfbuzz
mkdir -p work/fonts
curl -L -o "work/fonts/Geist[wght].ttf"     "https://github.com/google/fonts/raw/main/ofl/geist/Geist%5Bwght%5D.ttf"
curl -L -o "work/fonts/GeistMono[wght].ttf" "https://github.com/google/fonts/raw/main/ofl/geistmono/GeistMono%5Bwght%5D.ttf"
python build.py work
```

SVG files are written to `work/assets/`. Render PNGs from them with any browser or `rsvg-convert`, at 2× for retina screens.

The wordmark is converted to outlines, so the generated files do not depend on the font being installed.
