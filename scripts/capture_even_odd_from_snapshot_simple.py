"""
Capture Even/Odd Betting Coordinates from Snapshot (Simple Version)
Uses PIL/Pillow instead of OpenCV for better compatibility.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox


class CoordinateCaptureGUI:
    """Simple GUI for capturing coordinates from snapshot."""
    
    def __init__(self, image_path: str):
        """Initialize with snapshot image."""
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        self.image = Image.open(self.image_path)
        self.coordinates: Dict[str, list] = {}
        self.current_target = None
        
        # Zoom state (initialize before _display_image is called)
        self.zoom_level = 1.0
        self.base_scale = 1.0
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Even/Odd Coordinate Capture - Click on Par and Ímpar buttons")
        
        # Set initial window size (larger)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(screen_width - 100, 1600)
        window_height = min(screen_height - 100, 1000)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Create canvas for image with scrollbars
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            cursor="crosshair",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            bg="gray"
        )
        
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Display image
        self._display_image()
        
        # Bind mouse click
        self.canvas.bind("<Button-1>", self._on_click)
        
        # Instructions label
        self.instructions = tk.Label(
            self.root,
            text="Click on PAR button (Even), then ÍMPAR button (Odd)",
            bg="lightblue",
            font=("Arial", 12)
        )
        self.instructions.pack(fill=tk.X)
        
        # Status label
        self.status = tk.Label(
            self.root,
            text="Ready - Click on PAR button",
            bg="lightyellow",
            font=("Arial", 10)
        )
        self.status.pack(fill=tk.X)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Zoom controls
        zoom_frame = tk.Frame(button_frame)
        zoom_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(zoom_frame, text="Zoom:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(
            zoom_frame,
            text="+",
            command=self._zoom_in,
            bg="lightblue",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            zoom_frame,
            text="-",
            command=self._zoom_out,
            bg="lightblue",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            zoom_frame,
            text="Fit",
            command=self._zoom_fit,
            bg="lightblue"
        ).pack(side=tk.LEFT, padx=2)
        
        # Reset and Save buttons
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
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        # Set current target
        self.current_target = "even"
        self._update_status()
        
        # Bind mouse wheel for zoom
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux
        self.canvas.focus_set()  # Allow canvas to receive focus for mouse wheel
    
    def _display_image(self):
        """Display image on canvas."""
        # Get canvas size
        self.root.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # If canvas not ready, use default size
        if canvas_width <= 1:
            canvas_width = 1500
            canvas_height = 900
        
        # Get original image size
        img_width, img_height = self.image.size
        
        # Calculate base scale to fit canvas
        scale_w = (canvas_width * 0.95) / img_width
        scale_h = (canvas_height * 0.95) / img_height
        self.base_scale = min(scale_w, scale_h)
        
        # Apply zoom level
        self.scale = self.base_scale * self.zoom_level
        
        # Resize image for display
        display_width = int(img_width * self.scale)
        display_height = int(img_height * self.scale)
        display_image = self.image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(display_image)
        
        # Display on canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update scroll region
        self.canvas.config(scrollregion=(0, 0, display_width, display_height))
        
        # Draw existing markers
        self._draw_markers()
    
    def _zoom_in(self):
        """Zoom in on image."""
        self.zoom_level = min(self.zoom_level * 1.2, 4.0)  # Max 4x zoom
        self._display_image()
    
    def _zoom_out(self):
        """Zoom out on image."""
        self.zoom_level = max(self.zoom_level / 1.2, 0.5)  # Min 0.5x zoom
        self._display_image()
    
    def _zoom_fit(self):
        """Reset zoom to fit window."""
        self.zoom_level = 1.0
        self._display_image()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel for zoom."""
        if event.delta > 0 or event.num == 4:
            self._zoom_in()
        elif event.delta < 0 or event.num == 5:
            self._zoom_out()
    
    def _draw_markers(self):
        """Draw markers for captured coordinates."""
        for bet_type, coords in self.coordinates.items():
            if coords:
                # Convert to display coordinates
                x = int(coords[0] * self.scale)
                y = int(coords[1] * self.scale)
                
                # Draw circle
                color = "green" if bet_type == "even" else "blue"
                label = "PAR" if bet_type == "even" else "ÍMPAR"
                self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color, outline="black", width=2)
                self.canvas.create_text(x, y-20, text=label, fill=color, font=("Arial", 12, "bold"))
    
    def _on_click(self, event):
        """Handle mouse click on canvas."""
        # Convert display coordinates to original image coordinates
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        
        # Store coordinate
        if self.current_target:
            self.coordinates[self.current_target] = [x, y]
            print(f"   Captured {self.current_target.upper()}: [{x}, {y}]")
            
            # Update display
            self._display_image()
            self._update_status()
    
    def _update_status(self):
        """Update status label."""
        if "even" not in self.coordinates or not self.coordinates["even"]:
            self.current_target = "even"
            self.status.config(
                text="Click on PAR button (Even) - Coordinates will appear here",
                bg="lightyellow"
            )
        elif "odd" not in self.coordinates or not self.coordinates["odd"]:
            self.current_target = "odd"
            self.status.config(
                text="Click on ÍMPAR button (Odd) - Coordinates will appear here",
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
        """Reset coordinate for bet type."""
        if bet_type in self.coordinates:
            del self.coordinates[bet_type]
            self._display_image()
            self._update_status()
            print(f"  ↻ Reset {bet_type}")
    
    def _save_and_exit(self):
        """Save coordinates and exit."""
        if "even" not in self.coordinates or not self.coordinates["even"]:
            messagebox.showwarning("Missing Coordinate", "Please capture Even (PAR) coordinate first.")
            return
        if "odd" not in self.coordinates or not self.coordinates["odd"]:
            messagebox.showwarning("Missing Coordinate", "Please capture Odd (ÍMPAR) coordinate first.")
            return
        
        self.root.quit()
        self.root.destroy()
    
    def run(self) -> Dict[str, list]:
        """Run the GUI and return coordinates."""
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.root.mainloop()
        return self.coordinates


def capture_from_snapshot(image_path: str, output_file: str = "even_odd_coordinates.json") -> Dict[str, list]:
    """
    Capture Even/Odd coordinates from a snapshot image.
    
    Args:
        image_path: Path to snapshot image file
        output_file: Output JSON file path
        
    Returns:
        Dictionary with coordinates
    """
    print("=" * 70)
    print("EVEN/ODD COORDINATE CAPTURE FROM SNAPSHOT")
    print("=" * 70)
    print(f"\nImage: {image_path}")
    print("\nInstructions:")
    print("  1. A window will open showing your snapshot")
    print("  2. Click on the PAR button (Even)")
    print("  3. Click on the ÍMPAR button (Odd)")
    print("  4. Click 'Save & Exit' when done")
    print("\nPress Enter to start...")
    input()
    
    try:
        app = CoordinateCaptureGUI(image_path)
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
        print("Usage: python capture_even_odd_from_snapshot_simple.py <image_path>")
        print("\nExample:")
        print("  python capture_even_odd_from_snapshot_simple.py snapshot.png")
        print("\nOr enter image path when prompted:")
        image_path = input("Enter path to snapshot image: ").strip()
    else:
        image_path = sys.argv[1]
    
    if not image_path:
        print("Error: No image path provided.")
        sys.exit(1)
    
    try:
        capture_from_snapshot(image_path)
    except KeyboardInterrupt:
        print("\n\nCapture aborted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

