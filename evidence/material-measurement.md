# Native source material measurement

Measured `reference/source.mp4` directly at 2876×2160. Numeric material data are in `public/material-calibration.json`; no source image is embedded as a texture. Native-frame center trajectories and registration matrices are in `reference/analysis/material-dynamics.json`.

## Lattice

The first frame contains 40 visible columns ×13 rows, with the outside columns/rows clipped by the rounded surface. The best straight-line fit to seam minima is:

| Measurement | Native source pixels | At 720×540 |
|---|---:|---:|
| First vertical seam phase x | 799.421536 | 200.133347 |
| First horizontal seam phase y | 866.787879 | 216.696970 |
| Horizontal pitch | 32.227671 | 8.068123 |
| Vertical pitch | 32.199301 | 8.049825 |

Cell (row, column) center is origin + (column+.5, row+.5) × pitch. The slight x/y difference includes initial pose/projection. This is a projected first-frame lattice, not an assertion that local object-space cells are rectangular. The same cells persist on hover; there is no grid subdivision.

Seam full width at half depth is approximately 4.3–4.7 native pixels (1.08–1.18 at720). The visible seam rolls off over roughly ±5 native pixels. The nominal seam minimum is slightly left of the average fitted vertical phase on hover, consistent with pixel sampling and projection. There is no measurable bright white edge overshoot in the averaged crosssections; the main tile boundary is a recessed blue line. Avoid bright specular lines around every tile.

## Absolute idle palette and masking

`idleCenterRGB` is a 13×40 array of decoded sRGB triplets in 0–255 units. It is the median over a 17×17 native-pixel patch near each cell center. `idleCenterObserved` identifies 424 directly measured cells; 96 label/corner cells are imputed from a quadratic spatial illumination fit. `idleCenterRGBMeasured` retains pre-imputation samples for audit, with -1 for completely unobserved values. Because center labels obscure the source, those hidden cell albedos cannot be recovered exactly.

The average observed center is RGB(62.57,99.34,217.62). Spatial illumination is substantial: top-row average RGB(78.41,116.35,225.68), middle row6 RGB(61.38,99.81,221.19), bottom row12 RGB(44.89,76.36,190.81). Random residual standard deviation after quadratic spatial illumination removal is (4.87,3.89,3.78) RGB units. A flat or uniformly blue material therefore loses both the vertical falloff and the stable per-cell variations.

The identical cells at0 and1s have red-channel random-residual correlation0.990. At19.5s after leaving the button correlation with first-frame random residual is0.972, with median RGB delta approximately(0,0,-1). The random pattern does not regenerate during hover.

`idleSeamFloorRGB` independently measures the blue seam material per cell by taking four surrounding edge floors; `idleSeamFloorObserved` identifies346 directly observed cells. Label, corner and outer-edge values are imputed. This palette has mean RGB(54.41,91.65,212.47). Use an independent seam response, because multiplying the highlighted tile RGB by a darkness coefficient causes seams to brighten far too much.

## Seam RGB and hover contrast

The following values average a large interior sample, excluding the label and rounded corners. Centers here mean seam centers; interior is8 native pixels away.

| State | Direction | Seam RGB | Adjacent interior RGB |
|---|---|---|---|
| Idle0s | Vertical | (55.8,92.9,213.6) | (63.7,100.9,220.4) |
| Idle0s | Horizontal | (55.7,93.4,214.1) | (64.9,102.4,221.8) |
| Hover2s | Vertical | (61.5,95.6,211.6) | (89.6,120.3,223.9) |
| Hover2s | Horizontal | (61.1,94.6,210.0) | (91.6,122.3,225.5) |

Local near-cursor example at row2/vertical seam33:

- Idle: left(75,113,227), seam(65,103,217), right(75,113,227).
- Hover2s: left(138.7,162.1,238.7), seam(84.6,115.7,213), right(148.3,168.7,237.3).

Seams remain blue while tiles grow pale. The blue channel of the seam can decrease while tile red/green increase. There is some cursor-local seam response, so a globally fixed seam RGB is also an approximation. The source seam profile arrays include every RGB sample at native offsets-12…12; local profiles include offsets-16…16. Optical registration has median feature reprojection error around0.6 native pixels during hover, so single-pixel seam details are less certain than tile-center colors.

## Quantitative ordinary hover model

`hoverResponseFit` provides two additional13×40 RGB arrays, `baseDeltaRGB` and `radialDeltaRGB`. For a stable hovered frame:

```
g = exp(-distanceNativePx² / (2 * 210²))
sRGB255 = idleCenterRGB + hoverAmount * (baseDeltaRGB + radialDeltaRGB * g)
```

At720×540 the Gaussian sigma is52.5pixels. Distance is between the cell center and current cursor tip after transforming both into the initial lattice plane. The optimum lag over-0.1…+0.2s at1/60s increments is0s. The ordinary material glow tracks the cursor immediately; smoothing may still apply to button pose separately.

Averaged over measured cells, `baseDeltaRGB` is(9.770,6.758,0.467) and `radialDeltaRGB` is(57.984,46.154,12.227). The radial amplitude varies strongly by fixed cell: red10th/50th/90th percentiles33.36/59.34/80.61. This explains why brighter idle tiles become disproportionately bright near the pointer. Preserve the per-cell response instead of adding the same highlight to all tiles.

Fit RMS error is **(2.335,1.861,0.980) RGB units**, measured across observed center samples from1.8–18.4s while excluding click wave windows6.8–7.45s,9.366667–10.016667s,10.616667–11.266667s,12.933333–13.583333s. This is an empirical source-color model; it does not prove the source used that shader. The fit is in decoded **sRGB**, not linear RGB. If used in a physically lit renderer, convert appropriately or account for the render's lighting/tone mapping rather than applying these numbers as already-linear light.

Direct examples of stable per-cell behavior:

| Cell(row,col) | Idle | Hover2s, pointer right | Hover3s, pointer left | Idle19.5s |
|---|---|---|---|---|
| (2,6) | (66,106,224) | (69,109,225) | (97,129,229) | (66,106,224) |
| (2,33) | (75,113,227) | (149,169,237) | (87,123,229) | (76,112,225) |
| (8,34) | (47,87,217) | (76,107,222) | (53,91,218) | (47,87,215) |
| (9,6) | (56,94,220) | (72,103,220) | (109,133,227) | (57,93,218) |

Click waves must be a separate contribution: including those windows increases the same fit error to(7.45,5.97,1.86), and distorts the global hover brightness upward. Fitting global brightness per frame identifies large departures around7.167,9.667,11.0,13.167s, consistent with an expanding click wave reaching many cells simultaneously. The ordinary cursor model itself has no evidence of a persistent long trail.

## Reproduction

Run in this order (the first script rebuilds the JSON):

```
.venv-cursor/bin/python scripts/analyze-material.py
.venv-cursor/bin/python scripts/fit-material-response.py
.venv-cursor/bin/python scripts/measure-seam-palette.py
```

Analysis scripts only read the source video/cursor coordinates and write numeric measurements. They do not read implementation renders or change `src/main.js` or `src/style.css`.

## Click material residual

`scripts/measure-click-material.py` subtracts the ordinary hover prediction, then bins excess RGB by distance from the independently measured click wave radius `16 + 720*ageSeconds` at720×540. Results are in `reference/analysis/click-material-profile.json`.

| Offset from wave front,720px | Mean excess RGB |
|---|---|
| -100…-90 | (10.37,7.92,1.91) |
| -60…-50 | (29.06,23.09,6.01) |
| -40…-30 | (30.77,24.71,6.62) |
| -20…-10 | (37.96,30.41,7.68) |
| -10…0 | (46.01,37.09,9.93) |
| 0…10 | (39.02,31.43,8.48) |
| 10…20 | (22.24,17.58,4.74) |
| 20…30 | (7.67,5.89,1.52) |
| 30…40 | (2.07,1.40,0.31) |
| 50…60 | (0.32,0.17,0.07) |

This is a sharply advancing front with a long bright inner tail, not a narrow symmetric ring. An approximate leading Gaussian width15pixels with inner decay length roughly65pixels is a useful starting model; the table is measured, while those widths are an interpretation rather than a fitted result. The aggregate mixes several ages/clicks, so per-tile ring amplitude and decay should not be inferred as exactly constant.

## Precision seam response calibration

`hoverSeamResponseFit` now contains independent13×40 seam floor arrays `idleFloorRGB`, `baseDeltaRGB`, and `radialDeltaRGB`, plus separate vertical/horizontal directional fits. These use the same52.5px cursor Gaussian as the faces. The idle floor in this section is the mean of four edge minima, which is deliberately different from the older median-four-edge `idleSeamFloorRGB` field. Use all three arrays from this new section together.

```
seamRGB = idleFloorRGB + hoverAmount * (
  baseDeltaRGB + radialDeltaRGB * exp(-distance720Px²/(2*52.5²))
)
```

The mean seam base delta is **(+0.985,+0.111,-0.701)** and mean radial delta is **(+8.393,+2.329,-10.147)**. In particular, cursor proximity darkens the seam's blue channel while it greatly brightens face red/green. Seam RGB cannot be obtained by multiplying face illumination by a fixed positive factor.

The fit sampled87 native frames, retaining ordinary hover and idle checks and excluding click windows. Per-cell seam floor MAE is **(0.797,0.553,0.900)** RGB, RMSE **(1.156,0.877,1.187)**. The former proposed approximation `seamIdle + .35*faceBaseDelta + .27*faceRadialDelta*g` has MAE **(4.056,4.551,4.148)** and almost entirely positive brightness bias. Independent measured seam response materially improves this.

Directional mean deltas:

| Direction | Base delta RGB | Radial delta RGB | Fit MAE RGB |
|---|---|---|---|
| Vertical | (+0.235,-0.390,-0.774) | (+8.209,+2.685,-9.754) | (1.084,.791,1.221) |
| Horizontal | (+1.735,+0.611,-0.628) | (+8.577,+1.973,-10.541) | (.953,.682,1.180) |

Target mean floor RGB across each state's valid measurement cells is idle0s(54.27,91.49,212.34), hover2s(57.84,91.99,208.82), hover3s(57.49,91.30,208.23), hover6s(57.32,91.21,208.13), and hover12s(58.73,92.85,208.79). The valid subset varies to exclude the moving cursor, so those means should not replace per-cell validation.

A local floor example, cell(row2,col33), averages four neighboring seam minima: idle(62.97,100.97,216.97), near-pointer2s(72.47,102.83,203.75), far-pointer3s(65.39,101.28,217.25). Cell(row9,col6) is idle(43.03,81.78,210.61), pointer-far2s(44.81,82.47,208.28), pointer-near3s(52.58,84.17,202.11).

### Width and bevel precision

`widthMeasurements` includes red-channel depth profiles after subtracting the local linear interior-color ramp. At0s, vertical FWHM is4.208 native pixels (1.052 at720), horizontal4.004 (1.001 at720). Across hover states, vertical FWHM is4.35–4.56 native pixels and horizontal4.30–4.48 (about1.08–1.14 at720). Some broadening comes from the source scale increase and bilinear registration; this does not establish an intentionally animated seam width.

The0s vertical half-depth crossings are-2.491 and+1.717 native pixels relative to the fitted lattice phase, with depth centroid-0.532. Horizontal crossings are-2.149 and+1.855, centroid-0.055. The vertical dark line therefore has a small leading-side bias of about0.13px at720. Hover centroids vary with pose and sampling, generally negative0.3–1.1 native pixels. The averaged profiles do **not** show a white bevel highlight; their small apparent bright overshoots are at most about2% of seam depth and can be explained by compression/illumination-ramp error. A smooth recessed blue seam, around1.05px FWHM, with a tiny left/up bias, is supported better than visibly lit bright tile outlines.

Additional reproduction:

```
.venv-cursor/bin/python scripts/fit-seam-response.py
.venv-cursor/bin/python scripts/summarize-seam-profile.py
```

Raw registered seam trajectories are saved in `reference/analysis/seam-dynamics.json`; width data are also saved separately in `reference/analysis/seam-width-measurements.json`.

## Dense click pulse fit (supersedes constant-width ring approximation)

148 fresh **native-resolution** source frames were extracted around the four events: every frame for the first0.32s, then every second frame through0.767s, plus three pre-event frames. Every frame receives its own grid homography. The click origin is captured once in the local button plane at the event frame and held fixed as the surface compresses and recovers. Re-projecting a fixed screen origin through each later pose biases the fitted propagation speed; it is not the correct convention.

`clickResponseFit` in the calibration JSON now contains final per-cell `pulseGainRGB` and the following source-only fitted model (distances at720×540):

```
a = max(ageSeconds, 0)
radius = 15.8754 + 723.775*a
sigmaAhead = 6.99083 + 28.8851*a
widthBehind = 2.77234 + 238.248*a
offset = distanceFromFixedLocalClickPoint - radius
band = offset >= 0
  ? exp(-offset*offset / (2*sigmaAhead*sigmaAhead))
  : exp(-pow(-offset/widthBehind, 2.74924))
onset = 1 - exp(-a/0.0340064)
clickExcessRGB = pulseGainRGB * band * onset
```

No additional exponential age decay was selected by this fit. The wave fades at each fixed tile because its distance behind the advancing front increases. The radius agrees with the independently observed16+720*age law. The major corrections are **a34ms onset, a narrow initial wave that widens as it expands, and a steep-power inner profile instead of a constant65px exponential tail**.

Average measured pulse gain is RGB(53.50,42.74,11.57), approximately0.92×the ordinary cursor radial gain. The per-cell pulse gain correlates with cursor radial gain at0.968/0.971/0.976 in RGB, but the supplied per-cell array preserves the measured differences. Masked label/corner values are imputed by regression against ordinary hover gains. The peak gain is multiplied by the onset:0atage0,0.387at16.7ms,0.770at50ms,0.947at100ms,0.988at150ms. A fixed immediate0.8×gain therefore overstates the first frames and understates the mature front.

The fit removes ordinary hover and a small event-specific pre-click prediction bias for parameter identification. **Operational error without adding that event-specific bias back** is MAE **(2.697,2.177,0.930)** RGB, RMSE **(4.766,3.890,1.397)**. The previous formula `.8*hoverRadialGain*band*exp(-age*.55)` with constant ahead15/behind65 widths has MAE **(6.290,5.051,1.596)**, RMSE **(10.475,8.438,2.492)** on the same source samples. Identification error after pre-click bias removal is MAE(2.389,1.895,.970). These are tile-center material errors; body pose, seams, text and background are excluded.

Measured widths from the final compact fit:

| Age seconds | Ahead sigma720px | Behind width720px | Onset |
|---|---:|---:|---:|
| .0167 | 7.47 | 6.75 | .388 |
| .05 | 8.44 | 14.68 | .770 |
| .10 | 9.88 | 26.60 | .947 |
| .20 | 12.77 | 50.42 | .997 |
| .30 | 15.66 | 74.25 | 1.000 |

The old qualitative “leading sigma15 plus inner exponential65” estimate mixed pulse ages and is superseded by these dense measurements. Separately fitted per-age amplitude/shape numbers in `click-independent-age-shape.json` are diagnostics under a fixed1.3back-power assumption, **not** additional coefficients to combine with the final2.749power model.

Artifacts and reproduction:

```
.venv-cursor/bin/python scripts/extract-dense-click-material.py
.venv-cursor/bin/python scripts/fit-click-material-local-origin.py
```

The dense trajectories are `reference/analysis/dense-click-material.json`; the final standalone response is `reference/analysis/click-response-fit.json`. Alternate fitting scripts retain experimental parameterizations for audit. The final supported model is the fixed-local-origin fit above. This analysis only compares measured source material trajectories; it does not use implementation captures in the fit or claim a pixel-perfect recreation.

## Individual light onset and early crest refinement

The dense source data were reweighted toward **positive source light crests**, instead of letting many low-intensity tail pixels dominate the fit. Only the light timeline changes; preserve geometry/compression event timing. `clickPeakRefinement` provides a measured optional correction to the base click model:

| Event frame/time | Light age advance |
|---|---:|
| 408 /6.800000s | +0.004758s |
| 562 /9.366667s | +0.004481s |
| 637 /10.616667s | **−0.010361s** |
| 776 /12.933333s | +0.008599s |

Compute `lightAge=max(0, geometryAge+advance)` and use it for radius, widths, and light onset. The fourth event advances the front about6.2pixels at720 resolution; the third light pulse starts about10.4ms later than its geometry event. These separate phases significantly improve alignment of the ridge.

A jointly fitted early amplitude correction is:

```
w = smoothstep(.005,.04,lightAge)
  * (1-smoothstep(.15,.27,lightAge))
clickExcessRGB *= 1 + .104509*w
```

The best width multiplier is0.998364 during the same window, effectively no width correction. The source does not support blindly narrowing the wave or applying23%extra gain across all early frames.

Overall source RGB MAE improves from(2.697,2.177,.930) to **(2.282,1.838,.859)**. More importantly, per-event luma MAE restricted to source crests above25 and ages below.3s improves:

| Event | Before | Refined |
|---|---:|---:|
| 408 | 5.824 | 3.501 |
| 562 | 5.189 | 3.544 |
| 637 | 6.975 | 2.653 |
| 776 | 8.162 | 3.750 |

A23%boost with the corrected light phases worsens overall RGB MAE to(2.425,1.943,.888) and overshoots several source radial peaks. For event637 atage.15, source tile-center radial luma peak is45.33: corrected timing alone predicts43.61,10.45%boost48.17,23%boost53.64. Event562 atage.05 has source peak29.74:10.45%boost predicts30.56 versus34.03 with23%. Event408's earliest peak would individually benefit from a larger gain, but applying that gain to all events is contradicted by the measured source.

These peak values are calculated from **tile centers** in registered native source data and therefore differ numerically from a rendered full-pixel radial profile containing dark seams. They isolate the material model; compare live captures again after phase correction before attributing a remaining rendered peak loss entirely to pulse amplitude.

Reproduce with `.venv-cursor/bin/python scripts/refine-click-peaks.py`. Standalone results and per-event/age crest ratios are in `reference/analysis/click-peak-refinement.json`.
