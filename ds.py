"""Hand-written data structures (no collections/heapq shortcuts) used by the algorithms."""


class Queue:
    """FIFO queue (used by BFS). Uses a list plus a head index so dequeue is O(1)."""
    def __init__(self):
        self._items, self._head = [], 0

    def enqueue(self, x):
        self._items.append(x)

    def dequeue(self):
        x = self._items[self._head]
        self._head += 1
        return x

    def is_empty(self):
        return self._head >= len(self._items)

    def __len__(self):
        return len(self._items) - self._head


class Stack:
    """LIFO stack (used by DFS pathfinding and the DFS maze generator's backtracking)."""
    def __init__(self):
        self._items = []

    def push(self, x):
        self._items.append(x)

    def pop(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)


class MinHeap:
    """Binary min-heap priority queue (used by Dijkstra). push/pop are O(log n)."""
    def __init__(self):
        self._a, self._count = [], 0        # _count breaks ties so items are never compared

    def push(self, priority, item):
        self._a.append((priority, self._count, item))
        self._count += 1
        i = len(self._a) - 1
        while i > 0:                          # sift UP
            parent = (i - 1) // 2
            if self._a[i][:2] < self._a[parent][:2]:
                self._a[i], self._a[parent] = self._a[parent], self._a[i]
                i = parent
            else:
                break

    def pop(self):
        """Remove and return (priority, item) with the smallest priority."""
        top = self._a[0]
        last = self._a.pop()
        if self._a:
            self._a[0] = last
            i, n = 0, len(self._a)
            while True:                       # sift DOWN
                l, r, small = 2 * i + 1, 2 * i + 2, i
                if l < n and self._a[l][:2] < self._a[small][:2]:
                    small = l
                if r < n and self._a[r][:2] < self._a[small][:2]:
                    small = r
                if small == i:
                    break
                self._a[i], self._a[small] = self._a[small], self._a[i]
                i = small
        return top[0], top[2]

    def is_empty(self):
        return not self._a

    def __len__(self):
        return len(self._a)
