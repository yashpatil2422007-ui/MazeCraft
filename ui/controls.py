"""Small reusable widgets: section headers, Quick Start card, legend, stat cards."""
import customtkinter as ctk
from config import *


def section(parent, title):
    """A titled card in the sidebar; returns the frame to put widgets in."""
    box = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=10)
    box.pack(fill="x", padx=6, pady=5)
    ctk.CTkLabel(box, text=title, font=("Segoe UI", 12, "bold"), text_color=MUTED).pack(anchor="w", padx=12, pady=(8, 2))
    return box


def quick_start(parent):
    box = section(parent, "HOW TO USE")
    steps = [("①", "Generate a Maze", "Press Generate Maze."),
             ("②", "Set Start & End", "Click a cell = Start (S), next click = End (E)."),
             ("③", "Choose Algorithm", "Select BFS, DFS or Dijkstra."),
             ("④", "Solve", "Click Solve Maze and watch it search."),
             ("⑤", "View Results", "Nodes, path length, cost, time.")]
    for n, head, sub in steps:
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=1)
        ctk.CTkLabel(row, text=n, font=("Segoe UI", 16, "bold"), text_color=ACCENT, width=22).pack(side="left", anchor="n")
        col = ctk.CTkFrame(row, fg_color="transparent")
        col.pack(side="left", fill="x")
        ctk.CTkLabel(col, text=head, font=("Segoe UI", 12, "bold"), text_color=TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(col, text=sub, font=("Segoe UI", 10), text_color=MUTED, anchor="w", wraplength=230, justify="left").pack(anchor="w")
    ctk.CTkFrame(box, height=6, fg_color="transparent").pack()


class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent, fg_color=CARD, corner_radius=10)
        ctk.CTkLabel(self, text=title, font=("Segoe UI", 10), text_color=MUTED).pack(pady=(6, 0))
        self.value = ctk.CTkLabel(self, text="—", font=("Segoe UI", 20, "bold"), text_color=TEXT)
        self.value.pack(pady=(0, 6))

    def set(self, text):
        self.value.configure(text=text)


def legend(parent):
    """Colours come straight from config.py so the legend always matches the grid."""
    box = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=10)
    items = [("S", START_COLOR, "Start"), ("E", END_COLOR, "End"), ("■", TERRAIN_COLOR[WALL], "Wall"),
             ("", TERRAIN_COLOR[NORMAL], "Normal · cost 1"), ("", TERRAIN_COLOR[MUD], "Mud · cost 3"),
             ("", TERRAIN_COLOR[WATER], "Water · cost 5"), ("", TERRAIN_COLOR[MOUNTAIN], "Mountain · cost 10"),
             ("", VISITED_COLOR, "Visited (explored)"), ("", PATH_COLOR, "Final path (gold)")]
    for i, (sym, color, label) in enumerate(items):
        cell = ctk.CTkFrame(box, fg_color="transparent")
        cell.grid(row=i // 5, column=i % 5, sticky="w", padx=8, pady=3)
        ctk.CTkLabel(cell, text=sym, width=18, height=18, fg_color=color, corner_radius=4,
                     text_color="white", font=("Segoe UI", 10, "bold")).pack(side="left")
        ctk.CTkLabel(cell, text=label, font=("Segoe UI", 10), text_color=TEXT).pack(side="left", padx=4)
    return box
