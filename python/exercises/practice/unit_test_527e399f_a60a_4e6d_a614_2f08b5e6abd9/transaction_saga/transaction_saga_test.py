import unittest
from transaction_saga import coordinate_transaction
import random

class TestTransactionSaga(unittest.TestCase):
    def setUp(self):
        # Make tests deterministic by setting seed
        random.seed(42)

    def test_all_services_succeed(self):
        # All services succeed
        services = {
            0: [lambda data: True, lambda data: True],
            1: [lambda data: True, lambda data: True],
        }
        transaction = [(0, "create user"), (1, "create account")]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertTrue(success)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - success")
        self.assertEqual(logs[1], "perform: service_1 with data 'create account' - success")
    
    def test_second_service_fails_compensation_succeeds(self):
        # Second service fails, compensation succeeds
        services = {
            0: [lambda data: True, lambda data: True], 
            1: [lambda data: False, lambda data: True],
        }
        transaction = [(0, "create user"), (1, "create account")]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertFalse(success)
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - success")
        self.assertEqual(logs[1], "perform: service_1 with data 'create account' - failure")
        self.assertEqual(logs[2], "compensate: service_0 with data 'create user' - success")
    
    def test_compensation_fails(self):
        # Second service fails, compensation also fails
        services = {
            0: [lambda data: True, lambda data: False], 
            1: [lambda data: False, lambda data: True],
        }
        transaction = [(0, "create user"), (1, "create account")]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertFalse(success)
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - success")
        self.assertEqual(logs[1], "perform: service_1 with data 'create account' - failure")
        self.assertEqual(logs[2], "compensate: service_0 with data 'create user' - failure")
    
    def test_first_service_fails_no_compensation_needed(self):
        # First service fails, no compensation needed
        services = {
            0: [lambda data: False, lambda data: True], 
            1: [lambda data: True, lambda data: True],
        }
        transaction = [(0, "create user"), (1, "create account")]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertFalse(success)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - failure")
    
    def test_multiple_services_success(self):
        # Multiple services all succeed
        services = {
            0: [lambda data: True, lambda data: True],
            1: [lambda data: True, lambda data: True],
            2: [lambda data: True, lambda data: True],
            3: [lambda data: True, lambda data: True],
        }
        transaction = [
            (0, "create user"), 
            (1, "create account"),
            (2, "create order"),
            (3, "process payment")
        ]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertTrue(success)
        self.assertEqual(len(logs), 4)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - success")
        self.assertEqual(logs[1], "perform: service_1 with data 'create account' - success")
        self.assertEqual(logs[2], "perform: service_2 with data 'create order' - success")
        self.assertEqual(logs[3], "perform: service_3 with data 'process payment' - success")
    
    def test_multiple_services_failure_in_middle(self):
        # Multiple services with failure in the middle
        services = {
            0: [lambda data: True, lambda data: True],
            1: [lambda data: True, lambda data: True],
            2: [lambda data: False, lambda data: True],
            3: [lambda data: True, lambda data: True],
        }
        transaction = [
            (0, "create user"), 
            (1, "create account"),
            (2, "create order"),
            (3, "process payment")
        ]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertFalse(success)
        self.assertEqual(len(logs), 5)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - success")
        self.assertEqual(logs[1], "perform: service_1 with data 'create account' - success")
        self.assertEqual(logs[2], "perform: service_2 with data 'create order' - failure")
        self.assertEqual(logs[3], "compensate: service_1 with data 'create account' - success")
        self.assertEqual(logs[4], "compensate: service_0 with data 'create user' - success")
    
    def test_multiple_compensation_failures(self):
        # Multiple services with failure in the middle and compensations also failing
        services = {
            0: [lambda data: True, lambda data: False],
            1: [lambda data: True, lambda data: False],
            2: [lambda data: False, lambda data: True],
            3: [lambda data: True, lambda data: True],
        }
        transaction = [
            (0, "create user"), 
            (1, "create account"),
            (2, "create order"),
            (3, "process payment")
        ]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertFalse(success)
        self.assertEqual(len(logs), 5)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - success")
        self.assertEqual(logs[1], "perform: service_1 with data 'create account' - success")
        self.assertEqual(logs[2], "perform: service_2 with data 'create order' - failure")
        self.assertEqual(logs[3], "compensate: service_1 with data 'create account' - failure")
        self.assertEqual(logs[4], "compensate: service_0 with data 'create user' - failure")
    
    def test_empty_transaction(self):
        # Empty transaction
        services = {
            0: [lambda data: True, lambda data: True],
            1: [lambda data: True, lambda data: True],
        }
        transaction = []
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertTrue(success)
        self.assertEqual(logs, [])
    
    def test_same_service_multiple_calls(self):
        # Same service called multiple times with different data
        services = {
            0: [lambda data: True, lambda data: True],
            1: [lambda data: "order" in data, lambda data: True],  # Succeeds only if "order" in data
        }
        transaction = [
            (0, "create user"),
            (1, "create order"),  # This will succeed
            (1, "delete user"),   # This will fail
            (0, "update profile")
        ]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertFalse(success)
        self.assertEqual(len(logs), 5)
        self.assertEqual(logs[0], "perform: service_0 with data 'create user' - success")
        self.assertEqual(logs[1], "perform: service_1 with data 'create order' - success")
        self.assertEqual(logs[2], "perform: service_1 with data 'delete user' - failure")
        self.assertEqual(logs[3], "compensate: service_1 with data 'create order' - success")
        self.assertEqual(logs[4], "compensate: service_0 with data 'create user' - success")
    
    def test_random_failures_with_seed(self):
        # Testing with services that may randomly fail
        random.seed(12345)  # Set seed for deterministic random failures
        
        def random_perform(data):
            return random.random() >= 0.2  # 20% chance of failure
            
        def random_compensate(data):
            return random.random() >= 0.2  # 20% chance of failure
            
        services = {
            0: [random_perform, random_compensate],
            1: [random_perform, random_compensate],
            2: [random_perform, random_compensate],
        }
        
        transaction = [
            (0, "operation A"),
            (1, "operation B"),
            (2, "operation C")
        ]
        
        success, logs = coordinate_transaction(services, transaction)
        
        # With the given seed, we expect certain behavior
        # The exact expectations depend on the random numbers generated
        self.assertEqual(len(logs) > 0, True)
    
    def test_with_empty_data(self):
        # Test with empty strings as data
        services = {
            0: [lambda data: True, lambda data: True],
            1: [lambda data: len(data) > 0, lambda data: True],  # Fails on empty data
        }
        
        transaction = [
            (0, "data"),
            (1, "")  # Empty data will make service 1 fail
        ]
        
        success, logs = coordinate_transaction(services, transaction)
        
        self.assertFalse(success)
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0], "perform: service_0 with data 'data' - success")
        self.assertEqual(logs[1], "perform: service_1 with data '' - failure")
        self.assertEqual(logs[2], "compensate: service_0 with data 'data' - success")

if __name__ == "__main__":
    unittest.main()