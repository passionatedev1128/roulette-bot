# Roulette Bot Testing Playbook

## 1. Snapshot Testing (Winning Badge)
- Capture a badge image:  
  `python capture_winning-numbers.py --region <x y width height> --count 1 --output winning-numbers`
- Test OCR/templates on a single snapshot:  
  `python test_winning-number_snapshot.py winning-numbers/winning-number_22.png --config config/winning-number_snapshot_config.json`
- Expected output: correct number with `method: template_badge` (or `ocr` when template absent).

## 2. Video Replay Testing
- Run against recorded footage:  
  `python test_video.py roleta_brazileria.mp4 --config config/default_config.json`
- Use `--start <seconds>` to skip ahead and `--skip <n>` to sample frames:  
  `python test_video.py roleta_brazileria.mp4 --config config/default_config.json --start 120 --skip 2`
- Add `--display` if you want to view frames on a GUI-enabled machine.
- Check console summary and JSON output in `test_results/`.

## 3. Bot Dry Run
- Execute the bot in simulation mode:  
  `python main.py --config config/default_config.json --test`
- Verify logs in `logs/` (numbers should show `template_badge` or `ocr`).

## 4. Web Interface Validation (Optional)
- Backend: `uvicorn backend.server.app:app --reload`
- Frontend:  
  ```
  cd web
  npm install
  npm run dev
  ```
- Use the dashboard to monitor detections, stats, and try start/stop commands while the bot is in test mode.

## 5. Live Supervised Trial
- Run the bot against the live table with minimal stakes.
- Capture new winning numbers during play to expand `winning-numbers/`.
- Monitor logs/dashboard and ensure detections remain accurate.

## 6. Debugging Tips
- Enable `ocr_debug` in the config to write preprocessing variants to `ocr_debug/`.
- Check `test_results/*.json` for detection rates and method breakdowns.
- Re-run `test_video.py` after any template or config changes.
- Maintain `NEXT_STEPS_TEMPLATES_VERIFIED.md` with dates and detection metrics.

