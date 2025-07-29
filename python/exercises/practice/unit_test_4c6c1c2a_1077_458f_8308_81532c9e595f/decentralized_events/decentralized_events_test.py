import unittest
from decentralized_events import run_distributed_scheduler

def conflict_between(event1, event2):
    s1, d1 = event1
    s2, d2 = event2
    return max(s1, s2) < min(s1 + d1, s2 + d2)

class DecentralizedEventsTest(unittest.TestCase):
    def test_output_structure_single_agent(self):
        # Single agent with one event and no neighbors.
        agents_data = {
            0: ([(10, 5, 3)], [])
        }
        outputs = run_distributed_scheduler(agents_data)
        self.assertIn(0, outputs)
        adjusted_events, estimated_skews = outputs[0]
        
        # Check that adjusted_events is a list of tuples (start_time, duration)
        self.assertIsInstance(adjusted_events, list)
        self.assertEqual(len(adjusted_events), len(agents_data[0][0]))
        for event in adjusted_events:
            self.assertIsInstance(event, tuple)
            self.assertEqual(len(event), 2)
            self.assertIsInstance(event[0], int)
            self.assertIsInstance(event[1], int)
            # Adjusted start times should be non-negative.
            self.assertGreaterEqual(event[0], 0)
        
        # Check that estimated_skews is an empty dictionary (no neighbors).
        self.assertIsInstance(estimated_skews, dict)
        self.assertEqual(estimated_skews, {})

    def test_structure_two_agents(self):
        # Two agents with each one event and a single neighbor connection.
        agents_data = {
            0: ([(10, 5, 3)], [1]),
            1: ([(12, 5, 2)], [0])
        }
        outputs = run_distributed_scheduler(agents_data)
        for agent in [0, 1]:
            self.assertIn(agent, outputs)
            adjusted_events, estimated_skews = outputs[agent]
            # Check that adjusted_events length matches input events.
            self.assertIsInstance(adjusted_events, list)
            self.assertEqual(len(adjusted_events), len(agents_data[agent][0]))
            for event in adjusted_events:
                self.assertIsInstance(event, tuple)
                self.assertEqual(len(event), 2)
                self.assertIsInstance(event[0], int)
                self.assertIsInstance(event[1], int)
                self.assertGreaterEqual(event[0], 0)
            # Check that estimated_skews is a dict with keys matching neighbors.
            self.assertIsInstance(estimated_skews, dict)
            self.assertEqual(set(estimated_skews.keys()), set(agents_data[agent][1]))
            for offset in estimated_skews.values():
                self.assertIsInstance(offset, int)

    def test_conflict_resolution(self):
        # Two agents with initially conflicting events.
        agents_data = {
            0: ([(10, 5, 3)], [1]),
            1: ([(12, 5, 2)], [0])
        }
        # Count initial conflicts using raw event times.
        conflicts_initial = 0
        for e0 in agents_data[0][0]:
            for e1 in agents_data[1][0]:
                if conflict_between((e0[0], e0[1]), (e1[0], e1[1])):
                    conflicts_initial += 1

        outputs = run_distributed_scheduler(agents_data)
        # Count conflicts in adjusted schedules.
        conflicts_adjusted = 0
        adjusted_events_0 = outputs[0][0]
        adjusted_events_1 = outputs[1][0]
        for e0 in adjusted_events_0:
            for e1 in adjusted_events_1:
                if conflict_between(e0, e1):
                    conflicts_adjusted += 1
        # The scheduler should not worsen conflicts.
        self.assertLessEqual(conflicts_adjusted, conflicts_initial)

    def test_clock_skew_consistency(self):
        # Three agents fully connected among neighbors.
        agents_data = {
            0: ([(10, 5, 3)], [1, 2]),
            1: ([(12, 5, 2)], [0, 2]),
            2: ([(15, 5, 1)], [0, 1])
        }
        outputs = run_distributed_scheduler(agents_data)
        # For every pair of connected agents, check that the clock skew estimates are negatives of each other.
        for i in outputs:
            _, skews_i = outputs[i]
            for j in skews_i:
                self.assertIn(j, outputs)
                _, skews_j = outputs[j]
                self.assertIn(i, skews_j)
                self.assertEqual(skews_i[j], -skews_j[i])

    def test_non_negative_adjusted_times(self):
        # Agents with events starting near zero should have non-negative adjusted event times.
        agents_data = {
            0: ([(0, 4, 1)], [1]),
            1: ([(1, 4, 2)], [0])
        }
        outputs = run_distributed_scheduler(agents_data)
        for agent in outputs:
            adjusted_events, _ = outputs[agent]
            for event in adjusted_events:
                self.assertGreaterEqual(event[0], 0)

if __name__ == '__main__':
    unittest.main()