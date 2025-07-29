import io
import sys
import unittest
from contextlib import redirect_stdout
from route_master import solve

class TestRouteMaster(unittest.TestCase):
    def run_test_with_input(self, input_str, expected_output_str):
        stdin = io.StringIO(input_str)
        stdout = io.StringIO()
        sys.stdin = stdin
        try:
            with redirect_stdout(stdout):
                solve()
        finally:
            sys.stdin = sys.__stdin__
        output = stdout.getvalue().strip()
        self.assertEqual(output, expected_output_str)
    
    def test_single_customer_no_update(self):
        # Test case 1: One depot, one customer, no update.
        # Expected outcome: one vehicle used.
        input_data = "\n".join([
            "1 1 1",         # N M K
            "100",           # Depot capacities
            "10 0 100 5",    # Customer: demand, start, end, service time
            "0 5",           # Travel time matrix row 0: depot to depot, depot to customer
            "5 0",           # Travel time matrix row 1: customer to depot, customer to customer (not used)
            "0"              # U: no update events
        ])
        # For this simple case, assume the optimal solution uses 1 vehicle.
        expected_output = "1"
        self.run_test_with_input(input_data, expected_output)
    
    def test_multiple_customers_with_update(self):
        # Test case 2: Two depots, three customers and one update event.
        # Constructed such that the optimal solution uses 2 vehicles.
        input_data = "\n".join([
            "2 3 5",                     # N M K
            "100 100",                   # Depot capacities
            "10 0 60 10",                # Customer 0: D, start, end, service time
            "20 20 80 10",               # Customer 1
            "15 40 120 10",              # Customer 2
            # Travel time matrix (5 rows: 2 depots + 3 customers)
            "0 5 10 15 20",
            "5 0 10 10 15",
            "10 10 0 5 10",
            "15 10 5 0 5",
            "20 15 10 5 0",
            "1",                         # U: 1 update event
            "30 1 25"                    # Update event: at time 30, change customer 1 demand to 25
        ])
        # For this test case, assume the optimal solution uses 2 vehicles.
        expected_output = "2"
        self.run_test_with_input(input_data, expected_output)
    
    def test_complex_scenario_with_multiple_updates(self):
        # Test case 3: Two depots, four customers with two update events.
        # Designed with tighter depot capacities to force splitting deliveries.
        input_data = "\n".join([
            "2 4 5",                      # N M K
            "50 50",                      # Depot capacities
            "30 10 100 10",               # Customer 0
            "30 20 120 10",               # Customer 1
            "40 15 90 10",                # Customer 2
            "20 50 150 10",               # Customer 3
            # Travel time matrix (6 rows: 2 depots + 4 customers)
            "0 10 20 30 40 50",
            "10 0 25 35 45 55",
            "20 25 0 15 25 35",
            "30 35 15 0 20 30",
            "40 45 25 20 0 15",
            "50 55 35 30 15 0",
            "2",                          # U: 2 update events
            "60 2 50",                    # Update: at time 60, change customer 2 demand to 50
            "80 0 35"                     # Update: at time 80, change customer 0 demand to 35
        ])
        # For this test, assume the optimal solution uses 3 vehicles.
        expected_output = "3"
        self.run_test_with_input(input_data, expected_output)

if __name__ == "__main__":
    unittest.main()