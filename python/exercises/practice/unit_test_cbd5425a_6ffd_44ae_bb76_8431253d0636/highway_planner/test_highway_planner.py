import unittest
from highway_planner.highway_planner import optimize_highways

class TestHighwayPlanner(unittest.TestCase):
    def test_basic_case(self):
        cities = [
            (1, 0, 0, 100),
            (2, 1, 0, 150),
            (3, 0, 1, 200),
            (4, 1, 1, 250)
        ]
        max_length = 1.5
        budget = 3.0
        result = optimize_highways(cities, max_length, budget)
        self.assertTrue(self._is_valid_solution(result, cities, max_length, budget))

    def test_no_solution(self):
        cities = [
            (1, 0, 0, 100),
            (2, 10, 0, 150),
            (3, 0, 10, 200)
        ]
        max_length = 1.0
        budget = 5.0
        with self.assertRaises(ValueError):
            optimize_highways(cities, max_length, budget)

    def test_single_city(self):
        cities = [(1, 0, 0, 100)]
        max_length = 5.0
        budget = 10.0
        result = optimize_highways(cities, max_length, budget)
        self.assertEqual(result, [])

    def test_large_case(self):
        cities = [
            (1, 0, 0, 100),
            (2, 1, 0, 150),
            (3, 0, 1, 200),
            (4, 1, 1, 250),
            (5, 2, 0, 300),
            (6, 0, 2, 350),
            (7, 2, 2, 400)
        ]
        max_length = 2.5
        budget = 10.0
        result = optimize_highways(cities, max_length, budget)
        self.assertTrue(self._is_valid_solution(result, cities, max_length, budget))

    def test_edge_case_zero_budget(self):
        cities = [
            (1, 0, 0, 100),
            (2, 1, 0, 150)
        ]
        max_length = 1.5
        budget = 0.0
        with self.assertRaises(ValueError):
            optimize_highways(cities, max_length, budget)

    def _is_valid_solution(self, highways, cities, max_length, budget):
        # Check all highways are within max_length
        city_dict = {cid: (x, y, pop) for cid, x, y, pop in cities}
        total_cost = 0
        
        # Check highway constraints
        for city1, city2 in highways:
            x1, y1, _ = city_dict[city1]
            x2, y2, _ = city_dict[city2]
            distance = ((x2-x1)**2 + (y2-y1)**2)**0.5
            if distance > max_length:
                return False
            total_cost += distance
        
        if total_cost > budget:
            return False
            
        # Check connectivity
        if not self._is_connected(highways, cities):
            return False
            
        return True

    def _is_connected(self, highways, cities):
        if not cities:
            return True
        if not highways and len(cities) == 1:
            return True
            
        graph = {cid: set() for cid, _, _, _ in cities}
        for city1, city2 in highways:
            graph[city1].add(city2)
            graph[city2].add(city1)
            
        visited = set()
        stack = [next(iter(graph.keys()))]
        
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                stack.extend(graph[node] - visited)
                
        return len(visited) == len(graph)