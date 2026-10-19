"""Full interactive tutorial (multi-page). The 'Quick Start' card in the main window is the short version."""
import customtkinter as ctk
from config import *
from storage import save_settings

PAGES = [
    ("Welcome to MazeCraft", "A maze generator and pathfinding visualizer built for FODS.\n\nYou will see how Queue, Stack and Min-Heap data structures drive BFS, DFS and Dijkstra on a 2D grid."),
    ("1 · Generate a maze", "Press 'Generate Maze'. A maze is carved using DFS with backtracking (a Stack). Tick 'Animate generation' to watch it grow."),
    ("2 · Terrain", "Pick a brush in the Terrain menu: Mud (3), Water (5), Mountain (10) or Wall. Left-click/drag to paint, right-click to erase.\nCosts matter for Dijkstra."),
    ("3 · Start & End", "Choose the 'Start/End' tool. First click sets Start (green S), next click sets End (red E)."),
    ("4 · Solve", "Select BFS, DFS or Dijkstra and press SOLVE MAZE. Blue cells are explored, the gold line is the final path."),
    ("5 · Results & Compare", "The cards above the maze show nodes visited, path length, total cost and time. 'Compare Algorithms' runs all three side by side."),
]


def open_tutorial(parent, settings):
    win = ctk.CTkToplevel(parent)
    win.title("MazeCraft Tutorial")
    win.geometry("520x330")
    win.configure(fg_color=BG)
    win.transient(parent)
    idx = [0]
    title = ctk.CTkLabel(win, font=("Segoe UI", 20, "bold"), text_color=ACCENT)
    title.pack(pady=(20, 8))
    body = ctk.CTkLabel(win, font=("Segoe UI", 13), text_color=TEXT, wraplength=440, justify="left")
    body.pack(padx=30, pady=6, fill="x")
    show = ctk.BooleanVar(value=settings.get("show_tutorial", True))

    def toggled():
        settings["show_tutorial"] = show.get()
        save_settings(settings)

    ctk.CTkCheckBox(win, text="Show this tutorial on startup", variable=show, command=toggled).pack(side="bottom", pady=(0, 14))
    nav = ctk.CTkFrame(win, fg_color="transparent")
    nav.pack(side="bottom", pady=10)
    back = ctk.CTkButton(nav, text="◀ Back", width=90, command=lambda: go(-1))
    nxt = ctk.CTkButton(nav, text="Next ▶", width=90, command=lambda: go(1))
    back.pack(side="left", padx=6)
    nxt.pack(side="left", padx=6)

    def go(d):
        if idx[0] + d >= len(PAGES):
            win.destroy()
            return
        idx[0] = max(0, idx[0] + d)
        title.configure(text=PAGES[idx[0]][0])
        body.configure(text=PAGES[idx[0]][1])
        back.configure(state="normal" if idx[0] else "disabled")
        nxt.configure(text="Close ✓" if idx[0] == len(PAGES) - 1 else "Next ▶")

    go(0)
    win.after(100, win.lift)
    return win
