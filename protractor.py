import tkinter as tk
import math
import json
import os
from PIL import ImageGrab

CONFIG_FILE = "window_positions.json"

def load_window_positions():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_window_positions(positions):
    with open(CONFIG_FILE, "w") as f:
        json.dump(positions, f)

class ProtractorApp:
    def __init__(self, root, is_slope=False, geometry=None, on_move=None):
        self.root = root
        self.root.title("Protractor Overlay" if not is_slope else "Slope Measure Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
        self.width = 250
        self.height = 250
        self.is_slope = is_slope
        self.on_move = on_move

        if geometry:
            self.root.geometry(geometry)
        else:
            self.root.geometry(f"{self.width}x{self.height}+2000+1000" if not is_slope else f"{self.width}x{self.height}+800+1000")

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, 
                              bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.draw_protractor()
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<Button-3>', self.report_angle_from_center)  # Add this line
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.angle_label = tk.Label(self.root, text="Angle: --°", font=('Arial', 10), bg='white')
        self.angle_label.place(x=10, y=10)

    def draw_protractor(self):
        center_x = self.width / 2
        center_y = self.height / 2
        radius = min(self.width, self.height) * 0.28

        # Draw semicircle
        self.canvas.create_arc(center_x - radius, center_y - radius,
                             center_x + radius, center_y + radius,
                             start=0, extent=359, style='arc', width=2)

        # Draw angle markings
        for angle in range(0, 359, 10):
            rad = math.radians(angle)
            x1 = center_x + radius * math.cos(rad)
            y1 = center_y - radius * math.sin(rad)
            x2 = center_x + (radius + 10) * math.cos(rad)
            y2 = center_y - (radius + 10) * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2)
            # Add angle labels
            label_x = center_x + (radius + 20) * math.cos(rad)
            label_y = center_y - (radius + 20) * math.sin(rad)
            angle_text = str(angle) if not self.is_slope else f"{angle//10%18}"
            self.canvas.create_text(label_x, label_y, text=angle_text, font=('Arial', 8))

        # Draw center point
        self.canvas.create_oval(center_x-3, center_y-3, center_x+3, center_y+3, fill='black')

    def start_drag(self, event):
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
        if self.on_move:
            self.on_move(self.root.geometry())

    def report_angle_from_center(self, event):
        center_x = self.width / 2
        center_y = self.height / 2
        dx = event.x - center_x
        dy = center_y - event.y  # Invert y to match mathematical convention
        angle_rad = math.atan2(dy, dx)
        angle_deg = (math.degrees(angle_rad) + 360) % 360
        self.angle_label.config(text=f"Angle: {angle_deg:.2f}°")

class HorizontalScaleOverlay:
    def __init__(self, root, geometry=None, on_move=None):
        self.root = root
        self.root.title("Horizontal Scale Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
        self.width = 900
        self.height = 100
        self.on_move = on_move

        if geometry:
            self.root.geometry(geometry)
        else:
            self.root.geometry(f"{self.width}x{self.height}+1000+500")

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.draw_scale()
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.drag_start_x = 0
        self.drag_start_y = 0

    def draw_scale(self):
        center_x = self.width // 2
        y = self.height // 2
        scale_length = self.width * 0.8
        start_x = center_x - scale_length // 2
        end_x = center_x + scale_length // 2

        # Draw main horizontal line
        self.canvas.create_line(start_x, y, end_x, y, width=2)

        num_main_scales = 10
        num_sub_scales = 5
        main_scale_spacing = scale_length / num_main_scales

        # Draw scales
        for i in range(num_main_scales + 1):
            x = start_x + i * main_scale_spacing
            # Main scale (longer line)
            self.canvas.create_line(x, y - 20, x, y + 20, width=2)
            # Label
            label = str(i - num_main_scales // 2)
            self.canvas.create_text(x, y + 30, text=label, font=('Arial', 10, 'bold'))

            # Draw sub-scales (skip last main scale)
            if i < num_main_scales:
                for j in range(1, num_sub_scales):
                    sub_x = x + j * (main_scale_spacing / num_sub_scales)
                    self.canvas.create_line(sub_x, y - 10, sub_x, y + 10, width=1)

    def start_drag(self, event):
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
        if self.on_move:
            self.on_move(self.root.geometry())

class ScreenshotOverlay:
    def __init__(self, root, geometry=None):
        self.root = root
        self.root.title("Screenshot Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        self.width = 300
        self.height = 100

        if geometry:
            self.root.geometry(geometry)
        else:
            self.root.geometry(f"{self.width}x{self.height}+1200+700")

        self.button = tk.Button(self.root, text="Screenshot Area", command=self.screenshot_area, font=('Arial', 12))
        self.button.pack(expand=True, fill='both')
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.on_drag)
        self.drag_start_x = 0
        self.drag_start_y = 0

    def start_drag(self, event):
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def screenshot_area(self):
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = x + self.root.winfo_width()
        h = y + self.root.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, w, h))
        print((x, y, w, h))
        img.save("screenshot_overlay.png")

if __name__ == "__main__":
    positions = load_window_positions()
    # Protractor
    root = tk.Tk()
    def save_protractor_pos(geometry):
        positions['protractor'] = geometry
    protractor_app = ProtractorApp(root, geometry=positions.get('protractor'), on_move=save_protractor_pos)

    # Horizontal Scale
    scale_window = tk.Toplevel(root)
    def save_scale_pos(geometry):
        positions['scale'] = geometry
    scale_app = HorizontalScaleOverlay(scale_window, geometry=positions.get('scale'), on_move=save_scale_pos)

    # Slope Measure
    slope_measure_window = tk.Toplevel(root)
    def save_slope_pos(geometry):
        positions['slope'] = geometry
    slope_measure = ProtractorApp(slope_measure_window, True, geometry=positions.get('slope'), on_move=save_slope_pos)

    # Screenshot Overlay
    # screenshot_window = tk.Toplevel(root)
    # def save_screenshot_pos(geometry):
    #     positions['screenshot'] = geometry
    # screenshot_app = ScreenshotOverlay(screenshot_window, geometry=positions.get('screenshot'))

    def on_closing():
        positions['protractor'] = root.geometry()
        positions['scale'] = scale_window.geometry()
        positions['slope'] = slope_measure_window.geometry()
        #positions['screenshot'] = screenshot_window.geometry()
        save_window_positions(positions)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    scale_window.protocol("WM_DELETE_WINDOW", on_closing)
    slope_measure_window.protocol("WM_DELETE_WINDOW", on_closing)
    # screenshot_window.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()