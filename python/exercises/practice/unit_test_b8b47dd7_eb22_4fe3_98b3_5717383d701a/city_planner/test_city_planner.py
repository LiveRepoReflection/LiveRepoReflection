import unittest
from city_planner.city_planner import solve_city_planning

class TestCityPlanner(unittest.TestCase):
    def test_small_grid(self):
        N = 5
        R = 3
        C = 2
        P = 1
        I = 1
        commercial_weight = 50
        park_weight = 30
        infrastructure_weight = 10
        
        grid = solve_city_planning(N, R, C, P, I, commercial_weight, park_weight, infrastructure_weight)
        
        # Verify grid dimensions
        self.assertEqual(len(grid), N)
        for row in grid:
            self.assertEqual(len(row), N)
            
        # Count building types
        r_count = sum(row.count('R') for row in grid)
        c_count = sum(row.count('C') for row in grid)
        p_count = sum(row.count('P') for row in grid)
        i_count = sum(row.count('I') for row in grid)
        
        self.assertEqual(r_count, R)
        self.assertEqual(c_count, C)
        self.assertEqual(p_count, P)
        self.assertEqual(i_count, I)
        
        # Verify no park adjacent to commercial
        for i in range(N):
            for j in range(N):
                if grid[i][j] == 'P':
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < N and 0 <= nj < N:
                            self.assertNotEqual(grid[ni][nj], 'C')

    def test_medium_grid(self):
        N = 8
        R = 5
        C = 3
        P = 2
        I = 2
        commercial_weight = 60
        park_weight = 40
        infrastructure_weight = 15
        
        grid = solve_city_planning(N, R, C, P, I, commercial_weight, park_weight, infrastructure_weight)
        
        # Verify grid dimensions
        self.assertEqual(len(grid), N)
        for row in grid:
            self.assertEqual(len(row), N)
            
        # Count building types
        r_count = sum(row.count('R') for row in grid)
        c_count = sum(row.count('C') for row in grid)
        p_count = sum(row.count('P') for row in grid)
        i_count = sum(row.count('I') for row in grid)
        
        self.assertEqual(r_count, R)
        self.assertEqual(c_count, C)
        self.assertEqual(p_count, P)
        self.assertEqual(i_count, I)
        
        # Verify no park adjacent to commercial
        for i in range(N):
            for j in range(N):
                if grid[i][j] == 'P':
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < N and 0 <= nj < N:
                            self.assertNotEqual(grid[ni][nj], 'C')

    def test_large_grid(self):
        N = 10
        R = 8
        C = 4
        P = 3
        I = 3
        commercial_weight = 70
        park_weight = 50
        infrastructure_weight = 20
        
        grid = solve_city_planning(N, R, C, P, I, commercial_weight, park_weight, infrastructure_weight)
        
        # Verify grid dimensions
        self.assertEqual(len(grid), N)
        for row in grid:
            self.assertEqual(len(row), N)
            
        # Count building types
        r_count = sum(row.count('R') for row in grid)
        c_count = sum(row.count('C') for row in grid)
        p_count = sum(row.count('P') for row in grid)
        i_count = sum(row.count('I') for row in grid)
        
        self.assertEqual(r_count, R)
        self.assertEqual(c_count, C)
        self.assertEqual(p_count, P)
        self.assertEqual(i_count, I)
        
        # Verify no park adjacent to commercial
        for i in range(N):
            for j in range(N):
                if grid[i][j] == 'P':
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < N and 0 <= nj < N:
                            self.assertNotEqual(grid[ni][nj], 'C')

    def test_edge_case_minimum_grid(self):
        N = 5
        R = 1
        C = 1
        P = 1
        I = 1
        commercial_weight = 10
        park_weight = 10
        infrastructure_weight = 10
        
        grid = solve_city_planning(N, R, C, P, I, commercial_weight, park_weight, infrastructure_weight)
        
        # Verify grid dimensions
        self.assertEqual(len(grid), N)
        for row in grid:
            self.assertEqual(len(row), N)
            
        # Count building types
        r_count = sum(row.count('R') for row in grid)
        c_count = sum(row.count('C') for row in grid)
        p_count = sum(row.count('P') for row in grid)
        i_count = sum(row.count('I') for row in grid)
        
        self.assertEqual(r_count, R)
        self.assertEqual(c_count, C)
        self.assertEqual(p_count, P)
        self.assertEqual(i_count, I)
        
        # Verify no park adjacent to commercial
        for i in range(N):
            for j in range(N):
                if grid[i][j] == 'P':
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < N and 0 <= nj < N:
                            self.assertNotEqual(grid[ni][nj], 'C')

if __name__ == '__main__':
    unittest.main()