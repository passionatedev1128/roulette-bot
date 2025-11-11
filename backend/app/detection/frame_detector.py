"""
Frame Detection Module
Reads frames from a video source instead of capturing the desktop.
"""

import cv2
import logging
from typing import Optional

from .screen_detector import ScreenDetector

logger = logging.getLogger(__name__)


class FrameDetector(ScreenDetector):
    """Detector that reads frames from a video file (cv2.VideoCapture)."""

    def __init__(self, config, video_path: str):
        super().__init__(config)
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Unable to open video source: {video_path}")
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        logger.info("FrameDetector initialized with %s (%dx%d)", video_path, self.frame_width, self.frame_height)

    def capture_screen(self) -> Optional[cv2.Mat]:
        """Return the next frame from the video source."""
        ret, frame = self.cap.read()
        if not ret:
            logger.info("Video ended, restarting: %s", self.video_path)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame after restart.")
                return None
        return frame

    def release(self):
        """Release the video capture."""
        if self.cap:
            self.cap.release()
            self.cap = None


