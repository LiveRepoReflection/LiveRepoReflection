import unittest
import subprocess
import sys
import os

class TrafficAdvisorTest(unittest.TestCase):
    def run_solution(self, input_data):
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "traffic_advisor.py")]
        result = subprocess.run(cmd, input=input_data, text=True, capture_output=True, timeout=60)
        return result.stdout.strip(), result.stderr.strip()

    def validate_output_format(self, output, expected_intersections):
        lines = output.splitlines()
        self.assertEqual(len(lines), expected_intersections, f"Expected {expected_intersections} lines, got {len(lines)}")
        for line in lines:
            tokens = line.strip().split()
            self.assertEqual(len(tokens), 2, f"Each line must contain exactly 2 integers, got: {line}")
            for token in tokens:
                try:
                    value = int(token)
                except ValueError:
                    self.fail(f"Token is not an integer: {token}")
                self.assertGreaterEqual(value, 0, "Traffic light duration cannot be negative")
                self.assertLessEqual(value, 20, "Traffic light duration should not exceed 20")

    def test_small_grid(self):
        # 3x3 grid with a building and 2 intersections, 100 vehicles.
        input_data = (
            "3 3 2\n"
            "...\n"
            ".#.\n"
            "...\n"
            "0 0\n"
            "2 2\n"
            "100\n"
        )
        output, stderr = self.run_solution(input_data)
        self.assertEqual(stderr, "", f"Expected no stderr output, but got: {stderr}")
        self.validate_output_format(output, 2)

    def test_medium_grid(self):
        # 5x5 grid with internal obstacles and 3 intersections, 150 vehicles.
        input_data = (
            "5 5 3\n"
            ".....\n"
            ".###.\n"
            ".....\n"
            ".###.\n"
            ".....\n"
            "0 0\n"
            "2 2\n"
            "4 4\n"
            "150\n"
        )
        output, stderr = self.run_solution(input_data)
        self.assertEqual(stderr, "")
        self.validate_output_format(output, 3)

    def test_full_dense_grid(self):
        # 10x10 fully drivable grid, 4 intersections at the corners, 200 vehicles.
        grid = "\n".join(["." * 10 for _ in range(10)])
        input_data = f"10 10 4\n{grid}\n0 0\n0 9\n9 0\n9 9\n200\n"
        output, stderr = self.run_solution(input_data)
        self.assertEqual(stderr, "")
        self.validate_output_format(output, 4)

    def test_unreachable_intersection(self):
        # 5x5 grid with a vertical barrier preventing connectivity between intersections.
        input_data = (
            "5 5 2\n"
            ".....\n"
            "..#..\n"
            "..#..\n"
            "..#..\n"
            ".....\n"
            "0 0\n"
            "4 4\n"
            "120\n"
        )
        output, stderr = self.run_solution(input_data)
        self.assertEqual(stderr, "")
        self.validate_output_format(output, 2)

if __name__ == "__main__":
    unittest.main()