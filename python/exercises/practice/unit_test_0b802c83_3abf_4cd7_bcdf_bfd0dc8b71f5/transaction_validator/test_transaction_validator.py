import unittest

from transaction_validator import validate_transaction

class TestTransactionValidator(unittest.TestCase):
    def test_valid_transaction_basic(self):
        service_state = {
            "service_A": {"item1": 10, "item2": 20},
            "service_B": {"item3": 30, "item4": 40},
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 10},
            {"service_id": "service_B", "operation_type": "delete", "data_id": "item3", "expected_value": 30},
            {"service_id": "service_C", "operation_type": "create", "data_id": "item5", "new_value": 50}
        ]
        self.assertTrue(validate_transaction(service_state, transaction_log))

    def test_invalid_expected_value(self):
        service_state = {
            "service_A": {"item1": 10, "item2": 20}
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 12}
        ]
        self.assertFalse(validate_transaction(service_state, transaction_log))

    def test_create_existing_item(self):
        service_state = {
            "service_A": {"item1": 10}
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "create", "data_id": "item1", "new_value": 20}
        ]
        self.assertFalse(validate_transaction(service_state, transaction_log))

    def test_delete_nonexistent_item(self):
        service_state = {
            "service_A": {"item1": 10}
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "delete", "data_id": "item2", "expected_value": 20}
        ]
        self.assertFalse(validate_transaction(service_state, transaction_log))

    def test_complex_valid_transaction(self):
        service_state = {
            "service_A": {"item1": 10, "item2": 20},
            "service_B": {"item3": 30}
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 10},
            {"service_id": "service_B", "operation_type": "delete", "data_id": "item3", "expected_value": 30},
            {"service_id": "service_A", "operation_type": "create", "data_id": "item4", "new_value": 40},
            {"service_id": "service_C", "operation_type": "create", "data_id": "item5", "new_value": 50}
        ]
        self.assertTrue(validate_transaction(service_state, transaction_log))

    def test_sequential_dependencies(self):
        service_state = {
            "service_A": {"item1": 10}
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 10},
            {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 20, "expected_value": 15}
        ]
        self.assertTrue(validate_transaction(service_state, transaction_log))

    def test_empty_transaction_log(self):
        service_state = {
            "service_A": {"item1": 10}
        }
        transaction_log = []
        self.assertTrue(validate_transaction(service_state, transaction_log))

    def test_empty_service_state(self):
        service_state = {}
        transaction_log = [
            {"service_id": "service_A", "operation_type": "create", "data_id": "item1", "new_value": 10}
        ]
        self.assertTrue(validate_transaction(service_state, transaction_log))

    def test_invalid_operation_sequence(self):
        service_state = {
            "service_A": {"item1": 10}
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "delete", "data_id": "item1", "expected_value": 10},
            {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 20, "expected_value": 10}
        ]
        self.assertFalse(validate_transaction(service_state, transaction_log))

    def test_multiple_services_interaction(self):
        service_state = {
            "service_A": {"item1": 10},
            "service_B": {"item2": 20},
            "service_C": {"item3": 30}
        }
        transaction_log = [
            {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 10},
            {"service_id": "service_B", "operation_type": "delete", "data_id": "item2", "expected_value": 20},
            {"service_id": "service_C", "operation_type": "update", "data_id": "item3", "new_value": 35, "expected_value": 30},
            {"service_id": "service_B", "operation_type": "create", "data_id": "item4", "new_value": 40}
        ]
        self.assertTrue(validate_transaction(service_state, transaction_log))

if __name__ == '__main__':
    unittest.main()