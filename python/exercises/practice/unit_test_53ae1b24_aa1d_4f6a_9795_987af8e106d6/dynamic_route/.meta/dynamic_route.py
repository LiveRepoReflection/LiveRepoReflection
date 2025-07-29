import heapq
from collections import defaultdict

class RoutePlanner:
    def __init__(self, grid):
        self.grid = grid
        self.size = len(grid)
        self.temp_obstacles = set()
        self.distance_cache = defaultdict(dict)
        self.previous_cache = defaultdict(dict)
        
    def add_obstacle(self, x, y):
        if self.grid[x][y] == 0:
            self.temp_obstacles.add((x, y))
            self._invalidate_cache()

    def remove_obstacle(self, x, y):
        if (x, y) in self.temp_obstacles:
            self.temp_obstacles.remove((x, y))
            self._invalidate_cache()

    def _invalidate_cache(self):
        self.distance_cache.clear()
        self.previous_cache.clear()

    def _is_valid(self, x, y):
        return (0 <= x < self.size and 0 <= y < self.size and
                self.grid[x][y] == 0 and (x, y) not in self.temp_obstacles)

    def _get_neighbors(self, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self._is_valid(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def find_shortest_path(self, start_x, start_y, end_x, end_y):
        if not self._is_valid(start_x, start_y) or not self._is_valid(end_x, end_y):
            return []

        cache_key = (start_x, start_y)
        if (end_x, end_y) in self.distance_cache.get(cache_key, {}):
            return self._reconstruct_path(cache_key, (end_x, end_y))

        heap = []
        heapq.heappush(heap, (0, start_x, start_y))
        distances = defaultdict(lambda: float('inf'))
        distances[(start_x, start_y)] = 0
        previous = {}

        while heap:
            current_dist, x, y = heapq.heappop(heap)
            if (x, y) == (end_x, end_y):
                self._update_cache(cache_key, distances, previous)
                return self._reconstruct_path(cache_key, (end_x, end_y))

            if current_dist > distances[(x, y)]:
                continue

            for nx, ny in self._get_neighbors(x, y):
                distance = current_dist + 1
                if distance < distances[(nx, ny)]:
                    distances[(nx, ny)] = distance
                    previous[(nx, ny)] = (x, y)
                    heapq.heappush(heap, (distance, nx, ny))

        return []

    def _update_cache(self, cache_key, distances, previous):
        for (x, y), dist in distances.items():
            self.distance_cache[cache_key][(x, y)] = dist
        for (x, y), prev in previous.items():
            self.previous_cache[cache_key][(x, y)] = prev

    def _reconstruct_path(self, cache_key, end_pos):
        path = []
        current = end_pos
        while current in self.previous_cache[cache_key]:
            path.append(current)
            current = self.previous_cache[cache_key][current]
        path.append(current)
        path.reverse()
        return path