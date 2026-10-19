"""Main window: layout, canvas drawing, mouse painting, generation/solve animation, status bar."""
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from config import *
from maze import empty_grid, generate_maze_steps, finish_maze
from algorithms import SOLVERS
from storage import save_maze, load_maze, load_settings
from ui.controls import section, quick_start, StatCard, legend
from ui.tutorial import open_tutorial
from ui.compare import open_compare


def blend(c1, c2, t):
    """Mix two #rrggbb colours (t=0 -> c1, t=1 -> c2). Lets 'visited' cells still show their terrain."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


class MazeCraftApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("MazeCraft — Maze Generator & Algorithm Visualizer")
        self.geometry("1140x850")
        self.minsize(1040, 780)
        self.configure(fg_color=BG)
        self.settings = load_settings()
        self.grid_data = empty_grid()           # 2D array of terrain codes
        self.start = self.end = None
        self.visited, self.path = set(), set()  # overlay cells drawn on top of terrain
        self.job = None                         # pending after() id (animation)
        self.next_is_start = True
        self.tool, self.algo = tk.StringVar(value="Start/End"), tk.StringVar(value="BFS")
        self._build_ui()
        self.refresh_all()
        self.set_status("Ready — Generate a maze to begin.")
        if self.settings.get("show_tutorial", True):
            self.after(400, lambda: open_tutorial(self, self.settings))

    # ---------------------------------------------------------------- UI layout
    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(10, 2))
        ctk.CTkLabel(top, text="MazeCraft", font=("Segoe UI", 26, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(top, text="   Generate → Set Start/End → Choose algorithm → Solve → Compare results",
                     font=("Segoe UI", 12), text_color=MUTED).pack(side="left", pady=(8, 0))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=10)
        side = ctk.CTkScrollableFrame(body, width=290, fg_color=PANEL, corner_radius=12)
        side.pack(side="left", fill="y", padx=(0, 10), pady=4)
        main = ctk.CTkFrame(body, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True, pady=4)

        quick_start(side)                                                  # 1. Quick Start
        box = section(side, "MAZE CONFIGURATION")                          # 2.
        self.animate_gen = ctk.BooleanVar(value=True)
        self.use_terrain = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(box, text="Animate generation", variable=self.animate_gen).pack(anchor="w", padx=12, pady=2)
        ctk.CTkCheckBox(box, text="Add random terrain", variable=self.use_terrain).pack(anchor="w", padx=12, pady=2)
        ctk.CTkButton(box, text="Generate Maze", height=34, fg_color="#334155", hover_color="#475569",
                      command=self.generate).pack(fill="x", padx=12, pady=(6, 10))

        box = section(side, "TERRAIN  (left-click paint · right-click erase)")   # 3.
        ctk.CTkOptionMenu(box, values=list(TOOL_INFO), variable=self.tool, command=self.on_tool).pack(fill="x", padx=12, pady=4)
        self.tool_label = ctk.CTkLabel(box, text=TOOL_INFO["Start/End"], wraplength=250, justify="left",
                                       font=("Segoe UI", 11), text_color=MUTED)
        self.tool_label.pack(anchor="w", padx=12, pady=(0, 10))

        box = section(side, "PATHFINDER")                                  # 4.
        ctk.CTkSegmentedButton(box, values=ALGORITHMS, variable=self.algo, command=self.on_algo).pack(fill="x", padx=12, pady=4)
        self.algo_label = ctk.CTkLabel(box, wraplength=250, justify="left", font=("Segoe UI", 11), text_color=TEXT)
        self.algo_label.pack(anchor="w", padx=12, pady=(2, 0))
        self.ds_label = ctk.CTkLabel(box, wraplength=250, justify="left", font=("Segoe UI", 10, "italic"), text_color=PATH_COLOR)
        self.ds_label.pack(anchor="w", padx=12, pady=(2, 4))
        ctk.CTkLabel(box, text="Animation delay (ms)", font=("Segoe UI", 10), text_color=MUTED).pack(anchor="w", padx=12)
        self.delay = ctk.CTkSlider(box, from_=1, to=80, number_of_steps=79)
        self.delay.set(12)
        self.delay.pack(fill="x", padx=12, pady=(0, 6))
        ctk.CTkButton(box, text="▶  SOLVE MAZE", height=46, font=("Segoe UI", 16, "bold"),
                      fg_color=ACCENT, hover_color="#4f46e5", command=self.solve).pack(fill="x", padx=12, pady=(2, 12))
        self.on_algo(self.algo.get(), announce=False)

        box = section(side, "ACTIONS")                                     # 5.
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(2, 10))
        ctk.CTkButton(row, text="Reset Path", width=110, fg_color="#334155", hover_color="#475569",
                      command=self.reset_path).pack(side="left", expand=True, padx=(0, 3))
        ctk.CTkButton(row, text="Clear All", width=110, fg_color="#334155", hover_color="#475569",
                      command=self.clear_all).pack(side="left", expand=True, padx=(3, 0))

        box = section(side, "SAVE / LOAD & ANALYTICS")                     # 6.
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(2, 4))
        ctk.CTkButton(row, text="Save .mz", width=110, command=self.save).pack(side="left", expand=True, padx=(0, 3))
        ctk.CTkButton(row, text="Load .mz", width=110, command=self.load).pack(side="left", expand=True, padx=(3, 0))
        ctk.CTkButton(box, text="Compare Algorithms", command=self.compare).pack(fill="x", padx=12, pady=3)
        ctk.CTkButton(box, text="Tutorial", fg_color="#334155", hover_color="#475569",
                      command=lambda: open_tutorial(self, self.settings)).pack(fill="x", padx=12, pady=(3, 10))

        # right side: stat cards, maze, legend, DSA strip
        cards = ctk.CTkFrame(main, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 6))
        self.cards = {k: StatCard(cards, t) for k, t in
                      [("nodes", "Nodes Visited"), ("len", "Path Length"), ("cost", "Total Cost"), ("time", "Time Elapsed")]}
        for c in self.cards.values():
            c.pack(side="left", expand=True, fill="x", padx=3)
        self.canvas = tk.Canvas(main, width=COLS * CELL, height=ROWS * CELL, bg=BG, highlightthickness=0)
        self.canvas.pack(pady=4)
        self.cell_ids = [[self.canvas.create_rectangle(c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL,
                                                       outline=GRID_LINE) for c in range(COLS)] for r in range(ROWS)]
        self.marker_ids = []
        for seq in ("<Button-1>", "<B1-Motion>"):
            self.canvas.bind(seq, lambda e, s=seq: self.on_paint(e, erase=False, drag=(s == "<B1-Motion>")))
        for seq in ("<Button-3>", "<B3-Motion>", "<Button-2>"):
            self.canvas.bind(seq, lambda e: self.on_paint(e, erase=True, drag=True))
        legend(main).pack(pady=4)
        ctk.CTkLabel(main, text="DSA used:  2D Grid (array) • Graph (4-neighbour adjacency) • Queue • Stack • Min Heap • "
                                "Visited set • Parent map • DFS maze generation + backtracking • Path reconstruction",
                     font=("Segoe UI", 10), text_color=MUTED, wraplength=700).pack(pady=(2, 0))

        self.status = ctk.CTkLabel(self, text="", anchor="w", font=("Segoe UI", 14, "bold"), text_color=TEXT,
                                   fg_color=CARD, corner_radius=8, height=36)
        self.status.pack(fill="x", padx=12, pady=(4, 10))

    # ---------------------------------------------------------------- helpers
    def set_status(self, text):
        self.status.configure(text="  " + text)

    def cancel_animation(self):
        if self.job:
            self.after_cancel(self.job)
            self.job = None

    def clear_stats(self):
        for c in self.cards.values():
            c.set("—")

    def cell_color(self, r, c):
        if (r, c) == self.start: return START_COLOR
        if (r, c) == self.end: return END_COLOR
        base = TERRAIN_COLOR[self.grid_data[r][c]]
        if (r, c) in self.path: return PATH_COLOR
        if (r, c) in self.visited: return blend(base, VISITED_COLOR, 0.65)
        return base

    def refresh_cell(self, r, c):
        self.canvas.itemconfig(self.cell_ids[r][c], fill=self.cell_color(r, c))

    def refresh_all(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.refresh_cell(r, c)
        for m in self.marker_ids:
            self.canvas.delete(m)
        self.marker_ids = []
        for cell, label in ((self.start, "S"), (self.end, "E")):
            if cell:
                r, c = cell
                self.marker_ids.append(self.canvas.create_text(c * CELL + CELL // 2, r * CELL + CELL // 2, text=label,
                                                               fill="white", font=("Segoe UI", 11, "bold")))

    # ---------------------------------------------------------------- toolbar callbacks
    def on_tool(self, tool):
        self.tool_label.configure(text=TOOL_INFO[tool])
        if tool == "Start/End":
            self.next_is_start = True

    def on_algo(self, name, announce=True):
        info, ds = ALGO_INFO[name]
        self.algo_label.configure(text=info)
        self.ds_label.configure(text="Data structure: " + ds)
        if announce:
            self.set_status(f"{name} selected — Click Solve Maze to start.")

    # ---------------------------------------------------------------- painting
    def on_paint(self, event, erase, drag):
        r, c = event.y // CELL, event.x // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return
        cell, tool = (r, c), self.tool.get()
        if not erase and tool == "Start/End":
            if drag or self.grid_data[r][c] == WALL:
                return
            if self.next_is_start:
                if cell == self.end: return
                self.start = cell
                self.set_status("Start set — now click a cell for End (E).")
            else:
                if cell == self.start: return
                self.end = cell
                self.set_status("Start and End set — Choose an algorithm, then click Solve Maze.")
            self.next_is_start = not self.next_is_start
        else:
            if cell in (self.start, self.end):
                return                                    # never paint over S / E
            self.grid_data[r][c] = NORMAL if erase else TOOL_TO_TERRAIN.get(tool, NORMAL)
        self.cancel_animation()
        if self.visited or self.path:                     # editing invalidates the old result
            self.visited, self.path = set(), set()
            self.clear_stats()
            self.refresh_all()
        else:
            self.refresh_cell(r, c)
            self.refresh_all() if tool == "Start/End" else None

    # ---------------------------------------------------------------- generate / reset / clear
    def generate(self):
        self.cancel_animation()
        self.visited, self.path, self.start, self.end = set(), set(), None, None
        self.clear_stats()
        steps = generate_maze_steps(self.grid_data)
        self.set_status("Generating maze with DFS + backtracking...")

        def finish():
            self.start, self.end = finish_maze(self.grid_data, self.use_terrain.get())
            self.next_is_start = True
            self.refresh_all()
            self.set_status("Maze generated — Set Start and End points (or keep the defaults S and E).")

        if not self.animate_gen.get():
            for _ in steps: pass
            finish()
            return
        for r in range(ROWS):                             # show the all-wall starting grid
            for c in range(COLS):
                self.canvas.itemconfig(self.cell_ids[r][c], fill=TERRAIN_COLOR[WALL])
        for m in self.marker_ids: self.canvas.delete(m)
        self.marker_ids = []

        def tick():
            for _ in range(6):                            # a few carves per frame keeps it smooth
                try:
                    r, c = next(steps)
                except StopIteration:
                    self.job = None
                    finish()
                    return
                self.canvas.itemconfig(self.cell_ids[r][c], fill=TERRAIN_COLOR[NORMAL])
            self.job = self.after(8, tick)
        tick()

    def reset_path(self):
        self.cancel_animation()
        self.visited, self.path = set(), set()
        self.clear_stats()
        self.refresh_all()
        self.set_status("Path cleared — choose an algorithm and click Solve Maze.")

    def clear_all(self):
        self.cancel_animation()
        self.grid_data = empty_grid()
        self.start, self.end = (1, 1), (ROWS - 2, COLS - 2)
        self.visited, self.path = set(), set()
        self.next_is_start = True
        self.clear_stats()
        self.refresh_all()
        self.set_status("Cleared — paint walls/terrain, or press Generate Maze.")

    # ---------------------------------------------------------------- solving
    def solve(self):
        if not self.start or not self.end:
            self.set_status("⚠ Set Start and End first (use the Start/End tool, or Generate Maze).")
            return
        self.cancel_animation()
        name = self.algo.get()
        self.visited, self.path = set(), set()
        self.refresh_all()
        result = SOLVERS[name](self.grid_data, self.start, self.end)     # real algorithm run
        self.set_status(f"🔵 {name} is exploring the maze...")
        for k in ("len", "cost", "time"):
            self.cards[k].set("…")
        order, path, i = result["visited_order"], result["path"], [0]

        def explore():                                    # replay the visiting order as an animation
            if i[0] < len(order):
                cell = order[i[0]]
                i[0] += 1
                self.visited.add(cell)
                self.refresh_cell(*cell)
                self.cards["nodes"].set(str(i[0]))
                self.job = self.after(int(self.delay.get()), explore)
            else:
                self.cards["nodes"].set(str(result["nodes"]))
                self.job = self.after(150, draw_path, 0) if result["found"] else self.after(150, finish)

        def draw_path(j):                                 # then draw the reconstructed path in gold
            if j < len(path):
                self.path.add(path[j])
                self.refresh_cell(*path[j])
                self.job = self.after(25, draw_path, j + 1)
            else:
                finish()

        def finish():
            self.job = None
            self.refresh_all()
            self.cards["nodes"].set(str(result["nodes"]))
            self.cards["time"].set(f"{result['time_ms']:.2f} ms")
            if result["found"]:
                self.cards["len"].set(str(result["path_length"]))
                self.cards["cost"].set(str(result["cost"]))
                self.set_status(f"🟢 Path found! {name} completed successfully.")
            else:
                self.cards["len"].set("—")
                self.cards["cost"].set("—")
                self.set_status("🔴 No path found between Start and End.")
        explore()

    # ---------------------------------------------------------------- save / load / compare
    def save(self):
        p = filedialog.asksaveasfilename(defaultextension=".mz", filetypes=[("MazeCraft maze", "*.mz")])
        if p:
            save_maze(p, self.grid_data, self.start, self.end)
            self.set_status("💾 Maze saved.")

    def load(self):
        p = filedialog.askopenfilename(filetypes=[("MazeCraft maze", "*.mz")])
        if not p:
            return
        try:
            grid, s, e = load_maze(p)
        except ValueError as ex:
            messagebox.showerror("Load failed", str(ex))
            return
        if len(grid) != ROWS or len(grid[0]) != COLS:
            messagebox.showerror("Load failed", f"Maze must be {ROWS}x{COLS}.")
            return
        self.cancel_animation()
        self.grid_data, self.start, self.end = grid, s, e
        self.visited, self.path = set(), set()
        self.clear_stats()
        self.refresh_all()
        self.set_status("📂 Maze loaded — choose an algorithm and click Solve Maze.")

    def compare(self):
        if not self.start or not self.end:
            self.set_status("⚠ Set Start and End first, then compare.")
            return
        open_compare(self, self.grid_data, self.start, self.end)
