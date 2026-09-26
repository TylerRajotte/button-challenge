# Pixel ripple button

An interactive Three.js / WebGL recreation of [Raul Dronca’s Pixel Ripple Button](https://x.com/raul_dronca/status/2093270659824529461).

## Run

```sh
npm install
npm run dev
```

Vite listens on all interfaces at port **5173**, with a strict port so it cannot silently switch addresses. Open `http://localhost:5173` for local development.

- `/` — interactive button, source-motion replay, and optional virtual touchpad.
- `/?compare` — original video beside the interactive recreation, with synchronized cursor replay and timeline scrubbing.
- `/?clean` — faithful uncluttered composition for screenshots.

The touchpad is off by default on every device. Select **Use touchpad** to open it. Slide a finger to move its virtual cursor; lifting preserves hover. Tap the pad or use **Click** to press the button. The panel can be closed. Direct touch, mouse input, Enter and Space are also supported. There is no destination behind “Get started”; activation produces a ripple and emits an `activate` DOM event.

## Rendering

A beveled squircle mesh uses Three.js `MeshPhysicalMaterial`, real perspective rotation, and a calibrated custom color shader. Each of the 40 × 13 tiles has fixed measured color and light-response parameters. A pointer-following light reveals those differences; tiles do not shimmer or animate independently. Grid seams have their own measured response. Clicks launch a narrow expanding illumination front and briefly contract the mesh and label.

The shader uses numerical material parameters fitted from the reference, with a calibrated linear-to-sRGB lighting transfer. No video frame or screenshot is used as the button texture. A 900px perspective, up to 9° pointer-driven tilt, 1.03 hover scale, and four measured click profiles reproduce the source motion. Native DOM text sits outside transformed layers and updates its actual font size during compression. The canvas renders at 2–4× density. The background and contact shadow use CSS. Reduced-motion preferences disable temporal surface motion and tilt.

The composition follows the source's approximately 320 × 106 button in a 720 × 540 logical frame. It scales to fit the viewport. `public/material-calibration.json` stores fixed tile palettes, independent seam parameters, and the measured light model; `public/button-pose-model.json` and `public/click-profiles.json` document the source geometry and compression.

## Reference and verification

- `reference/source.mp4` — downloaded 2876 × 2160, 60 fps source video, 19.7167 seconds.
- `reference/all-frames/` — all 1,183 frames at 60 fps as 720 × 540 JPEGs.
- `reference/frames/` — 39 frames sampled at 2 fps, scaled to 720px wide.
- `reference/keyframes/` — 10 original-resolution keyframes sampled every two seconds.
- `reference/contact-sheet.jpg` — visual overview.
- `public/cursor-track.json` — measured source cursor trajectory, with one sample per source frame.
- `evidence/` — visual comparisons and interaction verification.

The original reference video and contact sheet are copied under `public/reference/` so they also work in a production build. Source creative work remains credited to Raul Dronca. Inter is distributed under the SIL Open Font License; see `public/fonts/Inter-LICENSE.txt`.

```sh
npm run build
npm test        # With the dev server running; Chromium / Playwright required
npm run capture # Writes idle and hover screenshots under evidence/
node scripts/capture-replay.mjs # Synchronized screenshots and replay/text checks
node scripts/capture-clicks.mjs # 40 matched frames across all four clicks
node scripts/capture-live-frames.mjs # Actual trusted click, frame-by-frame WebGL evidence
.venv-cursor/bin/python scripts/compare-pixels.py # Regional RGB metrics
.venv-cursor/bin/python scripts/compare-clicks.py # Click metrics and paired contact sheets
```

The browser scripts use Playwright’s installed Chromium, an available local cached Chromium, or `BROWSER_PATH`. Browser tests cover iPad touchpad dragging, hover retention, tapping, explicit click, keyboard activation, source video loading, replay synchronization, mobile orientation, and reduced-motion behavior. Screenshots are compared repeatedly against extracted frames and reviewed by an independent agent. Pixel comparisons exclude text where measuring material color and examine click onset, propagation, and recovery separately. Original shader code, input-event timestamps, and materials are unavailable; the source is compressed video, so exact pixel identity is not established. The numerical fit and independent review are documented in `evidence/material-measurement.md`, `evidence/pixel-comparison.md`, and `evidence/review-next.md`.

## Public transcript and deployment

`transcript.html` presents 37 user/assistant messages through the publication request; `public/transcript.md` is the text copy. Agent questions are attributed separately from user replies, and timestamps show the original local session time. Private network addresses and machine paths are redacted. Internal instructions, tool output, and agent-only discussions are excluded. The original public X post is credited throughout the site. No analytics or tracking scripts are included.

The Pages workflow builds with the repository's base path, then deploys the static `dist` artifact. To test a project path locally, run `BASE_PATH=/button-challenge/ npm run build`, then `npm run preview` and open `http://localhost:4173/button-challenge/`.

Bulk downloaded frames under `reference/` and generated screenshot/video captures under `evidence/` remain local and are excluded from Git. Public reference video, calibration data, analysis scripts, and selected review reports are included. Frame-analysis scripts require the downloaded reference and Python dependencies NumPy, Pillow, OpenCV, and SciPy.
