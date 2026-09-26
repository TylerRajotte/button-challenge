# Cursor tracking verification

Final data: `public/cursor-track.json` contains all **1,183 source frames at 60 fps**, spanning 0–19.700 seconds; the clip duration is 19.716667 seconds. Coordinates are the visible upper-left arrow tip in a **720 × 540** coordinate system. Source pixels are scaled independently by 720/2876 horizontally and 540/2160 vertically. No hand-authored substitute path or temporal smoothing was applied to the measured positions.

## Method and reproducibility

` scripts/track-cursor.py` decodes the reference with OpenCV, analyzes it at 1438 × 1080, and extracts an arrow template from the sharp cursor in frame zero. A filled outline mask excludes the template's white exterior background. Masked normalized squared-difference matching searches eight scales (0.72–1.12) within the previous frame's neighborhood. This avoids switching to the label or mosaic tiles when motion blur or cursor contraction changes the silhouette. The half-resolution tip is then mapped to the app coordinate system.

Run from the repository root:

```sh
.venv-cursor/bin/python scripts/track-cursor.py
.venv-cursor/bin/python scripts/cursor-tracking-evidence.py
```

Dependencies are `opencv-python-headless`, `numpy`, and `Pillow`; the local `.venv-cursor` environment contains them.

## Verification

- Every source frame was tracked; there are no missing samples or interpolated gaps.
- Median template similarity is **0.9418**, minimum **0.8534**. Confidence is `1 − normalized squared difference`, a matching score rather than a calibrated probability.
- Largest adjacent-frame tip displacement is **7.51 logical pixels**. There are no discontinuous position jumps.
- `cursor-tracking-contact-sheet.jpg` shows 105 checks: quarter-second samples plus the 30 lowest-confidence frames, with red circles at the measured tip. Reviewed the full sheet, including left/right turns, stationary intervals, label-adjacent passes, and the fast sweeps around 4 and 16.5 seconds. Markers follow the arrow tips throughout.
- `cursor-scale-detail.png` shows enlarged source cursor crops. It distinguishes real stationary contraction from motion blur. The baseline arrow spans approximately 56 source pixels, or 14 logical pixels.

## Rendering scale and limits

`detectionScale` preserves the raw best-fitting template scale. **Do not render directly from detectionScale**: at 4 seconds a blurred normal-size arrow matches a 0.72 sharp template, even though its visible extent has not shrunk. The same effect occurs during other fast sweeps.

`cursorScale` is corrected for replay: moving samples use 1.0; stationary samples retain the fitted scale, clamped to the visually supported minimum 0.84. Values 0.96 and above normalize to 1.0. Stationary is estimated from tip displacement across a seven-frame window, below 0.4 logical pixels/frame. Actual sharp contraction to about 0.84 is visible near 9.3, 10.6–10.7, and 12.95–13 seconds. Thus the corrected scale is **1.0 at 4 seconds**, **0.84 at 10.683 seconds**, and **0.84 at 13 seconds**. This is a visual scale estimate, not a verified mouse-button event; no `pressed` field is claimed.

Quantization is roughly half a logical pixel before template-scale offsets. A fast, blurred arrow has no single unambiguous instantaneous tip; the match follows its strongest visible contour, so a few logical pixels of bias are possible during the fastest sweeps. Scale transitions are approximate. Coordinates and source timing are much more reliable than any inferred input state.
