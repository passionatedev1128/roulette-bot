"""
Run FrameDetector against a video file to test detection without screen capture.
"""

from backend.app.detection.frame_detector import FrameDetector
from backend.app.config_loader import ConfigLoader


def main():
    config_path = "config/default_config.json"
    video_path = "roleta_brazileria.mp4"

    config = ConfigLoader.load_config(config_path)
    detector = FrameDetector(config, video_path)

    try:
        while True:
            frame = detector.capture_screen()
            if frame is None:
                break
            result = detector.detect_result(frame)
            print(result)
    finally:
        detector.release()


if __name__ == "__main__":
    main()


