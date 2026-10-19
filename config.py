"""Central configuration: grid size, terrain types, costs and the colour system."""

ROWS, COLS, CELL = 21, 31, 22          # odd sizes so the DFS maze generator fits neatly

# Terrain codes stored in the 2D grid (grid[row][col])
NORMAL, MUD, WATER, MOUNTAIN, WALL = 0, 1, 2, 3, 4

TERRAIN_NAMES = {NORMAL: "Normal", MUD: "Mud", WATER: "Water", MOUNTAIN: "Mountain", WALL: "Wall"}
TERRAIN_COST = {NORMAL: 1, MUD: 3, WATER: 5, MOUNTAIN: 10}   # cost of ENTERING a cell (walls: impassable)

# Colours (dark theme)
BG, PANEL, CARD, TEXT, MUTED, ACCENT = "#0f172a", "#111c33", "#1e293b", "#e2e8f0", "#94a3b8", "#6366f1"
TERRAIN_COLOR = {NORMAL: "#2b3648", MUD: "#8b5e3c", WATER: "#2f7fd1", MOUNTAIN: "#7d8590", WALL: "#05070d"}
START_COLOR, END_COLOR = "#22c55e", "#ef4444"
VISITED_COLOR, PATH_COLOR = "#38bdf8", "#fbbf24"   # explored cells / final path (gold-amber)
GRID_LINE = "#0f172a"

ALGORITHMS = ["BFS", "DFS", "Dijkstra"]
ALGO_INFO = {
    "BFS": ("BFS explores level-by-level using a Queue. It finds the shortest path "
            "when all movement costs are equal.", "Queue (FIFO) + visited set + parent map"),
    "DFS": ("DFS explores deeply using a Stack/recursion. It may find a path, but it "
            "does not guarantee the shortest path.", "Stack (LIFO) + visited set + parent map"),
    "Dijkstra": ("Dijkstra considers terrain costs and finds the minimum-cost path "
                 "using a Priority Queue/Min Heap.", "Min Heap (priority queue) + distance map + parent map"),
}
TOOL_INFO = {
    "Start/End": "Click a cell to set Start (S), click another to set End (E).",
    "Normal": "Normal — cost 1. The default ground.",
    "Mud": "Mud — cost 3. Slows movement.",
    "Water": "Water — cost 5. Very slow to cross.",
    "Mountain": "Mountain — cost 10. Extremely expensive; Dijkstra avoids it.",
    "Wall": "Wall — impassable. Blocks every algorithm.",
}
TOOL_TO_TERRAIN = {"Normal": NORMAL, "Mud": MUD, "Water": WATER, "Mountain": MOUNTAIN, "Wall": WALL}
