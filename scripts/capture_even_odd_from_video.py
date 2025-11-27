"""
Capture Even/Odd Betting Coordinates from Video File
Allows frame-by-frame navigation and coordinate capture from video.
"""

import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk


class VideoCoordinateCapture:
    """GUI for capturing coordinates from video frames."""
    
    def __init__(self, video_path: str):
        """Initialize with video file."""
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        # Open video
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.current_frame = 0
        
        # Load first frame
        self.coordinates: Dict[str, list] = {}
        self.current_target = "even"
        self.current_image = None
        self.scale = 1.0
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Even/Odd Coordinate Capture from Video")
        self.root.geometry("1400x900")
        
        # Top frame for controls
        control_frame = tk.Frame(self.root, bg="lightgray")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Video controls
        tk.Label(control_frame, text="Video Controls:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="⏮ First", command=self._first_frame, bg="lightblue").pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="⏪ Prev", command=self._prev_frame, bg="lightblue").pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="⏸ Pause", command=self._pause, bg="yellow").pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="⏩ Next", command=self._next_frame, bg="lightblue").pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="⏭ Last", command=self._last_frame, bg="lightblue").pack(side=tk.LEFT, padx=2)
        
        # Frame number display
        self.frame_label = tk.Label(control_frame, text="Frame: 0/0", font=("Arial", 10))
        self.frame_label.pack(side=tk.LEFT, padx=10)
        
        # Frame slider
        self.frame_var = tk.IntVar()
        self.frame_slider = ttk.Scale(
            control_frame,
            from_=0,
            to=self.total_frames - 1,
            orient=tk.HORIZONTAL,
            variable=self.frame_var,
            command=self._on_slider_change,
            length=300
        )
        self.frame_slider.pack(side=tk.LEFT, padx=10)
        
        # Canvas for image
        self.canvas = tk.Canvas(self.root, cursor="crosshair", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Instructions
        self.instructions = tk.Label(
            self.root,
            text="Navigate to a frame showing the betting table, then click on PAR (Even) and ÍMPAR (Odd) buttons",
            bg="lightblue",
            font=("Arial", 11),
            wraplength=1200
        )
        self.instructions.pack(fill=tk.X, padx=5, pady=2)
        
        # Status
        self.status = tk.Label(
            self.root,
            text="Use video controls to find a good frame, then click on PAR button",
            bg="lightyellow",
            font=("Arial", 10)
        )
        self.status.pack(fill=tk.X, padx=5, pady=2)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(
            button_frame,
            text="Reset Even",
            command=lambda: self._reset("even"),
            bg="lightcoral"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Reset Odd",
            command=lambda: self._reset("odd"),
            bg="lightcoral"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Save & Exit",
            command=self._save_and_exit,
            bg="lightgreen",
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        # Bind mouse click
        self.canvas.bind("<Button-1>", self._on_click)
        
        # Bind keyboard shortcuts
        self.root.bind("<Left>", lambda e: self._prev_frame())
        self.root.bind("<Right>", lambda e: self._next_frame())
        self.root.bind("<space>", lambda e: self._pause())
        self.root.bind("<Home>", lambda e: self._first_frame())
        self.root.bind("<End>", lambda e: self._last_frame())
        
        # Load first frame
        self._load_frame(0)
        self._update_status()
    
    def _load_frame(self, frame_number: int):
        """Load and display a specific frame."""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        
        if not ret:
            return False
        
        self.current_frame = frame_number
        self.frame_var.set(frame_number)
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        self.current_image = Image.fromarray(frame_rgb)
        
        # Display
        self._display_image()
        return True
    
    def _display_image(self):
        """Display current frame on canvas."""
        if self.current_image is None:
            return
        
        # Get canvas size
        self.root.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 1200
            canvas_height = 800
        
        # Calculate scale
        img_width, img_height = self.current_image.size
        scale_w = canvas_width / img_width
        scale_h = canvas_height / img_height
        self.scale = min(scale_w, scale_h, 1.0)
        
        # Resize for display
        display_width = int(img_width * self.scale)
        display_height = int(img_height * self.scale)
        display_image = self.current_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(display_image)
        
        # Display
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Draw markers
        self._draw_markers()
        
        # Update frame label
        self.frame_label.config(text=f"Frame: {self.current_frame + 1}/{self.total_frames}")
    
    def _draw_markers(self):
        """Draw markers for captured coordinates."""
        for bet_type, coords in self.coordinates.items():
            if coords:
                x = int(coords[0] * self.scale)
                y = int(coords[1] * self.scale)
                
                color = "green" if bet_type == "even" else "blue"
                label = "PAR" if bet_type == "even" else "ÍMPAR"
                self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=color, outline="white", width=2)
                self.canvas.create_text(x, y-25, text=label, fill=color, font=("Arial", 14, "bold"), bg="white")
    
    def _on_click(self, event):
        """Handle mouse click."""
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        
        if self.current_target:
            self.coordinates[self.current_target] = [x, y]
            print(f"   Captured {self.current_target.upper()}: [{x}, {y}]")
            self._display_image()
            self._update_status()
    
    def _update_status(self):
        """Update status label."""
        if "even" not in self.coordinates or not self.coordinates["even"]:
            self.current_target = "even"
            self.status.config(
                text=" Click on PAR button (Even) - Use arrow keys or buttons to navigate video",
                bg="lightyellow"
            )
        elif "odd" not in self.coordinates or not self.coordinates["odd"]:
            self.current_target = "odd"
            self.status.config(
                text=" Click on ÍMPAR button (Odd) - Use arrow keys or buttons to navigate video",
                bg="lightyellow"
            )
        else:
            self.current_target = None
            even_coords = self.coordinates.get("even", [])
            odd_coords = self.coordinates.get("odd", [])
            self.status.config(
                text=f" Both captured! Even: {even_coords}, Odd: {odd_coords} - Click 'Save & Exit'",
                bg="lightgreen"
            )
    
    def _reset(self, bet_type: str):
        """Reset coordinate."""
        if bet_type in self.coordinates:
            del self.coordinates[bet_type]
            self._display_image()
            self._update_status()
            print(f"  ↻ Reset {bet_type}")
    
    def _first_frame(self):
        """Go to first frame."""
        self._load_frame(0)
    
    def _prev_frame(self):
        """Go to previous frame."""
        if self.current_frame > 0:
            self._load_frame(self.current_frame - 1)
    
    def _next_frame(self):
        """Go to next frame."""
        if self.current_frame < self.total_frames - 1:
            self._load_frame(self.current_frame + 1)
    
    def _last_frame(self):
        """Go to last frame."""
        self._load_frame(self.total_frames - 1)
    
    def _pause(self):
        """Pause/continue playback (not implemented, just for button)."""
        pass
    
    def _on_slider_change(self, value):
        """Handle slider change."""
        frame_num = int(float(value))
        if frame_num != self.current_frame:
            self._load_frame(frame_num)
    
    def _save_and_exit(self):
        """Save and exit."""
        if "even" not in self.coordinates or not self.coordinates["even"]:
            messagebox.showwarning("Missing Coordinate", "Please capture Even (PAR) coordinate first.")
            return
        if "odd" not in self.coordinates or not self.coordinates["odd"]:
            messagebox.showwarning("Missing Coordinate", "Please capture Odd (ÍMPAR) coordinate first.")
            return
        
        self.cap.release()
        self.root.quit()
        self.root.destroy()
    
    def run(self) -> Dict[str, list]:
        """Run the GUI."""
        self.root.mainloop()
        return self.coordinates


def capture_from_video(video_path: str, output_file: str = "even_odd_coordinates.json") -> Dict[str, list]:
    """
    Capture Even/Odd coordinates from video file.
    
    Args:
        video_path: Path to video file
        output_file: Output JSON file path
        
    Returns:
        Dictionary with coordinates
    """
    print("=" * 70)
    print("EVEN/ODD COORDINATE CAPTURE FROM VIDEO")
    print("=" * 70)
    print(f"\nVideo: {video_path}")
    print("\nInstructions:")
    print("  1. A window will open with video controls")
    print("  2. Navigate to a frame showing the betting table clearly")
    print("  3. Click on the PAR button (Even)")
    print("  4. Click on the ÍMPAR button (Odd)")
    print("  5. Click 'Save & Exit' when done")
    print("\nControls:")
    print("  - Arrow keys: Navigate frames")
    print("  - Slider: Jump to any frame")
    print("  - Buttons: First, Prev, Next, Last")
    print("\nPress Enter to start...")
    input()
    
    try:
        app = VideoCoordinateCapture(video_path)
        coordinates = app.run()
        
        if coordinates and "even" in coordinates and "odd" in coordinates:
            # Save to file
            output_path = Path(output_file)
            output_path.write_text(json.dumps(coordinates, indent=2), encoding="utf-8")
            
            print("\n" + "=" * 70)
            print("COORDINATES SAVED")
            print("=" * 70)
            print(f"\nSaved to: {output_path.resolve()}")
            print("\nCoordinates:")
            print(f"  EVEN (Par): {coordinates['even']}")
            print(f"  ODD (Ímpar): {coordinates['odd']}")
            
            print("\n" + "=" * 70)
            print("CONFIG SNIPPET")
            print("=" * 70)
            print("\nAdd this to your config file:")
            print('"betting": {')
            print('  "betting_areas": {')
            print('    // ... existing entries ...')
            print(f'    "even": {coordinates["even"]},')
            print(f'    "odd": {coordinates["odd"]},')
            print('  },')
            print('}')
            
            return coordinates
        else:
            print("\n Coordinates not captured completely.")
            return {}
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python capture_even_odd_from_video.py <video_path>")
        print("\nExample:")
        print("  python capture_even_odd_from_video.py roleta_brazileria.mp4")
        print("\nOr enter video path when prompted:")
        video_path = input("Enter path to video file: ").strip()
    else:
        video_path = sys.argv[1]
    
    if not video_path:
        print("Error: No video path provided.")
        sys.exit(1)
    
    try:
        capture_from_video(video_path)
    except KeyboardInterrupt:
        print("\n\nCapture aborted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

