# Roulette Bot Implementation Workflow

## 1. Capture & Calibrate the UI
- Launch the LUCK.BET roulette table at the resolution you intend to automate.
- Run `python coordinate_capture_tool.py` and capture:
  - `detection.screen_region`: bounding box of the winning-number badge.
  - `betting.betting_areas.red` / `betting.betting_areas.black`.
  - `betting.chip_selection` and `betting.confirm_button` (if required).
- Use the built-in navigation (`n` / `p`) to skip or recapture targets.
- Verify the values with `python coordinate_capture_tool.py test <config-path>` before committing them to your config file.

## 2. Build & Verify Detection Templates
- Record or pause gameplay to capture frames of the winning-number overlay (not the betting grid).
- For each captured frame, crop the digit tightly and save as `templates/number_<n>.png`.
- Run `python test_templates_with_snapshot.py <snapshot.png>` to confirm:
  - The winning number is detected with high confidence.
  - Other templates stay below the acceptance threshold (no false positives).
- Optional: set `--visualize` so a debug image is saved with template matches.

## 3. Align the Screen Region for Video Testing
- Execute `python test_video.py <video>.mp4 --config <config>.json`.
- Ensure the on-screen green rectangle surrounds the winning-number badge.
- If the rectangle is off, adjust `detection.screen_region`:
  - For pre-cropped videos, use `[0, 0, frame_width, frame_height]`.
  - Otherwise, recapture the coordinates from the video frame.
- Re-run the test until `method` reads `template` or `ocr` with valid numbers; avoid falling back to `None` or `color_fallback`.

## 4. Configure Strategy & Risk Parameters
- Set your preferred strategy in `config/default_config.json` (or another profile):
  - `strategy.type`: `martingale`, `fibonacci`, or `custom`.
  - `strategy.base_bet`, `max_gales`, `multiplier`, etc.
  - `risk.initial_balance`, `stop_loss`, and guarantee fund allocation.
- Confirm `betting.requires_amount_entry` and chip coordinates reflect the current casino behaviour.

## 5. Dry-Run the Bot
- Start `python main.py --config <config>.json --test`.
- Mock or replay detection results to confirm strategy and logging flow.
- Review `logs/` to ensure spins, bets, and errors are recorded correctly.

## 6. Bring Up the Web Interface
- Install dependencies:
  - Backend: `pip install -r requirements.txt`.
  - Frontend: `cd web && npm install`.
- Start services:
  - API: `uvicorn backend.server.app:app --reload`.
  - Dashboard: `npm run dev`.
- With the bot in test mode, open the dashboard, verify live status, balance, results, and configuration panels, and try start/stop/mode changes.

## 7. Live Trial (Supervised)
- Run the bot against the live table using small chip values.
- Compare logged detections with the game UI; ensure no “sticky” numbers occur.
- Monitor the dashboard and console logs; be ready to stop the bot if detection drifts.

## 8. Monitoring & Maintenance
- Periodically re-run `test_templates_with_snapshot.py` and `test_video.py` after UI or layout changes.
- Archive working configurations (e.g. `config/backup/default_config_YYYYMMDD.json`).
- Update `NEXT_STEPS_TEMPLATES_VERIFIED.md` with calibration details, template updates, and testing notes for future reference.


