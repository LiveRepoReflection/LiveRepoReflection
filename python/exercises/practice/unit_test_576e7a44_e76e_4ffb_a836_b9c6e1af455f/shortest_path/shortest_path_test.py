import unittest
from shortest_path import shortest_path

class ShortestPathTest(unittest.TestCase):
    def test_basic_no_updates(self):
        graph = {
            1: [(2, 2), (3, 5)],
            2: [(4, 1)],
            3: [(4, 3)],
            4: []
        }
        sources = [1, 3]
        destinations = [4]
        updates = []
        # Path through source 3 -> 4 with cost 3 is optimal
        self.assertEqual(shortest_path(graph, sources, destinations, updates), 3)

    def test_basic_with_update(self):
        graph = {
            1: [(2, 2), (3, 5)],
            2: [(4, 1)],
            3: [(4, 3)],
            4: []
        }
        sources = [1]
        destinations = [4]
        updates = [(2, 4, 5)]
        # After updating edge 2->4 weight from 1 to 5, the only path 
        # from 1 would be 1->3->4 (5 + 3 = 8) or 1->2->4 (2 + 5 = 7); hence answer is 7.
        self.assertEqual(shortest_path(graph, sources, destinations, updates), 7)

    def test_no_path(self):
        graph = {
            1: [(2, 2)],
            2: [],
            3: [(4, 1)],
            4: []
        }
        sources = [1]
        destinations = [4]
        updates = []
        # There is no path from 1 to 4 as graph is disconnected
        self.assertEqual(shortest_path(graph, sources, destinations, updates), -1)

    def test_multiple_sources_destinations(self):
        graph = {
            1: [(2, 4), (3, 10)],
            2: [(4, 3)],
            3: [(4, 1), (5, 2)],
            4: [(6, 3)],
            5: [(6, 1)],
            6: []
        }
        sources = [1, 3]
        destinations = [6, 4]
        updates = []
        # Two possible valid answers:
        # From source 1: 1->2->4 = 4+3 = 7 or 1->3->4 = 10+1 = 11.
        # From source 3: 3->4 = 1 or 3->5->6 = 2+1 = 3.
        # Since destination can be either 4 or 6, the minimal cost is 1 (3->4).
        self.assertEqual(shortest_path(graph, sources, destinations, updates), 1)

    def test_multiple_updates_decrease_cost(self):
        graph = {
            1: [(2, 10), (3, 100)],
            2: [(4, 10)],
            3: [(4, 10)],
            4: [(5, 10)],
            5: []
        }
        sources = [1]
        destinations = [5]
        # Initially the cheapest is 1->2->4->5 = 10+10+10 = 30.
        # After the updates, the cheaper path will be created.
        updates = [(1, 3, 1), (3, 4, 1)]
        # With updates: path 1->3->4->5 = 1+1+10 = 12 (cheapest)
        self.assertEqual(shortest_path(graph, sources, destinations, updates), 12)

    def test_update_increases_cost(self):
        graph = {
            1: [(2, 1), (3, 5)],
            2: [(4, 1)],
            3: [(4, 1)],
            4: []
        }
        sources = [1]
        destinations = [4]
        # Initially, the cheapest path is 1->2->4 = 1+1 = 2.
        # After update, edge 2->4 becomes heavier.
        updates = [(2, 4, 10)]
        # Now, the optimal path is 1->3->4 = 5+1 = 6.
        self.assertEqual(shortest_path(graph, sources, destinations, updates), 6)

if __name__ == '__main__':
    unittest.main()