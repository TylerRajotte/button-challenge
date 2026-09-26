# Source button motion and click response

`public/button-motion.json` measures all **1,183 frames at 60 fps**. Coordinates use the same logical **720 × 540** space as cursor tracking. Each sample includes center, average width/height, clockwise rotation in degrees, separate opposing-edge dimensions, ideal corner quadrilateral, and silhouette area. The file also contains four observed compression events, their per-frame normalized width/height curves, and descriptive hover fits.

## Actual compression events

These times come from button geometry, independently of the mouse cursor silhouette. The observed onset is the first clear reduction of button dimensions. The minimum begins visible recovery; it approximates release, but the recording contains no instrumented mouse event timestamps.

| Event | First visible contraction | Minimum width | Minimum height | Essentially recovered | Minimum relative width/height |
|---|---:|---:|---:|---:|---:|
| 1 | 6.8000 s | 6.8500 s | 6.8667 s | 7.0667 s | 0.9616 / 0.9632 |
| 2 | 9.3667 s | 9.4667 s | 9.4667 s | 9.6667 s | 0.9485 / 0.9461 |
| 3 | 10.6167 s | 10.7500 s | 10.7500 s | 10.9667 s | 0.9458 / 0.9450 |
| 4 | 12.9333 s | 13.0167 s | 13.0500 s | 13.2500 s | 0.9456 / 0.9492 |

Dimensions are relative to each event's preceding six-frame hover baseline. Baselines are approximately 326–327 × 108.2 logical pixels. The deepest response reaches approximately 308.3 × 102.3. Initial resting dimensions are approximately 319.2 × 105.5. The first, shorter event contracts less deeply. Events 2–4 visibly contract by approximately 5.4% from hover size. Recovery takes approximately 0.20–0.23 seconds after the minimum, approaching the original hover dimensions smoothly without a pronounced oversized rebound.

Cursor contraction begins roughly 0.08–0.15 seconds before button geometry contraction, so cursor shrinking is unsuitable as a direct trigger timestamp for this response. The additional event at **6.8 seconds** is clearly visible in the button geometry and must be included in source replay.

## The click wave

An expanding **band of brighter mosaic tiles** originates at the click location while the button contracts. The original tile texture remains visible; the source does not become a continuous opaque circular overlay. The band crosses the button while the scale recovers. A large part of the visible effect persists after the geometry is nearly restored.

For event 2, rectified radial brightness profiles measured from the click location show crest radii of approximately **40, 64, 88, 112, 136, and 160 logical pixels** at **9.400, 9.433, 9.467, 9.500, 9.533, and 9.567 seconds**. This is approximately **720 logical pixels/second**. The far side, about 304 logical pixels from the click, brightens around 9.767 seconds. Median red-channel intensity within the crest rises approximately 35–57 levels above the pre-event blue mosaic, with individual tiles varying. The measured radial full width at half maximum is approximately 48 px at 9.5 seconds and 72 px at 9.6 seconds. This brightness measurement excludes the label and cursor and rectifies pose before comparing frames. It is an estimate of visible tile brightening, not a claim about the original shader's parameters.

Evidence: `button-press-sequences.jpg`, `button-motion-curves.png`, and `button-wave-propagation.png`.

## Normal hover pose

Excluding compression events and their immediate neighbors, these fits describe the observed source behavior:

```text
cx = 360.3257 - 0.0290596 * (cursorX - 360)
cy = 269.8921 - 0.0097800 * (cursorY - 270)
rotationDegrees = 0.00577 - 1.40262 * ((cursorX - 360) / 160) * ((cursorY - 270) / 54)
```

Root-mean-square fit errors are approximately 0.141 px, 0.051 px, and 0.059 degrees, respectively. Best tested temporal offset was zero frames. The apparent button center shifts **opposite** the cursor, consistent with its tilted surface viewed in perspective. Z rotation varies with the product of horizontal and vertical cursor displacement. These are descriptive fits to the video, not recovered source code; reproducing the observed response should preserve real interactive pointer dependence.

## Measurement and limits

` scripts/track-button-motion.py` segments the blue silhouette at half native resolution, selects its largest connected component, fits straight lines to the central portions of the top/bottom/left/right edges, and intersects those lines. The quadrilateral describes hypothetical unrounded corners, making it suitable for a perspective transform with rounded corners retained inside the shape. Native frame cadence is preserved. Effective edge coordinate resolution is about half a logical pixel, reduced by averaging over many edge pixels.

The blue color threshold can bias the edge fractionally inward. Antialiasing, the cursor briefly covering an edge, and rounded-edge shape changes introduce small frame-to-frame noise. Width/height minima for the same event can differ by one or two frames. The data strongly identifies the four compression events, their magnitude, and their timing; it does not prove exact pointerdown/up times or original spring constants.

Reproduce geometry with `.venv-cursor/bin/python scripts/track-button-motion.py`; render the sequence and curve evidence with `scripts/button-motion-evidence.py`. Radial-wave analysis is in `scripts/measure-button-wave.py`. Dependencies: OpenCV, NumPy, Pillow. Run `scripts/annotate-button-motion.py` after tracking to append the event annotation and descriptive fits.

## Fitted 3D pose model

A second fit uses a physically projected rectangle instead of the descriptive center/rotation regressions above. `public/button-pose-model.json` records the parameters and errors; reproduce with `.venv-cursor/bin/python scripts/fit-button-pose.py` (also requires SciPy).

The model is the CSS-order transform `perspective(f) rotateX(-normalizedY * angleX) rotateY(normalizedX * angleY) scale(hoverScale)`, applied right to left. Cursor normalization is `(x−360)/160` and `(y−270)/54`. No explicit Z rotation is required: the observed apparent Z rotation and center shift emerge from the two tilts and perspective projection.

Fitting 387 hover frames produced:

| Parameter | Best fit |
|---|---:|
| X tilt amplitude | 9.0086° |
| Y tilt amplitude | 8.9589° |
| Perspective distance | 897.98 px |
| Hover scale | 1.029892 |
| Projected center | 360.3281, 269.8943 |
| Base measured silhouette | 319.215 × 105.478 px |
| Per-coordinate RMSE | 0.278 px |
| Corner-distance RMSE | 0.393 px |
| Maximum corner error | 1.590 px |

The clean parameter values **9° tilt, 900 px perspective, and 1.03 hover scale** are strongly supported. The measured blue-silhouette dimensions can be fractionally smaller than the underlying CSS rectangle because the threshold excludes antialiased boundary pixels. These results support implementing real pointer-driven 3D transforms rather than animating an unrelated Z rotation or importing frame geometry as a substitute for interactive behavior.
