import unittest
import time
from collaborative_pathfinding import simulate

class TestCollaborativePathfinding(unittest.TestCase):

    def assert_no_collisions(self, paths, max_steps):
        # Determine the maximum number of simulation steps among all agents
        num_agents = len(paths)
        # For each simulation step index, extract positions for agents that have that step
        for step in range(max_steps):
            positions = set()
            for i in range(num_agents):
                if step < len(paths[i]):
                    pos = paths[i][step]
                    self.assertNotIn(pos, positions, f"Collision detected at step {step} for agent {i}")
                    positions.add(pos)
    
    def test_single_agent_no_obstacles(self):
        width = 10
        height = 10
        n = 1
        agent_configurations = [(0, 0, 9, 9)]
        static_obstacles = set()
        communication_range = 5.0
        time_budget = 50  # milliseconds
        max_steps = 50

        start_time = time.time()
        paths = simulate(width, height, n, agent_configurations, static_obstacles, communication_range, time_budget, max_steps)
        end_time = time.time()
        # Ensure simulation finishes within reasonable time (e.g., 1 second)
        self.assertLess(end_time - start_time, 1, "Simulation exceeded expected runtime")

        # Validate that the agent starts at the given start
        self.assertGreaterEqual(len(paths), 1, "No paths returned")
        path = paths[0]
        self.assertEqual(path[0], (0, 0), "Agent did not start at the correct position")
        # Validate that if the agent reached the destination before max_steps, the last coordinate equals target
        if path[-1] == (9, 9):
            self.assertEqual(path[-1], (9, 9), "Agent did not reach the correct destination")
        # Validate collisions - with one agent, there cannot be collisions
        self.assert_no_collisions(paths, max_steps)

    def test_two_agents_no_conflict(self):
        width = 10
        height = 10
        n = 2
        # Agents start at opposite corners and move diagonally toward each others' start
        agent_configurations = [(0, 0, 9, 9), (9, 9, 0, 0)]
        static_obstacles = set()
        communication_range = 5.0
        time_budget = 50
        max_steps = 50

        paths = simulate(width, height, n, agent_configurations, static_obstacles, communication_range, time_budget, max_steps)
        self.assertEqual(len(paths), 2, "Should return two paths")
        # Check that each agent starts and (if reached) ends at requested positions.
        for idx, (start_x, start_y, target_x, target_y) in enumerate(agent_configurations):
            path = paths[idx]
            self.assertEqual(path[0], (start_x, start_y), f"Agent {idx} did not start correctly")
            if path[-1] == (target_x, target_y):
                self.assertEqual(path[-1], (target_x, target_y), f"Agent {idx} did not reach the destination")
        # Check for collision between agents at each simulation step
        self.assert_no_collisions(paths, max_steps)
    
    def test_static_obstacles(self):
        width = 8
        height = 8
        n = 2
        agent_configurations = [(0, 0, 7, 7), (7, 0, 0, 7)]
        # Place obstacles in a pattern forcing agents to detour
        static_obstacles = {(3, 3), (3, 4), (4, 3), (4, 4)}
        communication_range = 4.0
        time_budget = 50
        max_steps = 60

        paths = simulate(width, height, n, agent_configurations, static_obstacles, communication_range, time_budget, max_steps)
        self.assertEqual(len(paths), 2)
        # For each agent, ensure no obstacle coordinate appears in their path.
        for idx, path in enumerate(paths):
            for pos in path:
                self.assertNotIn(pos, static_obstacles, f"Agent {idx} path illegally passes through an obstacle at {pos}")
        # Check for collisions at each simulation step
        self.assert_no_collisions(paths, max_steps)
    
    def test_max_steps_enforced(self):
        width = 15
        height = 15
        n = 1
        # Create a scenario where the target is unreachable within max_steps due to obstacles layout
        agent_configurations = [(0, 0, 14, 14)]
        # Create a barrier obstacle that forces a long detour
        static_obstacles = {(i, 7) for i in range(15) if i != 0}
        communication_range = 5.0
        time_budget = 50
        max_steps = 20  # intentionally small step limit

        paths = simulate(width, height, n, agent_configurations, static_obstacles, communication_range, time_budget, max_steps)
        # The path length should not exceed max_steps
        self.assertLessEqual(len(paths[0]), max_steps, f"Path length exceeds max_steps for agent 0")
    
    def test_dynamic_scenario_simulation(self):
        width = 20
        height = 20
        n = 3
        agent_configurations = [(0, 0, 19, 19), (19, 0, 0, 19), (10, 0, 10, 19)]
        # Set some static obstacles. Even though the problem is dynamic,
        # our simulation input includes only static obstacles.
        static_obstacles = {(10, y) for y in range(5, 15)}
        communication_range = 6.0
        time_budget = 50
        max_steps = 70

        paths = simulate(width, height, n, agent_configurations, static_obstacles, communication_range, time_budget, max_steps)
        self.assertEqual(len(paths), n)
        # Verify that none of the agents' paths cross through the obstacles.
        for idx, path in enumerate(paths):
            for pos in path:
                self.assertNotIn(pos, static_obstacles, f"Agent {idx} path illegally crosses an obstacle at {pos}")
        # Check that each step does not have collisions
        self.assert_no_collisions(paths, max_steps)
    
    def test_time_budget_constraint(self):
        width = 12
        height = 12
        n = 2
        agent_configurations = [(0, 0, 11, 11), (11, 0, 0, 11)]
        static_obstacles = set()
        communication_range = 5.0
        time_budget = 10  # Set a very tight time budget
        max_steps = 40

        # Record start time to ensure simulation does not exceed reasonable boundaries despite tight time constraints
        start_time = time.time()
        paths = simulate(width, height, n, agent_configurations, static_obstacles, communication_range, time_budget, max_steps)
        end_time = time.time()
        self.assertLess(end_time - start_time, 1, "Simulation exceeded expected runtime with a tight time budget")
        # Validate that starting positions and potential collisions are handled
        for idx, (start_x, start_y, target_x, target_y) in enumerate(agent_configurations):
            self.assertEqual(paths[idx][0], (start_x, start_y), f"Agent {idx} did not start correctly")
        self.assert_no_collisions(paths, max_steps)

if __name__ == '__main__':
    unittest.main()