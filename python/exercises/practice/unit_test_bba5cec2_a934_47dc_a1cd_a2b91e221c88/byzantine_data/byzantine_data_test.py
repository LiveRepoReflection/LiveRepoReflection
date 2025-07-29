import unittest
from byzantine_data import simulate_protocol

class TestByzantineDataProtocol(unittest.TestCase):
    def test_all_honest(self):
        # Test simulation with no Byzantine banks
        num_banks = 4
        byzantine_count = 0
        banks = simulate_protocol(num_banks, byzantine_count)
        
        # Check that we got the correct number of banks
        self.assertEqual(len(banks), num_banks)
        
        # Check that none of the banks are marked as Byzantine
        for bank in banks:
            self.assertFalse(bank.is_byzantine, f"Bank {bank.id} should be honest")
        
        # Check that all honest banks reached the same reconciled dataset
        # Assume that each bank has an attribute 'dataset'
        first_dataset = banks[0].dataset
        for bank in banks[1:]:
            self.assertEqual(bank.dataset, first_dataset, f"Bank {bank.id} dataset does not match consensus")
    
    def test_with_byzantine_banks(self):
        # Test simulation with a mix of honest and Byzantine banks
        num_banks = 7
        byzantine_count = 2
        banks = simulate_protocol(num_banks, byzantine_count)
        
        # Check that we got the correct number of banks
        self.assertEqual(len(banks), num_banks)
        
        # Count honest and Byzantine banks
        honest_banks = [bank for bank in banks if not bank.is_byzantine]
        byzantine_banks = [bank for bank in banks if bank.is_byzantine]
        self.assertEqual(len(byzantine_banks), byzantine_count, "Number of Byzantine banks does not match expectation")
        
        # Verify that all honest banks have identical reconciled dataset
        self.assertGreater(len(honest_banks), 0, "There should be at least one honest bank")
        consensus_dataset = honest_banks[0].dataset
        for bank in honest_banks[1:]:
            self.assertEqual(bank.dataset, consensus_dataset, 
                             f"Honest bank {bank.id} did not reach consensus with others")
    
    def test_invalid_fault_configuration(self):
        # This simulation should not be allowed if n <= 3f, so we expect an exception
        num_banks = 3
        byzantine_count = 1
        with self.assertRaises(ValueError) as context:
            simulate_protocol(num_banks, byzantine_count)
        self.assertIn("n must be greater than 3f", str(context.exception))
    
    def test_multiple_configurations(self):
        # Test a couple of different configurations to ensure protocol stability.
        
        # Configuration 1:
        num_banks = 10
        byzantine_count = 2
        banks = simulate_protocol(num_banks, byzantine_count)
        honest_banks = [bank for bank in banks if not bank.is_byzantine]
        self.assertTrue(len(honest_banks) >= num_banks - byzantine_count)
        consensus_dataset = honest_banks[0].dataset
        for bank in honest_banks[1:]:
            self.assertEqual(bank.dataset, consensus_dataset,
                             f"Honest bank {bank.id} does not agree with consensus in configuration 1")

        # Configuration 2:
        num_banks = 16
        byzantine_count = 4
        banks = simulate_protocol(num_banks, byzantine_count)
        honest_banks = [bank for bank in banks if not bank.is_byzantine]
        self.assertTrue(len(honest_banks) >= num_banks - byzantine_count)
        consensus_dataset = honest_banks[0].dataset
        for bank in honest_banks[1:]:
            self.assertEqual(bank.dataset, consensus_dataset,
                             f"Honest bank {bank.id} does not agree with consensus in configuration 2")

    def test_output_types(self):
        # Verify that the simulation produces objects with expected attributes and correct data types.
        num_banks = 8
        byzantine_count = 2
        banks = simulate_protocol(num_banks, byzantine_count)
        for bank in banks:
            # Each bank should have an id that is an integer or string.
            self.assertTrue(hasattr(bank, 'id'), "Bank object missing 'id' attribute")
            self.assertTrue(isinstance(bank.id, (int, str)), "'id' attribute must be int or str")
            
            # Each bank should have an 'is_byzantine' attribute of type bool.
            self.assertTrue(hasattr(bank, 'is_byzantine'), "Bank object missing 'is_byzantine' attribute")
            self.assertIsInstance(bank.is_byzantine, bool, "'is_byzantine' attribute must be boolean")
            
            # Each bank must have a 'dataset' attribute. For testing purposes assume dataset is a list.
            self.assertTrue(hasattr(bank, 'dataset'), "Bank object missing 'dataset' attribute")
            self.assertIsInstance(bank.dataset, list, "'dataset' attribute must be a list")

if __name__ == "__main__":
    unittest.main()