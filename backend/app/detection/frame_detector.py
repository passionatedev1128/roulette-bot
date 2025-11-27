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

    def __init__(self, config, video_path: str, start_frame: int = 1000):
        super().__init__(config)
        self.video_path = video_path
        self.start_frame = start_frame
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Unable to open video source: {video_path}")
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        logger.info("FrameDetector initialized with %s (%dx%d, %d frames, %.2f fps)", 
                   video_path, self.frame_width, self.frame_height, total_frames, fps)
        
        # Validate start_frame
        if start_frame >= total_frames:
            logger.warning("Start frame (%d) >= total frames (%d), using frame 0 instead", start_frame, total_frames)
            self.start_frame = 0
        elif start_frame < 0:
            logger.warning("Start frame (%d) is negative, using frame 0 instead", start_frame)
            self.start_frame = 0
        
        # Verify we can read at least one frame
        ret, test_frame = self.cap.read()
        if not ret or test_frame is None:
            logger.error(
                "Video file appears to be empty or unreadable. No frames available. "
                "Video info: %d frames, %dx%d, %.2f fps. "
                "Please verify the video file is valid and contains frames.",
                total_frames, self.frame_width, self.frame_height, fps
            )
            # Reset to beginning for actual use
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            # Set to start_frame after test read
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            logger.info("Video file verified: can read frames successfully (%d frames available)", total_frames)
            logger.info("Starting from frame %d", self.start_frame)
        
        # Track the actual frame number being processed (0-based)
        self.current_frame_number = self.start_frame

    def get_current_frame_number(self) -> int:
        """Get the current frame number that was just read (0-based index)."""
        return self.current_frame_number
    
    def capture_screen(self) -> Optional[cv2.Mat]:
        """
        Return the next frame from the video source.
        
        Returns None when video ends (does not auto-restart).
        For continuous looping, use restart_video() and call capture_screen() again.
        """
        # Get the frame number we're about to read
        frame_number_before = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) if self.cap else -1
        ret, frame = self.cap.read()
        if not ret:
            # Video has ended - return None instead of restarting
            # This allows callers to detect end of video and handle it appropriately
            logger.debug("Video ended at frame %d: %s", frame_number_before, self.video_path)
            return None
        
        # Update the current frame number to the one we just read
        self.current_frame_number = frame_number_before
        
        # Log the frame number that was just read with more detail (reduce logging frequency for performance)
        if self.current_frame_number % 30 == 0:  # Log every 30 frames to reduce I/O
            logger.info("Processing frame %d (absolute frame number in video)", self.current_frame_number)
        else:
            logger.debug("Processing frame %d", self.current_frame_number)
        
        return frame
    
    def restart_video(self):
        """Restart video from the start_frame."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            self.current_frame_number = self.start_frame
            logger.info("Video restarted from frame %d: %s", self.start_frame, self.video_path)

    def release(self):
        """Release the video capture."""
        if self.cap:
            self.cap.release()
            self.cap = None


