import tkinter as tk
import math
import json
import os
import sys

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
        self.is_slope = is_slope
        self.on_move = on_move

        if geometry:
            dims = geometry.split("+")[0]
            w_str, h_str = dims.split("x")
            self.width = int(w_str)
            self.height = int(h_str)
            self.root.geometry(geometry)
        else:
            self.width = 200
            self.height = 200
            self.root.geometry(f"{self.width}x{self.height}+2000+1000" if not is_slope else f"{self.width}x{self.height}+800+1000")

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height,
                              bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.draw_protractor()
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.drag_start_x = 0
        self.drag_start_y = 0

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

class HorizontalScaleOverlay:
    def __init__(self, root, geometry=None, on_move=None):
        self.root = root
        self.root.title("Horizontal Scale Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
        self.on_move = on_move

        if geometry:
            dims = geometry.split("+")[0]
            w_str, h_str = dims.split("x")
            self.width = int(w_str)
            self.height = int(h_str)
            self.root.geometry(geometry)
        else:
            self.width = 600
            self.height = 100
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

class ControlPanelApp:
    def __init__(self, master, windows):
        self.panel = tk.Toplevel(master)
        self.panel.title("Control Panel")
        self.panel.geometry("300x150")  #面板大小

        self.windows = windows
        self.entries = {}

        row = 0
        for name in ['protractor', 'scale', 'slope']:
            win = self.windows[name]
            win.update_idletasks()
            w = win.winfo_width()
            h = win.winfo_height()

            tk.Label(self.panel, text=f"{name.capitalize()} :").grid(row=row, column=0, sticky='e', padx=5, pady=2)

            # 輸入欄位
            tk.Label(self.panel, text="Width").grid(row=row, column=1, sticky='e')
            w_var = tk.StringVar(value=str(w))
            w_entry = tk.Entry(self.panel, textvariable=w_var, width=8)
            w_entry.grid(row=row, column=2, padx=2)

            tk.Label(self.panel, text="Height").grid(row=row, column=3, sticky='e')
            h_var = tk.StringVar(value=str(h))
            h_entry = tk.Entry(self.panel, textvariable=h_var, width=8)
            h_entry.grid(row=row, column=4, padx=2)

            self.entries[name] = {'width': w_var, 'height': h_var}
            row += 1

        # 按鈕
        tk.Button(self.panel, text="更新尺寸", command=self.apply_sizes).grid(row=row, column=2, columnspan=3, pady=10)

    def apply_sizes(self):
        new_positions = {}

        for name in self.windows:
            try:
                w = int(self.entries[name]['width'].get())
                h = int(self.entries[name]['height'].get())
                x = self.windows[name].winfo_x()
                y = self.windows[name].winfo_y()
                new_positions[name] = f"{w}x{h}+{x}+{y}"
            except ValueError:
                print(f"{name} 的輸入格式錯誤")
                return

        save_window_positions(new_positions)
        os.execl(sys.executable, sys.executable, *sys.argv)

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

    def on_closing():
        # Save current window positions
        positions['protractor'] = root.geometry()
        positions['scale'] = scale_window.geometry()
        positions['slope'] = slope_measure_window.geometry()
        save_window_positions(positions)
        root.destroy()

    ControlPanelApp(root, {'protractor': root,'scale': scale_window,'slope': slope_measure_window})
    root.protocol("WM_DELETE_WINDOW", on_closing)
    scale_window.protocol("WM_DELETE_WINDOW", on_closing)
    slope_measure_window.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()