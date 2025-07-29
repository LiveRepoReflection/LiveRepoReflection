import heapq
from collections import defaultdict

class TrainScheduler:
    def __init__(self, n):
        # n: number of stations
        self.n = n
        # Graph stored as: graph[u][v] = (travel_time, capacity)
        self.graph = [dict() for _ in range(n)]
    
    def add_track(self, station1, station2, travel_time, capacity):
        # Update track from station1 to station2
        self.graph[station1][station2] = (travel_time, capacity)
        self.graph[station2][station1] = (travel_time, capacity)
    
    def shortest_time(self, start_station, end_station):
        # Uses Dijkstra to find the shortest travel time using all tracks regardless of capacity.
        if start_station == end_station:
            return 0
        dist = [float('inf')] * self.n
        dist[start_station] = 0
        heap = [(0, start_station)]
        while heap:
            current_time, node = heapq.heappop(heap)
            if node == end_station:
                return current_time
            if current_time > dist[node]:
                continue
            for neighbor, (time, cap) in self.graph[node].items():
                new_time = current_time + time
                if new_time < dist[neighbor]:
                    dist[neighbor] = new_time
                    heapq.heappush(heap, (new_time, neighbor))
        return -1 if dist[end_station] == float('inf') else dist[end_station]
    
    def max_passengers(self, start_station, end_station, time_window):
        # For maximum passengers, we want to maximize:
        # (time_window - route_time + 1) * bottleneck_capacity
        # Consider only routes with route_time <= time_window.
        # We iterate through capacities that occur in the graph (each track's capacity).
        candidate_caps = set()
        for u in range(self.n):
            for v, (time, cap) in self.graph[u].items():
                if u < v:
                    candidate_caps.add(cap)
        if not candidate_caps:
            return 0

        max_total = 0
        sorted_caps = sorted(candidate_caps, reverse=True)
        # For each candidate capacity threshold, filter graph and compute shortest travel time.
        for cap_threshold in sorted_caps:
            t = self._filtered_shortest_time(start_station, end_station, cap_threshold)
            if t == -1 or t > time_window:
                continue
            departures = time_window - t + 1
            total = departures * cap_threshold
            if total > max_total:
                max_total = total
        return max_total

    def _filtered_shortest_time(self, start_station, end_station, cap_threshold):
        # Dijkstra on graph restricted to edges with capacity >= cap_threshold.
        if start_station == end_station:
            return 0
        dist = [float('inf')] * self.n
        dist[start_station] = 0
        heap = [(0, start_station)]
        while heap:
            current_time, node = heapq.heappop(heap)
            if node == end_station:
                return current_time
            if current_time > dist[node]:
                continue
            for neighbor, (time, cap) in self.graph[node].items():
                if cap < cap_threshold:
                    continue
                new_time = current_time + time
                if new_time < dist[neighbor]:
                    dist[neighbor] = new_time
                    heapq.heappush(heap, (new_time, neighbor))
        return -1 if dist[end_station] == float('inf') else dist[end_station]