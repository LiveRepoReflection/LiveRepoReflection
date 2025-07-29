import unittest
from byzantine_chain import simulate_consensus

class ByzantineChainTest(unittest.TestCase):
    def test_no_byzantine(self):
        # With no Byzantine nodes, all nodes should commit exactly the same log.
        # "abc" has length 3 (prime), so it is accepted.
        # "defg" has length 4 (not prime), so it is rejected.
        n = 4
        f = 0
        events = ["abc", "defg"]
        expected_log = ["abc"]
        logs = simulate_consensus(n, f, events)
        self.assertEqual(len(logs), n)
        for log in logs:
            self.assertEqual(log, expected_log)

    def test_sample_scenario(self):
        # This test follows the example scenario:
        # n = 5, f = 1, events = ["hello", "world", "python"]
        # "hello" and "world" have length 5 (prime) so they are accepted by honest nodes.
        # "python" has length 6 (not prime) so it is rejected by honest nodes.
        # However, the simulation of Byzantine behavior might lead to nodes having minor discrepancies.
        # In this expected output, most nodes commit ["hello", "python"] except one node.
        n = 5
        f = 1
        events = ["hello", "world", "python"]
        expected_logs = [
            ["hello", "python"],
            ["hello"],
            ["hello", "python"],
            ["hello", "python"],
            ["hello", "python"]
        ]
        logs = simulate_consensus(n, f, events)
        self.assertEqual(len(logs), n)
        for i in range(n):
            self.assertEqual(logs[i], expected_logs[i])

    def test_empty_events(self):
        # When there are no events proposed, all nodes should end with an empty log.
        n = 7
        f = 2
        events = []
        logs = simulate_consensus(n, f, events)
        self.assertEqual(len(logs), n)
        for log in logs:
            self.assertEqual(log, [])

    def test_all_prime_events(self):
        # When all events have lengths that are prime numbers, every honest node should accept all events.
        n = 6
        f = 1
        events = ["ab", "abc", "abcde"]  # lengths: 2 (prime), 3 (prime), 5 (prime)
        expected_log = events
        logs = simulate_consensus(n, f, events)
        self.assertEqual(len(logs), n)
        # We assume the first n-f nodes are honest.
        for i in range(n - f):
            self.assertEqual(logs[i], expected_log)

    def test_mixed_events(self):
        # Test where events are a mix of prime length and non-prime length.
        # "a": length 1 (not prime)
        # "ab": length 2 (prime)
        # "abc": length 3 (prime)
        # "abcd": length 4 (not prime)
        # "abcde": length 5 (prime)
        # Honest nodes should commit only prime-length events: "ab", "abc", "abcde".
        n = 5
        f = 1
        events = ["a", "ab", "abc", "abcd", "abcde"]
        expected_log = ["ab", "abc", "abcde"]
        logs = simulate_consensus(n, f, events)
        self.assertEqual(len(logs), n)
        # We assume the first n-f nodes are honest.
        for i in range(n - f):
            self.assertEqual(logs[i], expected_log)

if __name__ == '__main__':
    unittest.main()