import os
import tempfile
import unittest
from optimal_air import find_optimal_paths

class OptimalAirTest(unittest.TestCase):
    def test_basic_path(self):
        # Create temporary files for graph, zone, and flight schedule.
        graph_content = "A B 10 5\nB C 15 3\nA C 30 1\n"
        zone_content = "Zone1 20\n"
        flight_content = "F1 A C\n"

        with tempfile.NamedTemporaryFile("w", delete=False) as graph_file:
            graph_file.write(graph_content)
            graph_file.flush()
            graph_filename = graph_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as zone_file:
            zone_file.write(zone_content)
            zone_file.flush()
            zone_filename = zone_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as flight_file:
            flight_file.write(flight_content)
            flight_file.flush()
            flight_filename = flight_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as output_file:
            output_filename = output_file.name

        # Use a penalty multiplier of 2.0 for this test.
        penalty_multiplier = 2.0

        # Execute the optimal path calculation.
        find_optimal_paths(graph_filename, zone_filename, flight_filename, output_filename, penalty_multiplier)

        # Read the result from the output file.
        with open(output_filename, "r") as f:
            result = f.read().strip()

        # For this basic case, assume the optimal path for flight F1 is "A,B,C".
        self.assertEqual(result, "F1: A,B,C")

        # Clean up temporary files.
        os.unlink(graph_filename)
        os.unlink(zone_filename)
        os.unlink(flight_filename)
        os.unlink(output_filename)

    def test_no_path(self):
        # Create files in which no valid path exists from start to destination.
        graph_content = "A B 10 5\n"  # Only a connection between A and B.
        zone_content = ""
        flight_content = "F2 A C\n"  # Flight from A to C, where C is disconnected.

        with tempfile.NamedTemporaryFile("w", delete=False) as graph_file:
            graph_file.write(graph_content)
            graph_file.flush()
            graph_filename = graph_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as zone_file:
            zone_file.write(zone_content)
            zone_file.flush()
            zone_filename = zone_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as flight_file:
            flight_file.write(flight_content)
            flight_file.flush()
            flight_filename = flight_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as output_file:
            output_filename = output_file.name

        penalty_multiplier = 1.0

        find_optimal_paths(graph_filename, zone_filename, flight_filename, output_filename, penalty_multiplier)

        with open(output_filename, "r") as f:
            result = f.read().strip()

        # Expect "No path found" if the flight cannot be routed.
        self.assertEqual(result, "F2: No path found")

        os.unlink(graph_filename)
        os.unlink(zone_filename)
        os.unlink(flight_filename)
        os.unlink(output_filename)

    def test_penalty_edge(self):
        # Create a scenario where a potential path incurs a noise penalty.
        # Two possible paths:
        #   Path 1: A -> B -> C with high noise values that exceed the zone threshold.
        #   Path 2: A -> C direct with lower noise.
        #
        # The graph has:
        #   A B 5 10
        #   B C 5 10
        #   A C 15 1
        # Zone threshold is set so that the cumulative noise along A->B and B->C exceeds it.
        graph_content = "A B 5 10\nB C 5 10\nA C 15 1\n"
        zone_content = "ZoneX 50\n"
        flight_content = "F3 A C\n"

        with tempfile.NamedTemporaryFile("w", delete=False) as graph_file:
            graph_file.write(graph_content)
            graph_file.flush()
            graph_filename = graph_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as zone_file:
            zone_file.write(zone_content)
            zone_file.flush()
            zone_filename = zone_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as flight_file:
            flight_file.write(flight_content)
            flight_file.flush()
            flight_filename = flight_file.name

        with tempfile.NamedTemporaryFile("w", delete=False) as output_file:
            output_filename = output_file.name

        penalty_multiplier = 1.0

        find_optimal_paths(graph_filename, zone_filename, flight_filename, output_filename, penalty_multiplier)

        with open(output_filename, "r") as f:
            result = f.read().strip()

        # In this case, the optimal route should be A -> C direct.
        self.assertEqual(result, "F3: A,C")

        os.unlink(graph_filename)
        os.unlink(zone_filename)
        os.unlink(flight_filename)
        os.unlink(output_filename)

if __name__ == "__main__":
    unittest.main()