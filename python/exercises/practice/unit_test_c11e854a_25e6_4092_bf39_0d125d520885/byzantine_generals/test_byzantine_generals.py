import unittest
from byzantine_generals import byzantine_agreement

class TestByzantineGenerals(unittest.TestCase):
    # Test cases with no traitors
    def test_no_traitors_attack(self):
        def no_traitors(id): return False
        self.assertEqual(byzantine_agreement(4, 1, 'Attack', no_traitors), 'Attack')
        
    def test_no_traitors_retreat(self):
        def no_traitors(id): return False
        self.assertEqual(byzantine_agreement(4, 1, 'Retreat', no_traitors), 'Retreat')
    
    # Test cases with loyal commander
    def test_loyal_commander_with_traitors_attack(self):
        def traitor_is_general_1(id): return id == 1
        self.assertEqual(byzantine_agreement(4, 1, 'Attack', traitor_is_general_1), 'Attack')
        
    def test_loyal_commander_with_traitors_retreat(self):
        def traitor_is_general_2(id): return id == 2
        self.assertEqual(byzantine_agreement(4, 1, 'Retreat', traitor_is_general_2), 'Retreat')
    
    # Test cases with traitorous commander
    def test_traitorous_commander_attack(self):
        def commander_is_traitor(id): return id == 0
        # With a traitorous commander, the loyal generals must still agree on something
        result = byzantine_agreement(4, 1, 'Attack', commander_is_traitor)
        self.assertIn(result, ['Attack', 'Retreat'])
        
    def test_traitorous_commander_retreat(self):
        def commander_is_traitor(id): return id == 0
        # With a traitorous commander, the loyal generals must still agree on something
        result = byzantine_agreement(4, 1, 'Retreat', commander_is_traitor)
        self.assertIn(result, ['Attack', 'Retreat'])
    
    # Test cases with multiple traitors
    def test_multiple_traitors(self):
        def multiple_traitors(id): return id in [1, 2]
        # With two traitors out of 7 generals, the loyal ones should still agree
        self.assertIn(byzantine_agreement(7, 2, 'Attack', multiple_traitors), ['Attack', 'Retreat'])
    
    # Edge cases
    def test_single_general_loyal(self):
        def no_traitors(id): return False
        # With only one general (the commander) and no traitors, should follow commander's order
        self.assertEqual(byzantine_agreement(1, 0, 'Attack', no_traitors), 'Attack')
    
    def test_minimum_generals_for_one_traitor(self):
        # Need at least 4 generals to tolerate 1 traitor (m < n/3)
        def one_traitor(id): return id == 3
        self.assertEqual(byzantine_agreement(4, 1, 'Attack', one_traitor), 'Attack')
    
    # Test minimum generals required based on m < n/3
    def test_minimum_generals_for_two_traitors(self):
        # Need at least 7 generals to tolerate 2 traitors
        def two_traitors(id): return id in [5, 6]
        self.assertEqual(byzantine_agreement(7, 2, 'Retreat', two_traitors), 'Retreat')
    
    def test_minimum_generals_for_three_traitors(self):
        # Need at least 10 generals to tolerate 3 traitors
        def three_traitors(id): return id in [7, 8, 9]
        self.assertEqual(byzantine_agreement(10, 3, 'Attack', three_traitors), 'Attack')

    # Test complex traitor scenarios
    def test_strategic_traitors(self):
        # Traitors at critical positions
        def strategic_traitors(id): return id in [0, 1, 5]  # Commander is traitor
        self.assertIn(byzantine_agreement(10, 3, 'Attack', strategic_traitors), ['Attack', 'Retreat'])

    # Test randomized traitor configurations
    def test_random_traitors_configuration(self):
        import random
        random.seed(42)  # For reproducibility
        
        n = 10
        m = 3
        traitor_ids = random.sample(range(n), m)
        
        def random_traitors(id): return id in traitor_ids
        
        # Whether the result is 'Attack' or 'Retreat', all loyal generals should agree
        result = byzantine_agreement(n, m, 'Attack', random_traitors)
        self.assertIn(result, ['Attack', 'Retreat'])

if __name__ == '__main__':
    unittest.main()