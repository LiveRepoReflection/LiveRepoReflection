import unittest
from faulty_agreement import reach_consensus

class TestFaultyAgreement(unittest.TestCase):
    def test_basic_no_faulty_messengers(self):
        # Simple case with no faulty messengers
        result = reach_consensus(
            n=3,
            m=0,
            commander_decision=True,
            messages=[]
        )
        self.assertEqual(result, [True, True, True])
        
    def test_basic_with_one_faulty_messenger(self):
        # Test with one faulty messenger altering a message
        messages = [(0, 1, False)]  # Faulty messenger changes True to False
        result = reach_consensus(
            n=3,
            m=1,
            commander_decision=True,
            messages=messages
        )
        # All generals should still agree on True despite the faulty message
        self.assertEqual(result, [True, True, True])

    def test_multiple_faulty_messengers(self):
        messages = [
            (0, 1, False),
            (1, 2, True),
            (2, 0, False)
        ]
        result = reach_consensus(
            n=4,
            m=2,
            commander_decision=False,
            messages=messages
        )
        # Check all generals reached the same decision
        self.assertEqual(len(set(result)), 1)
        
    def test_maximum_generals(self):
        # Test with large number of generals
        result = reach_consensus(
            n=1000,
            m=2,
            commander_decision=True,
            messages=[(0, 1, False), (1, 2, True)]
        )
        self.assertEqual(len(result), 1000)
        self.assertEqual(len(set(result)), 1)  # All should agree

    def test_edge_cases(self):
        # Test minimum number of generals
        result = reach_consensus(
            n=3,
            m=0,
            commander_decision=False,
            messages=[]
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result, [False, False, False])

    def test_complex_message_patterns(self):
        messages = [
            (0, 1, True),
            (1, 2, False),
            (2, 3, True),
            (3, 0, False),
            (0, 2, True),
            (1, 3, False)
        ]
        result = reach_consensus(
            n=5,
            m=3,
            commander_decision=True,
            messages=messages
        )
        self.assertEqual(len(result), 5)
        self.assertEqual(len(set(result)), 1)  # All should agree

    def test_input_validation(self):
        # Test invalid inputs
        with self.assertRaises(ValueError):
            reach_consensus(n=2, m=0, commander_decision=True, messages=[])
        
        with self.assertRaises(ValueError):
            reach_consensus(n=5, m=5, commander_decision=True, messages=[])
            
        with self.assertRaises(ValueError):
            reach_consensus(n=1001, m=0, commander_decision=True, messages=[])

    def test_message_validation(self):
        # Test invalid message format
        with self.assertRaises(ValueError):
            messages = [(0, 5, True)]  # Invalid receiver_id
            reach_consensus(n=3, m=1, commander_decision=True, messages=messages)

        with self.assertRaises(ValueError):
            messages = [(-1, 1, True)]  # Invalid sender_id
            reach_consensus(n=3, m=1, commander_decision=True, messages=messages)

    def test_consistency_with_different_message_orders(self):
        # Test that the result is consistent regardless of message order
        messages1 = [(0, 1, False), (1, 2, True)]
        messages2 = [(1, 2, True), (0, 1, False)]
        
        result1 = reach_consensus(n=4, m=1, commander_decision=True, messages=messages1)
        result2 = reach_consensus(n=4, m=1, commander_decision=True, messages=messages2)
        
        self.assertEqual(result1, result2)

    def test_all_possible_decisions_for_small_case(self):
        # Test all possible combinations for a small case
        for commander_decision in [True, False]:
            for m in range(2):
                result = reach_consensus(
                    n=4,
                    m=m,
                    commander_decision=commander_decision,
                    messages=[]
                )
                # Verify all generals reached same decision
                self.assertEqual(len(set(result)), 1)
                # If no faulty messengers, verify decision matches commander
                if m == 0:
                    self.assertEqual(result[0], commander_decision)

if __name__ == '__main__':
    unittest.main()