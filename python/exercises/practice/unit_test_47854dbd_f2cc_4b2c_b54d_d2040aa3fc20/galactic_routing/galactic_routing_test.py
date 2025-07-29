import unittest
from galactic_routing import process_events

class GalacticRoutingTest(unittest.TestCase):
    def test_basic_routing(self):
        events = [
            "ADD_LINK 0 1 50 500 0.9",
            "ADD_LINK 1 2 30 400 0.8",
            "ADD_LINK 0 2 80 300 0.7",
            "QUERY_ROUTE 0 2 100 200",
            "REMOVE_LINK 0 1",
            "QUERY_ROUTE 0 2 100 200"
        ]
        expected_outputs = [
            "0 1 2",
            "0 2"
        ]
        result = process_events(events)
        self.assertEqual(result, expected_outputs)

    def test_no_route(self):
        events = [
            "ADD_LINK 0 1 100 500 0.9",
            "ADD_LINK 2 3 40 300 0.8",
            "QUERY_ROUTE 0 3 50 150"
        ]
        expected_outputs = [
            "NO_ROUTE"
        ]
        result = process_events(events)
        self.assertEqual(result, expected_outputs)

    def test_tight_deadline(self):
        events = [
            "ADD_LINK 0 1 50 500 0.9",
            "ADD_LINK 1 2 70 400 0.8",
            "QUERY_ROUTE 0 2 100 100"
        ]
        expected_outputs = [
            "NO_ROUTE"
        ]
        result = process_events(events)
        self.assertEqual(result, expected_outputs)

    def test_update_link(self):
        events = [
            "ADD_LINK 0 1 100 300 0.5",
            "ADD_LINK 0 1 60 600 0.8",
            "ADD_LINK 1 2 40 400 0.9",
            "QUERY_ROUTE 0 2 100 200"
        ]
        expected_outputs = [
            "0 1 2"
        ]
        result = process_events(events)
        self.assertEqual(result, expected_outputs)

    def test_complex_routing(self):
        events = [
            "ADD_LINK 0 1 40 400 0.9",
            "ADD_LINK 1 2 40 300 0.85",
            "ADD_LINK 0 2 90 600 0.7",
            "ADD_LINK 2 3 30 500 0.95",
            "ADD_LINK 1 3 80 450 0.65",
            "QUERY_ROUTE 0 3 150 200"
        ]
        expected_outputs = [
            "0 1 2 3"
        ]
        result = process_events(events)
        self.assertEqual(result, expected_outputs)

    def test_multiple_queries(self):
        events = [
            "ADD_LINK 0 1 20 500 0.8",
            "ADD_LINK 1 2 20 500 0.8",
            "ADD_LINK 2 3 20 500 0.8",
            "QUERY_ROUTE 0 3 100 100",
            "REMOVE_LINK 1 2",
            "QUERY_ROUTE 0 3 100 100",
            "ADD_LINK 1 2 10 300 0.95",
            "QUERY_ROUTE 0 3 100 100"
        ]
        expected_outputs = [
            "0 1 2 3",
            "NO_ROUTE",
            "0 1 2 3"
        ]
        result = process_events(events)
        self.assertEqual(result, expected_outputs)

if __name__ == '__main__':
    unittest.main()