import unittest
from byzantine_strategy import solve_byzantine_generals

def create_receive_messages(sim_dict):
    def receive_messages(general_id, round_number):
        return sim_dict.get((general_id, round_number), [])
    return receive_messages

class ByzantineStrategyTest(unittest.TestCase):
    def test_single_general(self):
        # N=1, T=0, commander is the only general.
        N = 1
        T = 0
        # With one general, no messages are passed. Assume commander's order is embedded.
        # We simulate by returning empty list for any query.
        sim_dict = {}
        receive_messages = create_receive_messages(sim_dict)
        # Expected: since commander is the only general, his order (simulate as "Attack")
        # In our simulation, we assume the algorithm treats N=1 as using the given commander's order.
        result = solve_byzantine_generals(N, T, receive_messages)
        self.assertEqual(result, "Attack")

    def test_no_traitors_attack(self):
        # N=4, T=1, all commanders and generals are loyal. Commander's order is "Attack".
        N = 4
        T = 1
        # For T = 1, assume the consensus algorithm runs for 2 rounds (rounds 1 and 2).
        # All loyal generals always forward the correct order "Attack".
        sim_dict = {}
        # For each loyal general (including commander if needed) we simulate that they always receive "Attack"
        for round_number in [1, 2]:
            for general_id in range(N):
                # Each general receives messages from the other N-1 generals.
                sim_dict[(general_id, round_number)] = ["Attack"] * (N - 1)
        receive_messages = create_receive_messages(sim_dict)
        result = solve_byzantine_generals(N, T, receive_messages)
        self.assertEqual(result, "Attack")

    def test_no_traitors_retreat(self):
        # N=4, T=1, all generals are loyal. Commander's order is "Retreat".
        N = 4
        T = 1
        sim_dict = {}
        for round_number in [1, 2]:
            for general_id in range(N):
                sim_dict[(general_id, round_number)] = ["Retreat"] * (N - 1)
        receive_messages = create_receive_messages(sim_dict)
        result = solve_byzantine_generals(N, T, receive_messages)
        self.assertEqual(result, "Retreat")

    def test_traitor_present(self):
        # N=4, T=1, with one traitor (general 2).
        # Commander is loyal and issues "Attack".
        # Trait our general 2 sends conflicting orders.
        N = 4
        T = 1
        sim_dict = {}
        # Define rounds 1 and 2.
        for round_number in [1, 2]:
            # For general 1, simulate receiving messages from generals: 0,2,3.
            # General 0 and 3 are loyal sending "Attack", general 2 (traitor) sends "Retreat".
            sim_dict[(1, round_number)] = ["Attack", "Retreat", "Attack"]
            # For general 3, simulate: messages from generals: 0,1,2.
            sim_dict[(3, round_number)] = ["Attack", "Attack", "Retreat"]
            # For the traitor (general 2) it doesn't matter what is received; but we define for completeness.
            sim_dict[(2, round_number)] = ["Attack", "Attack", "Attack"]
            # For the commander (general 0), simulate loyal transmissions from others.
            sim_dict[(0, round_number)] = ["Attack", "Attack", "Attack"]
        receive_messages = create_receive_messages(sim_dict)
        result = solve_byzantine_generals(N, T, receive_messages)
        # Loyal generals should follow the commander's order "Attack".
        self.assertEqual(result, "Attack")

    def test_insufficient_generals(self):
        # N=3, T=1, commander is traitor.
        # In the classic Byzantine problem, for N <= 3T, consensus may not be possible.
        # We simulate conflicting messages:
        N = 3
        T = 1
        sim_dict = {}
        # For rounds 1 and 2:
        for round_number in [1, 2]:
            # For general 1, commander (general 0, traitor) sends "Attack" and general 2 sends "Retreat".
            sim_dict[(1, round_number)] = ["Attack", "Retreat"]
            # For general 2, commander sends "Retreat" and general 1 sends "Attack".
            sim_dict[(2, round_number)] = ["Retreat", "Attack"]
            # For the traitorous commander general 0, we simulate some messages as well.
            sim_dict[(0, round_number)] = ["Attack", "Retreat"]
        receive_messages = create_receive_messages(sim_dict)
        result = solve_byzantine_generals(N, T, receive_messages)
        self.assertEqual(result, "Undecided")

if __name__ == '__main__':
    unittest.main()