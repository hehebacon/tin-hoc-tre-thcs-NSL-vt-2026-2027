import tkinter as tk
from tkinter import ttk

from config import MAP_W, MAP_H, CELL, OBSTACLES, BASE, ROBOT_START, VICTIM
from core import RescueCore
from sensors import SensorSimulator, PublicDataSimulator


class App:
    def __init__(self, root):
        self.root = root
        root.title("RESCUE ROBOT OS - Simulator V1")
        root.resizable(False, False)

        self.core = RescueCore(MAP_W, MAP_H, OBSTACLES, BASE, VICTIM)
        self.core.robot = ROBOT_START
        self.sensors = SensorSimulator(VICTIM)
        self.public = PublicDataSimulator()

        self.canvas = tk.Canvas(
            root, width=MAP_W * CELL, height=MAP_H * CELL,
            bg="#11151a", highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        side = ttk.Frame(root, padding=10)
        side.grid(row=0, column=1, sticky="n")
        ttk.Label(side, text="ROBOT OS", font=("TkDefaultFont", 16, "bold")).pack(pady=(0, 10))

        for mode in self.core.MODES:
            ttk.Button(side, text=mode, command=lambda m=mode: self.set_mode(m)).pack(fill="x", pady=2)

        ttk.Separator(side).pack(fill="x", pady=10)
        ttk.Button(side, text="RESET", command=self.reset).pack(fill="x", pady=2)

        self.status = tk.StringVar()
        ttk.Label(side, textvariable=self.status, justify="left").pack(anchor="w", pady=8)

        self.logbox = tk.Listbox(root, width=52, height=9)
        self.logbox.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="n")
        self.root.after(250, self.loop)

    def set_mode(self, mode):
        self.core.set_mode(mode)
        self.refresh()

    def reset(self):
        self.core.reset()
        self.refresh()

    def draw(self):
        c = self.canvas
        c.delete("all")

        for y in range(MAP_H):
            for x in range(MAP_W):
                x1, y1 = x * CELL, y * CELL
                x2, y2 = x1 + CELL, y1 + CELL
                fill = "#1b2229" if (x, y) not in OBSTACLES else "#4a4f55"
                c.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#252c33")

        bx, by = BASE
        c.create_oval(bx*CELL+8, by*CELL+8, bx*CELL+24, by*CELL+24, fill="#55aaff", outline="")
        c.create_text(bx*CELL+16, by*CELL+25, text="BASE", fill="white", font=("TkDefaultFont", 7))

        vx, vy = VICTIM
        c.create_oval(vx*CELL+7, vy*CELL+7, vx*CELL+25, vy*CELL+25, fill="#ff6b6b", outline="")
        c.create_text(vx*CELL+16, vy*CELL+25, text="PERSON", fill="white", font=("TkDefaultFont", 7))

        if len(self.core.path) > 1:
            points = []
            for x, y in self.core.path:
                points.extend([x*CELL+CELL/2, y*CELL+CELL/2])
            c.create_line(*points, fill="#ffd166", width=3)

        rx, ry = self.core.robot
        c.create_rectangle(rx*CELL+6, ry*CELL+6, rx*CELL+26, ry*CELL+26, fill="#7cf29a", outline="")
        c.create_text(rx*CELL+16, ry*CELL+16, text="R", fill="#07120a", font=("TkDefaultFont", 10, "bold"))

    def refresh(self):
        sensor = self.sensors.snapshot()
        public = self.public.snapshot()
        self.status.set(
            f"MODE: {self.core.mode}\n"
            f"ROBOT: {self.core.robot}\n"
            f"PERSON: {'DETECTED' if sensor['person_visible'] else 'NOT DETECTED'}\n"
            f"THERMAL: {sensor['thermal']:.2f}\n"
            f"TEMP: {sensor['temperature']:.1f} C\n"
            f"HUMIDITY: {sensor['humidity']:.1f}%\n"
            f"PRESSURE: {sensor['pressure']:.1f} hPa\n"
            f"ENV: {sensor['environment']}\n"
            f"PUBLIC: {public['alert']}"
        )
        self.logbox.delete(0, tk.END)
        for line in self.core.log[:10]:
            self.logbox.insert(tk.END, line)
        self.draw()

    def loop(self):
        self.sensors.update(self.core.robot)
        if self.core.mode in ("RESCUE", "AUTONOMOUS") and self.sensors.person_visible and self.core.robot == VICTIM:
            self.core.report_found()
        self.core.step()
        self.refresh()
        self.root.after(500, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
