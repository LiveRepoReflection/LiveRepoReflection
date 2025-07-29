import unittest
from drone_swarm import next_target

def is_within_bounds(point, bounds):
    (min_x, min_y), (max_x, max_y) = bounds
    x, y = point
    return min_x <= x <= max_x and min_y <= y <= max_y

def movement_cost(src, dst):
    dx = abs(dst[0] - src[0])
    dy = abs(dst[1] - src[1])
    return (dx + dy) * 0.001

class DroneSwarmTest(unittest.TestCase):
    def test_low_battery(self):
        # When battery is insufficient to move to any new coordinate, the drone must remain in place.
        drone_id = 1
        current_location = (5, 5)
        communication_range = 10
        known_drones = {2: (6, 6), 3: (4, 4)}
        explored_areas = {(5,5), (5,6)}
        poi_candidates = [(7, 7)]
        global_bounds = ((0, 0), (10, 10))
        battery_level = 0.0005  # Insufficient to move anywhere (movement cost >= 0.001 for any move)

        next_loc = next_target(drone_id, current_location, communication_range, known_drones,
                                explored_areas, poi_candidates, global_bounds, battery_level)
        self.assertEqual(next_loc, current_location, "Drone should stay in place if battery is insufficient.")

    def test_within_bounds(self):
        # Any movement decision should result in a target within the global bounds.
        drone_id = 2
        current_location = (3, 3)
        communication_range = 15
        known_drones = {1: (2, 2), 3: (4, 4)}
        explored_areas = {(3,3)}
        poi_candidates = [(8, 8), (1, 1)]
        global_bounds = ((0, 0), (10, 10))
        battery_level = 0.01

        next_loc = next_target(drone_id, current_location, communication_range, known_drones,
                                explored_areas, poi_candidates, global_bounds, battery_level)
        self.assertTrue(is_within_bounds(next_loc, global_bounds), "Target location must be within global bounds.")
        self.assertIsInstance(next_loc, tuple, "Target location must be a tuple.")
        self.assertEqual(len(next_loc), 2, "Target location must be a tuple of two integers.")
        self.assertTrue(all(isinstance(coord, int) for coord in next_loc), "Both coordinates should be integers.")

    def test_explored_unexplored_preference(self):
        # If a POI candidate is available that has not been explored, it is preferable.
        drone_id = 3
        current_location = (2, 2)
        communication_range = 10
        known_drones = {1: (3, 3), 2: (1, 1)}
        explored_areas = {(2,2), (3,3)}
        # One candidate is already explored; the other is new.
        poi_candidates = [(3, 3), (5, 5)]
        global_bounds = ((0, 0), (10, 10))
        battery_level = 0.01

        next_loc = next_target(drone_id, current_location, communication_range, known_drones,
                                explored_areas, poi_candidates, global_bounds, battery_level)
        # Check that if a POI candidate is chosen, and if one candidate is unexplored, it should be prioritized.
        if next_loc in poi_candidates:
            self.assertEqual(next_loc, (5, 5), "Unexplored POI candidate should be prioritized over an explored one.")
        self.assertTrue(is_within_bounds(next_loc, global_bounds), "Returned target must be within global bounds.")

    def test_battery_movement_cost(self):
        # Ensure that if the drone moves, the battery is sufficient for the movement cost.
        drone_id = 4
        current_location = (4, 4)
        communication_range = 10
        known_drones = {}
        explored_areas = {(4,4)}
        poi_candidates = [(7, 4), (4, 7)]
        global_bounds = ((0, 0), (10, 10))
        battery_level = 0.005  # Allows movement cost up to 0.005

        next_loc = next_target(drone_id, current_location, communication_range, known_drones,
                                explored_areas, poi_candidates, global_bounds, battery_level)
        # If the drone moves, the battery level should be enough for the move
        cost = movement_cost(current_location, next_loc)
        self.assertTrue(battery_level >= cost, "Battery level must be sufficient for the intended move.")
        self.assertTrue(is_within_bounds(next_loc, global_bounds), "Target location must remain within bounds.")

    def test_known_drones_influence(self):
        # The decision might be influenced by the positions of known drones.
        drone_id = 5
        current_location = (5, 5)
        communication_range = 10
        known_drones = {6: (8, 8), 7: (2, 2)}
        explored_areas = {(5,5)}
        poi_candidates = [(6, 5), (5, 6)]
        global_bounds = ((0, 0), (10, 10))
        battery_level = 0.02

        next_loc = next_target(drone_id, current_location, communication_range, known_drones,
                                explored_areas, poi_candidates, global_bounds, battery_level)
        # Verify target is within bounds and the battery can cover the move cost.
        cost = movement_cost(current_location, next_loc)
        self.assertTrue(battery_level >= cost, "Battery level must be sufficient for the move.")
        self.assertTrue(is_within_bounds(next_loc, global_bounds), "Target location must be within global bounds.")
        self.assertIsInstance(next_loc, tuple, "Result must be a tuple of two integers.")
        self.assertEqual(len(next_loc), 2, "Result must be a coordinate pair (x, y).")

    def test_no_valid_move_due_to_bounds(self):
        # When the global bounds restrict movement, the drone should stay in place.
        drone_id = 8
        current_location = (0, 0)
        communication_range = 5
        known_drones = {}
        explored_areas = {(0,0)}
        poi_candidates = [(-1, -1), (-2, -2)]
        global_bounds = ((0, 0), (0, 0))  # Drone is locked in place.
        battery_level = 0.02

        next_loc = next_target(drone_id, current_location, communication_range, known_drones,
                                explored_areas, poi_candidates, global_bounds, battery_level)
        self.assertEqual(next_loc, current_location, "Drone should not move outside global bounds.")

if __name__ == '__main__':
    unittest.main()