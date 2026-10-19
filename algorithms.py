"""BFS, DFS and Dijkstra on the grid graph. Each cell is a node; its 4 neighbours are edges."""
import time
from config import *
from ds import Queue, Stack, MinHeap

DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]             # up, right, down, left


def neighbors(grid, cell):
    """Graph adjacency: walkable 4-neighbours of a cell."""
    r, c = cell
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != WALL:
            yield (nr, nc)


def reconstruct_path(parent, start, end):
    """PATH RECONSTRUCTION: walk backwards end -> start through the parent map, then reverse."""
    if end not in parent and end != start:
        return []
    path, cur = [end], end
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path


def _result(name, grid, order, parent, start, end, t0):
    found = end in order
    path = reconstruct_path(parent, start, end) if found else []
    cost = sum(TERRAIN_COST[grid[r][c]] for r, c in path[1:])          # cost of entering each step
    return {"name": name, "found": found, "visited_order": order, "path": path,
            "nodes": len(order), "path_length": max(len(path) - 1, 0) if found else 0,
            "cost": cost if found else 0, "time_ms": (time.perf_counter() - t0) * 1000}


def bfs(grid, start, end):
    """BFS: FIFO Queue -> explores level by level -> fewest steps (shortest if costs are equal)."""
    t0 = time.perf_counter()
    queue, seen, parent, order = Queue(), {start}, {}, []
    queue.enqueue(start)
    while not queue.is_empty():
        cur = queue.dequeue()
        order.append(cur)
        if cur == end:
            break
        for nb in neighbors(grid, cur):
            if nb not in seen:
                seen.add(nb)                       # mark when ENQUEUED so nothing is queued twice
                parent[nb] = cur                   # parent tracking
                queue.enqueue(nb)
    return _result("BFS", grid, order, parent, start, end, t0)


def dfs(grid, start, end):
    """DFS: LIFO Stack -> dives deep first, backtracks at dead ends. Path is NOT guaranteed shortest."""
    t0 = time.perf_counter()
    stack, seen, parent, order = Stack(), set(), {}, []
    stack.push((start, None))
    while not stack.is_empty():
        cur, prev = stack.pop()
        if cur in seen:                            # already explored via another route
            continue
        seen.add(cur)
        if prev is not None:
            parent[cur] = prev
        order.append(cur)
        if cur == end:
            break
        for nb in reversed(list(neighbors(grid, cur))):
            if nb not in seen:
                stack.push((nb, cur))
    return _result("DFS", grid, order, parent, start, end, t0)


def dijkstra(grid, start, end):
    """Dijkstra: Min Heap always pops the cheapest-known cell -> minimum TOTAL COST path."""
    t0 = time.perf_counter()
    heap, dist, parent, done, order = MinHeap(), {start: 0}, {}, set(), []
    heap.push(0, start)
    while not heap.is_empty():
        d, cur = heap.pop()
        if cur in done:                            # stale heap entry (a cheaper one was used)
            continue
        done.add(cur)
        order.append(cur)
        if cur == end:
            break
        for nb in neighbors(grid, cur):
            nd = d + TERRAIN_COST[grid[nb[0]][nb[1]]]
            if nb not in dist or nd < dist[nb]:    # RELAXATION: found a cheaper route to nb
                dist[nb] = nd
                parent[nb] = cur
                heap.push(nd, nb)
    return _result("Dijkstra", grid, order, parent, start, end, t0)


SOLVERS = {"BFS": bfs, "DFS": dfs, "Dijkstra": dijkstra}
