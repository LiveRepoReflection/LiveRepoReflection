import unittest
from dtm_system import DTM

class TestDTMSystem(unittest.TestCase):
    def setUp(self):
        # Create a new instance of DTM before each test
        self.dtm = DTM()
        # Register two services with different validation rules.
        # One service accepts only integers.
        # The other service accepts only strings of length between 5 and 10.
        self.dtm.register_service("int_service")
        self.dtm.register_service("str_service")
        # Assume that when a service is registered, the DTM internally attaches a validation function.
        # For testing purposes, we assume that each service can be accessed and modified via
        # a public attribute 'validation' and 'available'. This is to simulate behavior in tests.
        # Set default availability to True.
        self.dtm.get_service_data("int_service")  # Force creation if needed.
        self.dtm.get_service_data("str_service")
        # For testing, we monkey-patch the internal service objects to add attributes for simulation.
        # Assume that DTM instance has an attribute _services which is a dict mapping service names
        # to service objects that have 'validate_update' and 'available' attributes.
        self.dtm._services["int_service"].validate_update = self.validate_update_int_only
        self.dtm._services["int_service"].available = True
        self.dtm._services["str_service"].validate_update = self.validate_update_length_limit
        self.dtm._services["str_service"].available = True

    # Validation function for int_service: accepts only integers.
    def validate_update_int_only(self, key, new_value):
        if not self.dtm._services["int_service"].available:
            return False
        return isinstance(new_value, int)

    # Validation function for str_service: accepts only strings with length in [5, 10].
    def validate_update_length_limit(self, key, new_value):
        if not self.dtm._services["str_service"].available:
            return False
        if not isinstance(new_value, str):
            return False
        return 5 <= len(new_value) <= 10

    def test_register_duplicate_service(self):
        # Attempt to register a service with a name that already exists.
        with self.assertRaises(ValueError):
            self.dtm.register_service("int_service")

    def test_unregistered_service_in_transaction(self):
        # Prepare a transaction that refers to an unregistered service.
        txn_id = self.dtm.begin_transaction()
        operations = {
            "nonexistent_service": {"key1": 100}
        }
        with self.assertRaises(ValueError):
            self.dtm.prepare_transaction(txn_id, operations)

    def test_transaction_commit(self):
        # Create a transaction with valid operations for both services.
        txn_id = self.dtm.begin_transaction()
        operations = {
            "int_service": {"num": 42},
            "str_service": {"text": "welcome"}
        }
        prepare_result = self.dtm.prepare_transaction(txn_id, operations)
        self.assertTrue(prepare_result, "Transaction should be prepared successfully.")
        # Commit the transaction.
        self.dtm.commit_transaction(txn_id)
        # Verify that the services' data have been updated.
        int_data = self.dtm.get_service_data("int_service")
        str_data = self.dtm.get_service_data("str_service")
        self.assertIn("num", int_data)
        self.assertEqual(int_data["num"], 42)
        self.assertIn("text", str_data)
        self.assertEqual(str_data["text"], "welcome")

    def test_transaction_rollback_due_to_validation_failure(self):
        # Create a transaction with an invalid update for int_service (non-integer value).
        txn_id = self.dtm.begin_transaction()
        operations = {
            "int_service": {"num": "not an int"},  # Invalid update for int_service.
            "str_service": {"text": "hello"}  # This update is borderline invalid since length 5.
        }
        prepare_result = self.dtm.prepare_transaction(txn_id, operations)
        self.assertFalse(prepare_result, "Transaction should fail preparation due to invalid int update.")
        # Rollback the transaction.
        self.dtm.rollback_transaction(txn_id)
        # Verify that no changes have been applied.
        int_data = self.dtm.get_service_data("int_service")
        str_data = self.dtm.get_service_data("str_service")
        self.assertNotIn("num", int_data)
        self.assertNotIn("text", str_data)

    def test_transaction_rollback_due_to_service_unavailability(self):
        # Simulate unavailability of str_service.
        self.dtm._services["str_service"].available = False
        # Create a transaction with valid formatted values.
        txn_id = self.dtm.begin_transaction()
        operations = {
            "int_service": {"num": 100},
            "str_service": {"text": "consistent"}  # Although valid string, service is unavailable.
        }
        prepare_result = self.dtm.prepare_transaction(txn_id, operations)
        self.assertFalse(prepare_result, "Transaction should fail due to service unavailability.")
        # Rollback the transaction.
        self.dtm.rollback_transaction(txn_id)
        # Verify that no changes have been applied.
        int_data = self.dtm.get_service_data("int_service")
        str_data = self.dtm.get_service_data("str_service")
        self.assertNotIn("num", int_data)
        self.assertNotIn("text", str_data)
        # Restore availability for further tests.
        self.dtm._services["str_service"].available = True

    def test_multiple_operations_in_one_transaction(self):
        # Create a transaction that updates multiple keys on the same service.
        txn_id = self.dtm.begin_transaction()
        operations = {
            "int_service": {"a": 1, "b": 2, "c": 3},
            "str_service": {"first": "python", "second": "unittest"}  # "unittest" length is 8.
        }
        prepare_result = self.dtm.prepare_transaction(txn_id, operations)
        self.assertTrue(prepare_result, "Multiple operations should be prepared successfully.")
        self.dtm.commit_transaction(txn_id)
        int_data = self.dtm.get_service_data("int_service")
        str_data = self.dtm.get_service_data("str_service")
        self.assertEqual(int_data.get("a"), 1)
        self.assertEqual(int_data.get("b"), 2)
        self.assertEqual(int_data.get("c"), 3)
        self.assertEqual(str_data.get("first"), "python")
        self.assertEqual(str_data.get("second"), "unittest")

    def test_prepare_after_commit_has_no_effect(self):
        # Test that after a successful commit, further attempts to commit or rollback the same transaction have no effect.
        txn_id = self.dtm.begin_transaction()
        operations = {
            "int_service": {"num": 55}
        }
        prepare_result = self.dtm.prepare_transaction(txn_id, operations)
        self.assertTrue(prepare_result, "Preparation should succeed.")
        # Commit the transaction.
        self.dtm.commit_transaction(txn_id)
        int_data_before = self.dtm.get_service_data("int_service")
        # Now attempt to commit again, expecting no changes or errors.
        self.dtm.commit_transaction(txn_id)
        int_data_after = self.dtm.get_service_data("int_service")
        self.assertEqual(int_data_before, int_data_after)
        # Similarly, trying to rollback should not revert the change.
        self.dtm.rollback_transaction(txn_id)
        int_data_final = self.dtm.get_service_data("int_service")
        self.assertEqual(int_data_after, int_data_final)

if __name__ == '__main__':
    unittest.main()