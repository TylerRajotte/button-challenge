# Strict dynamic review — reopened

The previous still-image review was insufficient to establish faithful interaction. Acceptance is reopened. The following findings come from the source video at native 60 fps, dense 100 ms contact sheets around click responses, and full-video segmentation of the blue button boundary. No app code was inspected.

## Source click behavior

The source contains **four** distinct click responses. Times below are visible-response estimates, not verified input-event timestamps. Coordinates and dimensions are normalized to 720 × 540.

| Response onset (approx.) | Pointer position | Baseline width | Minimum width | Minimum time |
|---|---:|---:|---:|---:|
| 6.78 s | 225, 287 | 327 px | 315 px | 6.867 s |
| 9.35 s | 497, 239 | 327 px | 311 px | 9.467 s |
| 10.62 s | 497, 302 | 327 px | 310 px | 10.733 s |
| 12.93 s | 265, 233 | 329 px | 312 px | 13.033 s |

Allow roughly 1–2 source frames of onset uncertainty. The cursor starts contracting around 100 ms before the button response. Therefore, do not assume cursor contraction alone identifies the ripple start.

The button contracts by roughly 4–5%, with minimum size about 100–120 ms after response onset, then recovers over approximately 140 ms. This affects the physical button pose, not merely tile brightness. A distinct expanding curved wavefront launches from the click location and travels across the whole face. It is clipped to the button. It does not behave like random glitter or a stationary radial spotlight.

Measured ring radii from luminance differences against pre-click frames, excluding text:

| Time | Third-click radius | Time | Fourth-click radius |
|---|---:|---|---:|
| 10.70 s | ~70 px | 13.00 s | ~60 px |
| 10.80 s | ~140 px | 13.10 s | ~149 px |
| 10.90 s | ~198 px | 13.20 s | ~200 px |

This supports propagation around **700 logical pixels/second**, with an edge click crossing the face in roughly 0.4–0.45 seconds. The bright band is several tiles wide. Exact ring shape is affected by perspective, tile discretization, and compression; these are measurement estimates rather than renderer constants.

The wave brightens tiles to pale periwinkle while **retaining dark-blue grid seams**. The region behind the wave returns toward the ordinary hover appearance. At 10.7–11.0 seconds, the wave travels from right to left; at 13.0–13.3 seconds, it travels left to right. This organized temporal progression is a required feature.

## Required evidence for the next quality gate

- Matched source/implementation frame sequences for all four clicks, sampled at least every 50 ms from before contraction through wave exit and recovery.
- Actual pointer-driven click capture, in addition to deterministic replay, showing that the same response occurs through the live interface.
- Verify ring position, width, direction, onset, propagation duration, button contraction/recovery, and grid contrast across the sequence; one attractive highlight still cannot establish equivalence.
- Compare idle, ordinary hover, wave peak, and post-wave states separately. Source idle seams are subdued; source illuminated seams remain strongly distinct. Tile fill and seam color must be judged independently.

## First revised dynamic comparison

Inspected all ten matched times in each of `click-replay/comparison-{408,562,637,776}.jpg` and measured body bounds in the corresponding exact PNG pairs. The fixed material calibration improves ordinary hover substantially, and all four clicks now produce traveling illumination. The gate remains **open** for these actionable differences:

1. **Traveling wave is too weak and diffuse.** At 7.000, 9.567, 10.817, and 13.133 seconds, the source has a bright, coherent, narrow band that remains visually distinct as it crosses the center. The recreation shows a weaker, broader, speckled region. Increase the traveling front's sustained contrast and retain its narrow spatial shape; distinguish it from the decaying tail. Conversely, recreation onset at 6.800 and 12.933 seconds spikes individual nearly white tiles around the pointer more strongly than the source. Do not solve the later weakness by uniformly increasing the entire pulse.
2. **Contraction recovery is too slow.** Blue-body width measurements: source/recreation at 6.950 seconds = 325/316 px; 9.567 = 325/316 px; 10.817 = 321/316 px; 13.133 = 326/318 px. The source has substantially recovered while the recreation remains compressed. The first response is also late: at 6.850 seconds widths are 316/321 px, then at 6.900 they are 320/314 px. Move its compression earlier and shorten recovery for all four.
3. **Body is consistently too tall.** Before and after clicks, source blue-body height is approximately 112 px versus recreation 114 px across the reviewed tilted poses. The top edge generally aligns, leaving the recreated lower edge roughly 2 px too low. Correct projected height or vertical pose rather than masking this with shadow changes.
4. **Label does not contract with the source.** The recreation keeps the label at full size during the deepest compression while the source label shrinks with the button. Preserve native sharpness by adjusting actual font size/letter spacing to the contraction amount rather than applying a blurry CSS transform.
5. **Stationary material stability still needs direct verification.** Hold the pointer at one location, wait until the hover response settles, and compare two frames at least one second apart. Repeat after a click has completely decayed. With no pointer movement, settled tile colors must remain stable. A fixed-material claim alone is insufficient; capture the live result. Also capture an actual live click, since deterministic replay does not prove event wiring.

The revised texture is substantially nearer the source, but the visibly weaker traveling front and slower compression recovery remain material interaction mismatches. Low mean pixel error over the entire face does not negate those localized temporal errors. No blanket acceptance is given.

## Geometry and compression follow-up

Re-inspected all four regenerated sequences after measured compression profiles and native label sizing were applied. The prior slow recovery and first-click lag are resolved in the sampled frames. Widths at the previously failing recovery points are now source/recreation: 6.950 s = 325/324 px, 9.567 s = 325/324 px, 10.817 s = 321/321 px, and 13.133 s = 326/326 px. The label visibly contracts with the body and remains sharp. Those two critiques are closed for the inspected sequences.

**Correction to the previous height diagnosis:** the broad blue threshold also included some of the recreation's denser lower shadow. With a stricter dark-face threshold, the face silhouettes differ by approximately 0–1 px in height, rather than the 2–3 px originally reported. The remaining visible difference is chiefly shadow density immediately underneath: at frame 405, centerline y=325 is source RGB (183, 200, 244) versus recreation (169, 188, 235). The recreation has a darker, denser lower shadow. Lighten that immediate shadow before making further large body-height changes. Resting face bounds are approximately 1 px wider/leftward in some samples; this is secondary and close to antialiasing uncertainty.

Wave critique remains open pending the new fit. Stationary stability and actual live-click captures are also still pending. No further substantive compression or native-label issue is visible in the updated sampled sequences.

## Fitted-wave follow-up

Re-inspected all four sequences after the source-fitted wave was applied. The previous major failure—weak, diffuse illumination disappearing while crossing the face—is resolved. A narrow bright front now persists through center and edge crossing, while dark-blue seams remain legible. Shadow and broad backdrop no longer show a substantial actionable mismatch in these comparisons.

Two refinements remain for the wave:

- **Early front intensity:** radial luminance gain against each sequence's pre-click baseline, excluding the label and averaging nearby radii, is source/recreation: 6.850 s = 29.2/22.0, 9.417 s = 27.6/22.7, 10.767 s = 37.5/29.8, and 12.983 s = 23.8/18.6 (8-bit luminance units). Thus the early traveling front still tends to be weaker, although later first/second-event peaks are within approximately 1–3 units. Check early envelope or leading-band color rather than increasing the whole pulse globally.
- **Fourth-event alignment:** the fourth sequence's brightest traveling region appears somewhat behind the source at 13.083, 13.133, and 13.233 seconds. Check its event start offset separately before changing global propagation speed. Radial peak locations are affected by individual tile brightness, so their displacement alone is not a reliable physical front-radius measurement.

Independently loaded and compared `live-click/stationary-a.png` and `stationary-b.png`: same 720 × 540 dimensions, every pixel identical, maximum channel delta zero. The inspected stationary frame also looks settled. This closes the stationary-drift critique for that capture. The provided live-click measurements show a scale minimum of 0.973757 followed by recovery to 1.03; latest-wave live visual capture remains to be reviewed.

## Live capture audit

Decoded the supplied latest `live-click/interaction.webm` at its recorded 25 fps and made `live-click/review-dense.png` at 40 ms intervals. The live click clearly triggers a wave that propagates across the face and then fades, confirming live event wiring. However, this recording does **not** capture its onset or compression: frames remain visually unchanged through 3.120 s, then 3.160 s abruptly shows the wave already near the center/left and the button nearly recovered. Face-width minimum after the first second is approximately 326 px, versus approximately 327 px baseline—so the expected 4–5% contraction is absent from the recording even though JS scale measurements report it.

Frame-to-frame button-region mean pixel difference is only 0.072 (maximum 2, consistent with codec noise) throughout 2.44–3.12 s, then jumps to 11.822 (maximum 197) at 3.16 s. This may be a recording artifact or capture starvation; it is not proof the app itself skipped its opening animation. Recapture without concurrent expensive screenshots/measurements, or provide direct live-render frames at approximately 40 ms intervals covering the actual click. The live onset/compression gate remains open until that missing interval is visible. Stationary PNGs were rechecked and remain exactly identical.

## Final review decision — gate closed for the reviewed scope

Re-inspected all 40 matched click frames after the early-envelope correction and individual light-timing offsets. The systematic early-wave weakness and fourth-event lag are resolved. Independent baseline-subtracted radial luminance checks now give source/recreation: 9.517 s = 37.7/38.0, 10.767 s = 37.5/36.6, 10.817 s = 39.4/39.5, and 13.083 s = 31.8/31.3. At 13.233 s, both radial peaks lie at approximately 246 px. Some isolated tile/radius samples still differ, but they no longer establish a consistent visual defect with a supported corrective direction. Do not apply further global brightness or timing changes based on an isolated peak.

Reviewed `live-click/direct/contact-sheet.jpg`, its measurements, and `scripts/capture-live-frames.mjs` to verify capture validity. The script issues a real trusted mouse click and observes the canvas immediately after the normal renderer runs; it does not freeze the timeline or reconstruct the frame. Its 46 captured frames include 12 within the first 200 ms. They visibly show the missing onset, contraction, traveling wave, recovery, and fade. Minimum scale is 0.973745 at approximately 127 ms, returning to 1.03; native font-size measurements follow the contraction. This closes the live onset/compression evidence gap. Native label appearance was assessed separately in the matched full-page captures because the direct canvas excludes it.

All identified actionable critiques are now closed within the reviewed scope: material stability, tile/seam treatment, traveling wave, timing, compression/recovery, native label behavior, shadow/backdrop, and live event rendering. There is **no remaining actionable visual critique from this evidence**.

This is a visual quality-gate decision based on the four recorded source click sequences, sampled source hover states, a trusted live click, and the stationary comparison. It does not claim pixel equivalence to a compressed reference video or exhaustive certification of every viewport, device, or possible interaction.

## Evidence

- `review-click/click-6.png`, `click-9.png`, `click-10.png`, `click-13.png`: dense source sequences.
- `review-click/bounds.json`: measured blue-button bounds for all 1,183 source frames.
- `review-click/source-10.70.png`, `source-10.80.png`, `source-13.00.png`, `source-13.10.png`: clear source wavefront examples.
