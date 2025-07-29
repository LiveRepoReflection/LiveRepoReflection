import unittest
import uuid
from dtc_conflicts import DistributedTransactionCoordinator, Service, Transaction
from dtc_conflicts import TransactionState, ConflictError

class TestDtcCoordinator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures, if any."""
        self.dtc = DistributedTransactionCoordinator()
        # Create some services
        for i in range(1, 4):
            self.dtc.add_service(i)

    def test_basic_transaction(self):
        """Test a simple transaction that should succeed."""
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        self.dtc.write(txn_id, 1, "item1", "value1")
        status = self.dtc.commit(txn_id)
        self.assertEqual(status, "SUCCESS")
        
        # Verify the data was written
        txn_id2 = str(uuid.uuid4())
        self.dtc.begin(txn_id2)
        value = self.dtc.read(txn_id2, 1, "item1")
        self.assertEqual(value, "value1")

    def test_rollback_transaction(self):
        """Test rolling back a transaction."""
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        self.dtc.write(txn_id, 1, "item1", "value1")
        self.dtc.rollback(txn_id)
        
        # Verify the data was not written
        txn_id2 = str(uuid.uuid4())
        self.dtc.begin(txn_id2)
        value = self.dtc.read(txn_id2, 1, "item1")
        self.assertIsNone(value)

    def test_conflict_detection(self):
        """Test conflict detection between two transactions."""
        # Start first transaction
        txn_id1 = str(uuid.uuid4())
        self.dtc.begin(txn_id1)
        self.dtc.write(txn_id1, 1, "item1", "value1")
        
        # Start second transaction
        txn_id2 = str(uuid.uuid4())
        self.dtc.begin(txn_id2)
        self.dtc.read(txn_id2, 1, "item1")  # Read should succeed
        
        # First transaction commits successfully
        status1 = self.dtc.commit(txn_id1)
        self.assertEqual(status1, "SUCCESS")
        
        # Second transaction tries to write to the same item that was modified
        self.dtc.write(txn_id2, 1, "item1", "value2")
        status2 = self.dtc.commit(txn_id2)
        self.assertEqual(status2, "ABORTED")

    def test_multiple_services_transaction(self):
        """Test a transaction across multiple services."""
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        self.dtc.write(txn_id, 1, "item1", "value1")
        self.dtc.write(txn_id, 2, "item2", "value2")
        self.dtc.write(txn_id, 3, "item3", "value3")
        status = self.dtc.commit(txn_id)
        self.assertEqual(status, "SUCCESS")
        
        # Verify the data was written in all services
        txn_id2 = str(uuid.uuid4())
        self.dtc.begin(txn_id2)
        value1 = self.dtc.read(txn_id2, 1, "item1")
        value2 = self.dtc.read(txn_id2, 2, "item2")
        value3 = self.dtc.read(txn_id2, 3, "item3")
        self.assertEqual(value1, "value1")
        self.assertEqual(value2, "value2")
        self.assertEqual(value3, "value3")

    def test_service_not_found(self):
        """Test handling of non-existent service."""
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        with self.assertRaises(ValueError):
            self.dtc.read(txn_id, 999, "item1")

    def test_transaction_not_found(self):
        """Test handling of non-existent transaction."""
        with self.assertRaises(ValueError):
            self.dtc.read("nonexistent_txn", 1, "item1")

    def test_concurrent_transactions_no_conflict(self):
        """Test concurrent transactions with no conflicts."""
        txn_id1 = str(uuid.uuid4())
        txn_id2 = str(uuid.uuid4())
        
        self.dtc.begin(txn_id1)
        self.dtc.begin(txn_id2)
        
        # Transaction 1 writes to item1, Transaction 2 writes to item2
        self.dtc.write(txn_id1, 1, "item1", "value1")
        self.dtc.write(txn_id2, 1, "item2", "value2")
        
        status1 = self.dtc.commit(txn_id1)
        status2 = self.dtc.commit(txn_id2)
        
        self.assertEqual(status1, "SUCCESS")
        self.assertEqual(status2, "SUCCESS")
        
        # Verify both items
        txn_id3 = str(uuid.uuid4())
        self.dtc.begin(txn_id3)
        value1 = self.dtc.read(txn_id3, 1, "item1")
        value2 = self.dtc.read(txn_id3, 1, "item2")
        self.assertEqual(value1, "value1")
        self.assertEqual(value2, "value2")

    def test_complex_conflict_scenario(self):
        """Test a more complex conflict scenario with multiple transactions."""
        # Transaction 1: Read and write to items in different services
        txn_id1 = str(uuid.uuid4())
        self.dtc.begin(txn_id1)
        self.dtc.write(txn_id1, 1, "item1", "txn1_value1")
        self.dtc.write(txn_id1, 2, "item2", "txn1_value2")
        
        # Transaction 2: Read and write to some of the same items
        txn_id2 = str(uuid.uuid4())
        self.dtc.begin(txn_id2)
        self.dtc.write(txn_id2, 1, "item1", "txn2_value1")  # Conflicts with txn1
        self.dtc.write(txn_id2, 3, "item3", "txn2_value3")  # No conflict
        
        # Transaction 3: Read and write to different items
        txn_id3 = str(uuid.uuid4())
        self.dtc.begin(txn_id3)
        self.dtc.write(txn_id3, 2, "item4", "txn3_value4")
        self.dtc.write(txn_id3, 3, "item5", "txn3_value5")
        
        # Commit transactions in specific order
        status1 = self.dtc.commit(txn_id1)
        status2 = self.dtc.commit(txn_id2)
        status3 = self.dtc.commit(txn_id3)
        
        # Transaction 1 should succeed
        self.assertEqual(status1, "SUCCESS")
        # Transaction 2 should be aborted due to conflict with transaction 1
        self.assertEqual(status2, "ABORTED")
        # Transaction 3 should succeed as it doesn't conflict with committed transactions
        self.assertEqual(status3, "SUCCESS")
        
        # Verify final state
        txn_id4 = str(uuid.uuid4())
        self.dtc.begin(txn_id4)
        value1 = self.dtc.read(txn_id4, 1, "item1")
        value2 = self.dtc.read(txn_id4, 2, "item2")
        value3 = self.dtc.read(txn_id4, 3, "item3")
        value4 = self.dtc.read(txn_id4, 2, "item4")
        value5 = self.dtc.read(txn_id4, 3, "item5")
        
        self.assertEqual(value1, "txn1_value1")  # From transaction 1
        self.assertEqual(value2, "txn1_value2")  # From transaction 1
        self.assertIsNone(value3)  # Transaction 2 was aborted
        self.assertEqual(value4, "txn3_value4")  # From transaction 3
        self.assertEqual(value5, "txn3_value5")  # From transaction 3

    def test_command_interface(self):
        """Test the command interface for the DTC."""
        commands = [
            "BEGIN tx1",
            "READ tx1 1 item1",
            "WRITE tx1 1 item1 value1",
            "COMMIT tx1"
        ]
        
        outputs = []
        for cmd in commands:
            output = self.dtc.process_command(cmd)
            if output:
                outputs.append(output)
        
        self.assertEqual(outputs, ["COMMIT tx1 SUCCESS"])
        
        # Test with a conflict
        commands_conflict = [
            "BEGIN tx2",
            "READ tx2 1 item1",
            "WRITE tx2 1 item1 value1_modified",
            "BEGIN tx3",
            "WRITE tx3 1 item1 value1_from_tx3",
            "COMMIT tx3",
            "COMMIT tx2"
        ]
        
        outputs_conflict = []
        for cmd in commands_conflict:
            output = self.dtc.process_command(cmd)
            if output:
                outputs_conflict.append(output)
        
        self.assertIn("COMMIT tx3 SUCCESS", outputs_conflict)
        self.assertIn("COMMIT tx2 ABORTED", outputs_conflict)

    def test_read_isolation(self):
        """Test transaction isolation for reads."""
        # Start and write in transaction 1
        txn_id1 = str(uuid.uuid4())
        self.dtc.begin(txn_id1)
        self.dtc.write(txn_id1, 1, "item1", "initial_value")
        self.dtc.commit(txn_id1)
        
        # Start transaction 2 and read
        txn_id2 = str(uuid.uuid4())
        self.dtc.begin(txn_id2)
        value2 = self.dtc.read(txn_id2, 1, "item1")
        self.assertEqual(value2, "initial_value")
        
        # Start and write in transaction 3
        txn_id3 = str(uuid.uuid4())
        self.dtc.begin(txn_id3)
        self.dtc.write(txn_id3, 1, "item1", "new_value")
        self.dtc.commit(txn_id3)
        
        # Transaction 2 should still see the original value
        value2_again = self.dtc.read(txn_id2, 1, "item1")
        self.assertEqual(value2_again, "initial_value")
        
        # But trying to write now should fail on commit due to version mismatch
        self.dtc.write(txn_id2, 1, "item1", "attempted_value")
        status2 = self.dtc.commit(txn_id2)
        self.assertEqual(status2, "ABORTED")
        
        # Verify the final value
        txn_id4 = str(uuid.uuid4())
        self.dtc.begin(txn_id4)
        final_value = self.dtc.read(txn_id4, 1, "item1")
        self.assertEqual(final_value, "new_value")

    def test_large_batch_of_transactions(self):
        """Test handling a large batch of transactions."""
        # Create a bunch of transactions
        for i in range(100):
            txn_id = f"batch_txn_{i}"
            self.dtc.begin(txn_id)
            self.dtc.write(txn_id, 1, f"batch_item_{i}", f"batch_value_{i}")
            status = self.dtc.commit(txn_id)
            self.assertEqual(status, "SUCCESS")
        
        # Verify some random values
        verify_txn = str(uuid.uuid4())
        self.dtc.begin(verify_txn)
        for i in [0, 25, 50, 75, 99]:
            value = self.dtc.read(verify_txn, 1, f"batch_item_{i}")
            self.assertEqual(value, f"batch_value_{i}")

    def test_error_handling(self):
        """Test various error handling scenarios."""
        # Test invalid service
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        with self.assertRaises(ValueError):
            self.dtc.read(txn_id, 999, "item")
        
        # Test invalid transaction ID
        with self.assertRaises(ValueError):
            self.dtc.read("invalid_txn", 1, "item")
        
        # Test commit of already committed transaction
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        self.dtc.write(txn_id, 1, "item", "value")
        self.dtc.commit(txn_id)
        with self.assertRaises(ValueError):
            self.dtc.commit(txn_id)
        
        # Test rollback of already rolled back transaction
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        self.dtc.rollback(txn_id)
        with self.assertRaises(ValueError):
            self.dtc.rollback(txn_id)
            
        # Test operation on committed transaction
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        self.dtc.commit(txn_id)
        with self.assertRaises(ValueError):
            self.dtc.write(txn_id, 1, "item", "value")
            
        # Test operation on rolled back transaction
        txn_id = str(uuid.uuid4())
        self.dtc.begin(txn_id)
        self.dtc.rollback(txn_id)
        with self.assertRaises(ValueError):
            self.dtc.read(txn_id, 1, "item")

if __name__ == '__main__':
    unittest.main()