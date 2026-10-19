"""Compare screen: runs BFS, DFS and Dijkstra on the CURRENT maze and shows real measured results."""
import customtkinter as ctk
from config import *
from algorithms import SOLVERS


def open_compare(parent, grid, start, end):
    results = [SOLVERS[n](grid, start, end) for n in ALGORITHMS]   # real execution, nothing hardcoded
    win = ctk.CTkToplevel(parent)
    win.title("Compare Algorithms")
    win.configure(fg_color=BG)
    win.transient(parent)
    ctk.CTkLabel(win, text="Algorithm Comparison (same maze, same Start/End)", font=("Segoe UI", 16, "bold"),
                 text_color=TEXT).pack(padx=20, pady=(16, 8))
    table = ctk.CTkFrame(win, fg_color=CARD, corner_radius=10)
    table.pack(padx=20, pady=6)
    heads = ["Algorithm", "Data structure", "Nodes Visited", "Path Length", "Total Cost", "Time"]
    for c, h in enumerate(heads):
        ctk.CTkLabel(table, text=h, font=("Segoe UI", 12, "bold"), text_color=MUTED).grid(row=0, column=c, padx=14, pady=8)
    ds_name = {"BFS": "Queue", "DFS": "Stack", "Dijkstra": "Min Heap"}
    ok = [r for r in results if r["found"]]
    best = {k: min(r[k] for r in ok) for k in ("nodes", "path_length", "cost", "time_ms")} if ok else {}
    for i, r in enumerate(results, start=1):
        vals = [r["name"], ds_name[r["name"]]]
        vals += [str(r["nodes"]), str(r["path_length"]), str(r["cost"]), f"{r['time_ms']:.2f} ms"] if r["found"] else ["No path", "—", "—", "—"]
        for c, v in enumerate(vals):
            key = {2: "nodes", 3: "path_length", 4: "cost", 5: "time_ms"}.get(c)
            good = r["found"] and key and r[key] == best[key]      # highlight the best value per column
            ctk.CTkLabel(table, text=v, font=("Segoe UI", 13, "bold" if c == 0 or good else "normal"),
                         text_color="#4ade80" if good else TEXT).grid(row=i, column=c, padx=14, pady=6)
    note = ("Green = best in that column. Notice: BFS and Dijkstra find the shortest path by steps; "
            "only Dijkstra guarantees the lowest COST on weighted terrain; DFS may take a long detour.")
    ctk.CTkLabel(win, text=note if ok else "No path exists between Start and End.", wraplength=620,
                 font=("Segoe UI", 11), text_color=MUTED, justify="left").pack(padx=20, pady=(6, 16))
    win.after(100, win.lift)
