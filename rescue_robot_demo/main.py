import tkinter as tk
from tkinter import ttk

from config import MAP_W, MAP_H, CELL, OBSTACLES, BASE, ROBOT_START, VICTIM
from core import RescueCore
from sensors import SensorSimulator, PublicDataSimulator


TICK_MS = 50
DT = TICK_MS / 1000.0


class App:
    def __init__(self, root):
        self.root = root
        root.title("RESCUE ROBOT OS - Simulator V3")
        root.resizable(False, False)

        self.core = RescueCore(MAP_W, MAP_H, OBSTACLES, BASE, VICTIM)
        self.core.robot = ROBOT_START
        self.sensors = SensorSimulator(VICTIM)
        self.public = PublicDataSimulator()

        self.canvas = tk.Canvas(
            root,
            width=MAP_W * CELL,
            height=MAP_H * CELL,
            bg="#11151a",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        side = ttk.Frame(root, padding=10)
        side.grid(row=0, column=1, sticky="n")

        ttk.Label(
            side,
            text="ROBOT OS",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(pady=(0, 10))

        for mode in self.core.MODES:
            ttk.Button(
                side,
                text=mode,
                command=lambda m=mode: self.set_mode(m),
            ).pack(fill="x", pady=2)

        ttk.Separator(side).pack(fill="x", pady=10)

        ttk.Button(side, text="RESET", command=self.reset).pack(fill="x", pady=2)
        ttk.Button(side, text="E-STOP", command=self.estop).pack(fill="x", pady=2)
        ttk.Button(side, text="RESUME", command=self.resume).pack(fill="x", pady=2)

        self.status = tk.StringVar()
        ttk.Label(side, textvariable=self.status, justify="left").pack(
            anchor="w", pady=8
        )

        self.leg_status = tk.StringVar()
        ttk.Label(
            side,
            textvariable=self.leg_status,
            justify="left",
            font=("TkFixedFont", 9),
        ).pack(anchor="w", pady=4)

        self.ik_status = tk.StringVar()
        ttk.Label(
            side,
            textvariable=self.ik_status,
            justify="left",
            font=("TkFixedFont", 8),
        ).pack(anchor="w", pady=4)

        self.logbox = tk.Listbox(root, width=52, height=9)
        self.logbox.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="n")

        self.root.after(TICK_MS, self.loop)

    def set_mode(self, mode):
        self.core.set_mode(mode)
        self.refresh()

    def reset(self):
        self.core.reset()
        self.refresh()

    def estop(self):
        self.core.stop()
        self.refresh()

    def resume(self):
        self.core.resume()
        self.refresh()

    def draw_robot(self):
        rx, ry = self.core.robot
        cx = rx * CELL + CELL / 2
        cy = ry * CELL + CELL / 2

        self.canvas.create_rectangle(
            cx - 10, cy - 8, cx + 10, cy + 8,
            fill="#7cf29a", outline=""
        )
        self.canvas.create_text(
            cx, cy, text="R", fill="#07120a",
            font=("TkDefaultFont", 10, "bold")
        )

        # Visualize the four gait states around the body.
        positions = {
            "FL": (-11, -10),
            "FR": (11, -10),
            "RL": (-11, 10),
            "RR": (11, 10),
        }

        for leg, (ox, oy) in positions.items():
            target = self.core.last_leg_targets[leg]
            lift = max(0.0, target.z - self.core.gait.body_height)
            length = 6 + min(9, abs(target.x) / 4)
            x1 = cx + ox
            y1 = cy + oy
            x2 = x1 + (length if target.x >= 0 else -length)
            y2 = y1 + (-lift / 2)

            self.canvas.create_line(x1, y1, x2, y2, fill="#8fd3ff", width=3)
            self.canvas.create_oval(
                x2 - 3, y2 - 3, x2 + 3, y2 + 3,
                fill="#8fd3ff", outline=""
            )
            self.canvas.create_text(
                x2, y2 - 9, text=leg,
                fill="white", font=("TkDefaultFont", 6, "bold")
            )

    def draw(self):
        c = self.canvas
        c.delete("all")

        for y in range(MAP_H):
            for x in range(MAP_W):
                x1, y1 = x * CELL, y * CELL
                x2, y2 = x1 + CELL, y1 + CELL
                fill = "#1b2229" if (x, y) not in OBSTACLES else "#4a4f55"
                c.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill, outline="#252c33"
                )

        bx, by = BASE
        c.create_oval(
            bx * CELL + 8, by * CELL + 8,
            bx * CELL + 24, by * CELL + 24,
            fill="#55aaff", outline=""
        )
        c.create_text(
            bx * CELL + 16, by * CELL + 25,
            text="BASE", fill="white",
            font=("TkDefaultFont", 7)
        )

        vx, vy = VICTIM
        c.create_oval(
            vx * CELL + 7, vy * CELL + 7,
            vx * CELL + 25, vy * CELL + 25,
            fill="#ff6b6b", outline=""
        )
        c.create_text(
            vx * CELL + 16, vy * CELL + 25,
            text="PERSON", fill="white",
            font=("TkDefaultFont", 7)
        )

        if len(self.core.path) > 1:
            points = []
            for x, y in self.core.path:
                points.extend([
                    x * CELL + CELL / 2,
                    y * CELL + CELL / 2,
                ])
            c.create_line(*points, fill="#ffd166", width=3)

        self.draw_robot()

    def refresh(self):
        sensor = self.sensors.snapshot()
        public = self.public.snapshot()
        terrain = self.core.terrain_at()

        self.status.set(
            f"MODE: {self.core.mode}\n"
            f"ROBOT: {self.core.robot}\n"
            f"PERSON: {'DETECTED' if sensor['person_visible'] else 'NOT DETECTED'}\n"
            f"THERMAL: {sensor['thermal']:.2f}\n"
            f"TEMP: {sensor['temperature']:.1f} C\n"
            f"HUMIDITY: {sensor['humidity']:.1f}%\n"
            f"PRESSURE: {sensor['pressure']:.1f} hPa\n"
            f"ENV: {sensor['environment']}\n"
            f"TERRAIN: {terrain['type']} {terrain['slope_deg']:.1f} deg\n"
            f"GAIT: {self.core.gait.move_name}\n"
            f"PUBLIC: {public['alert']}"
        )

        leg_lines = ["LEGS"]
        for leg in ("FL", "FR", "RL", "RR"):
            state = self.core.last_leg_targets[leg]
            leg_lines.append(
                f"{leg}: {state.phase:<6} "
                f"x={state.x:>6.1f} z={state.z:>6.1f}"
            )
        self.leg_status.set("\n".join(leg_lines))

        self.logbox.delete(0, tk.END)
        for line in self.core.log[:10]:
            self.logbox.insert(tk.END, line)

        self.draw()

    def loop(self):
        self.sensors.update(self.core.robot)

        if (
            self.core.mode in ("RESCUE", "AUTONOMOUS")
            and self.sensors.person_visible
            and self.core.robot == VICTIM
        ):
            self.core.report_found()

        self.core.step(DT)
        self.refresh()
        self.root.after(TICK_MS, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
