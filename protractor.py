import tkinter as tk
import math

class ProtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Protractor Overlay")
        
        # Make window always on top and transparent
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
        
        # Set window size and position
        self.width = 200
        self.height = 200
        self.root.geometry(f"{self.width}x{self.height}+2000+1000")
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, 
                              bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Draw protractor
        self.draw_protractor()
        
        # Make window draggable
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
            self.canvas.create_text(label_x, label_y, text=str(angle), font=('Arial', 8))
        
        # Draw center point
        self.canvas.create_oval(center_x-3, center_y-3, center_x+3, center_y+3, fill='black')
        
    def start_drag(self, event):
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()
        
    def on_drag(self, event):
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")


class HorizontalScaleOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Horizontal Scale Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
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


if __name__ == "__main__":
    root = tk.Tk()
    protractor_app = ProtractorApp(root)
    scale_window = tk.Toplevel(root)
    scale_app = HorizontalScaleOverlay(scale_window)
    root.mainloop()