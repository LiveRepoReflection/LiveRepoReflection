import io
import sys
import unittest
from contextlib import redirect_stdout

from flow_design import solve

class FlowDesignTest(unittest.TestCase):
    def run_io_fun(self, inp):
        backup_stdin = sys.stdin
        sys.stdin = io.StringIO(inp)
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                solve()
        finally:
            sys.stdin = backup_stdin
        return output.getvalue().strip()

    def test_sample(self):
        inp = """4 5 2
0 1 10 1
0 2 5 2
1 3 8 1
2 3 7 2
1 2 3 1
0 3 5
2 3 4"""
        result = self.run_io_fun(inp)
        self.assertEqual(result, "0")

    def test_zero_demand(self):
        inp = """1 0 1
0 0 0"""
        result = self.run_io_fun(inp)
        self.assertEqual(result, "0")

    def test_upgrade_required(self):
        inp = """2 1 1
0 1 2 5
0 1 5"""
        # Required extra capacity: 5 - 2 = 3, total cost = 3*5 = 15.
        result = self.run_io_fun(inp)
        self.assertEqual(result, "15")

    def test_multiple_paths(self):
        inp = """3 3 1
0 1 2 1
1 2 2 1
0 2 5 3
0 2 7"""
        result = self.run_io_fun(inp)
        self.assertEqual(result, "0")

    def test_impossible(self):
        inp = """2 1 1
0 1 10 2
1 0 5"""
        result = self.run_io_fun(inp)
        self.assertEqual(result, "-1")

if __name__ == '__main__':
    unittest.main()