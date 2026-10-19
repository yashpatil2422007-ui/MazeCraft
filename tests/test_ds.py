"""Run:  python tests/test_ds.py"""
import os, sys, random, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *
from ds import Queue, Stack, MinHeap
from maze import empty_grid, generate_maze_steps, finish_maze
from algorithms import bfs, dfs, dijkstra
from storage import save_maze, load_maze


def test_queue_stack_heap():
    q = Queue(); [q.enqueue(i) for i in (1, 2, 3)]
    assert [q.dequeue() for _ in range(3)] == [1, 2, 3] and q.is_empty()
    s = Stack(); [s.push(i) for i in (1, 2, 3)]
    assert s.peek() == 3 and [s.pop() for _ in range(3)] == [3, 2, 1] and s.is_empty()
    h = MinHeap(); vals = [random.randint(0, 50) for _ in range(200)]
    for v in vals: h.push(v, v)
    assert [h.pop()[0] for _ in vals] == sorted(vals)


def make(seed, terrain=True):
    rng = random.Random(seed)
    g = empty_grid()
    for _ in generate_maze_steps(g, rng): pass
    s, e = finish_maze(g, terrain, rng)
    return g, s, e


def test_maze_solvable_and_algorithms():
    for seed in range(20):
        g, s, e = make(seed, terrain=False)
        b, d, k = bfs(g, s, e), dfs(g, s, e), dijkstra(g, s, e)
        assert b["found"] and d["found"] and k["found"]              # generated mazes are connected
        assert b["path_length"] == k["path_length"] <= d["path_length"]   # BFS shortest when costs equal
        assert b["cost"] == b["path_length"]
        g, s, e = make(seed)
        assert dijkstra(g, s, e)["cost"] <= bfs(g, s, e)["cost"]     # Dijkstra = min cost with weights
        assert dijkstra(g, s, e)["cost"] <= dfs(g, s, e)["cost"]


def test_no_path_and_same_cell():
    g = empty_grid(); s, e = (1, 1), (5, 5)
    for r in range(len(g)): g[r][3] = WALL                            # full wall barrier
    for f in (bfs, dfs, dijkstra):
        assert not f(g, s, e)["found"] and f(g, s, e)["path"] == []
        assert f(g, s, s)["found"] and f(g, s, s)["path_length"] == 0


def test_save_load():
    g, s, e = make(1)
    p = os.path.join(tempfile.mkdtemp(), "t.mz")
    save_maze(p, g, s, e)
    assert load_maze(p) == (g, s, e)
    open(p, "w").write("garbage")
    try: load_maze(p); assert False
    except ValueError: pass


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("PASS", name)
    print("All tests passed.")
