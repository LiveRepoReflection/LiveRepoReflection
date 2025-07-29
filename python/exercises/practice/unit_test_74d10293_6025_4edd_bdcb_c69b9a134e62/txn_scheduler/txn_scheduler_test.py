import unittest
from collections import defaultdict
from itertools import chain

# Import the required functions and classes from the txn_scheduler module
from txn_scheduler import schedule_transactions, Transaction, Operation, Shard

class TxnSchedulerTest(unittest.TestCase):

    def setUp(self):
        # Helper to reset transaction operation pointers for matching scheduled operations later
        self.txn_op_indices = {}

    def map_scheduled_ops(self, transactions, schedule):
        """
        Given the list of transactions and the schedule (list of tuples), reconstruct
        a mapping from each scheduled tuple to the corresponding Operation. This function
        assumes that operations in each transaction are scheduled in the order they appear.
        Returns a list of dictionaries with keys: 'timestamp', 'transaction_id', 'shard_id',
        'estimated_duration' (finish time can be computed), and the original operation.
        """
        # Build mapping from transaction id to list of operations (in order)
        txn_ops = {}
        for txn in transactions:
            txn_ops[txn.id] = list(txn.operations)
            self.txn_op_indices[txn.id] = 0

        scheduled_details = []
        for entry in schedule:
            timestamp, txn_id, shard_id = entry
            # Check that the transaction has remaining operations
            if self.txn_op_indices[txn_id] >= len(txn_ops[txn_id]):
                self.fail(f"More scheduled operations than available in transaction {txn_id}")
            op = txn_ops[txn_id][self.txn_op_indices[txn_id]]
            # Validate that the shard_id matches the operation's shard_id
            if op.shard_id != shard_id:
                self.fail(f"Scheduled shard_id {shard_id} does not match operation shard_id {op.shard_id} for transaction {txn_id}")
            scheduled_details.append({
                'timestamp': timestamp,
                'finish_time': timestamp + op.estimated_duration,
                'transaction_id': txn_id,
                'shard_id': shard_id,
                'operation': op
            })
            self.txn_op_indices[txn_id] += 1
        return scheduled_details

    def test_schedule_sort_order(self):
        # Transactions with operations on different shards and no conflicts.
        transactions = [
            Transaction(id=1, operations=[
                Operation(type="READ", key="A", shard_id=1, estimated_duration=10, transaction_id=1),
                Operation(type="WRITE", key="B", shard_id=2, estimated_duration=5, transaction_id=1)
            ]),
            Transaction(id=2, operations=[
                Operation(type="WRITE", key="C", shard_id=3, estimated_duration=8, transaction_id=2)
            ])
        ]
        shard_map = {
            1: Shard(processing_capacity=2),
            2: Shard(processing_capacity=2),
            3: Shard(processing_capacity=1)
        }
        schedule = schedule_transactions(transactions, shard_map)
        
        # Check that the schedule is sorted by timestamp (non-decreasing)
        timestamps = [entry[0] for entry in schedule]
        self.assertEqual(timestamps, sorted(timestamps), "Schedule is not sorted by timestamp")
        
        # Check that all operations are scheduled (if no transaction is aborted, they all should be scheduled)
        expected_ops = sum(len(txn.operations) for txn in transactions)
        self.assertEqual(len(schedule), expected_ops, "Not all operations are scheduled when expected")
        
        # Match scheduled operations to original transactions to validate shard_ids
        self.map_scheduled_ops(transactions, schedule)

    def test_operation_order_within_transaction(self):
        # A transaction with multiple operations; ensure that scheduling respects order.
        transactions = [
            Transaction(id=1, operations=[
                Operation(type="WRITE", key="X", shard_id=1, estimated_duration=10, transaction_id=1),
                Operation(type="READ", key="Y", shard_id=1, estimated_duration=15, transaction_id=1),
                Operation(type="WRITE", key="Z", shard_id=2, estimated_duration=20, transaction_id=1)
            ])
        ]
        shard_map = {
            1: Shard(processing_capacity=1),
            2: Shard(processing_capacity=1)
        }
        schedule = schedule_transactions(transactions, shard_map)
        scheduled_details = self.map_scheduled_ops(transactions, schedule)
        
        # Extract all scheduled start times for transaction 1 in order of appearance
        txn_times = [detail['timestamp'] for detail in scheduled_details if detail['transaction_id'] == 1]
        # Ensure non-decreasing order of timestamps
        self.assertEqual(txn_times, sorted(txn_times), "Operations within a transaction are not scheduled in order")

    def test_shard_capacity_constraints(self):
        # Create transactions with operations destined for the same shard.
        transactions = [
            Transaction(id=1, operations=[
                Operation(type="WRITE", key="A", shard_id=1, estimated_duration=50, transaction_id=1)
            ]),
            Transaction(id=2, operations=[
                Operation(type="READ", key="A", shard_id=1, estimated_duration=30, transaction_id=2)
            ]),
            Transaction(id=3, operations=[
                Operation(type="WRITE", key="B", shard_id=1, estimated_duration=20, transaction_id=3)
            ])
        ]
        # Shard capacity exactly 2; so at no point, more than 2 operations should run concurrently on shard 1.
        shard_map = {1: Shard(processing_capacity=2)}
        schedule = schedule_transactions(transactions, shard_map)
        scheduled_details = self.map_scheduled_ops(transactions, schedule)
        
        # Build events for shard 1.
        events = []
        for detail in scheduled_details:
            if detail['shard_id'] == 1:
                events.append((detail['timestamp'], +1))
                events.append((detail['finish_time'], -1))
        # Sort events by time; if same timestamp, finishing events come before starting events.
        events.sort(key=lambda x: (x[0], x[1]))
        
        concurrent = 0
        for time, delta in events:
            concurrent += delta
            self.assertLessEqual(concurrent, shard_map[1].processing_capacity, 
                f"Shard capacity exceeded at time {time}: {concurrent} concurrent operations")

    def test_conflict_serializability(self):
        # Create transactions with conflicting operations on the same key and shard.
        # This scenario can potentially cause a cycle. The scheduler should break cycles by aborting one transaction.
        transactions = [
            Transaction(id=1, operations=[
                Operation(type="WRITE", key="X", shard_id=1, estimated_duration=10, transaction_id=1),
                Operation(type="READ", key="Y", shard_id=2, estimated_duration=10, transaction_id=1)
            ]),
            Transaction(id=2, operations=[
                Operation(type="READ", key="X", shard_id=1, estimated_duration=5, transaction_id=2),
                Operation(type="WRITE", key="Y", shard_id=2, estimated_duration=15, transaction_id=2)
            ]),
            Transaction(id=3, operations=[
                Operation(type="WRITE", key="Y", shard_id=2, estimated_duration=20, transaction_id=3),
                Operation(type="READ", key="X", shard_id=1, estimated_duration=10, transaction_id=3)
            ])
        ]
        shard_map = {
            1: Shard(processing_capacity=2),
            2: Shard(processing_capacity=2)
        }
        schedule = schedule_transactions(transactions, shard_map)
        scheduled_details = self.map_scheduled_ops(transactions, schedule)
        
        # For serializability, for each key with conflicting operations (where at least one is WRITE),
        # operations from different transactions should not be interleaved.
        key_to_txn_times = defaultdict(lambda: defaultdict(list))
        for detail in scheduled_details:
            op = detail['operation']
            # Considering keys where operation type is WRITE or conflict might occur.
            if op.type in ("WRITE", "READ"):
                key_to_txn_times[op.key][detail['transaction_id']].append(detail['timestamp'])
        
        for key, txn_dict in key_to_txn_times.items():
            # Only check if multiple transactions access the key.
            if len(txn_dict) > 1:
                txn_time_boundaries = {}
                for txn_id, times in txn_dict.items():
                    txn_time_boundaries[txn_id] = (min(times), max(times))
                txn_ids = list(txn_time_boundaries.keys())
                for i in range(len(txn_ids)):
                    for j in range(i + 1, len(txn_ids)):
                        tid1, tid2 = txn_ids[i], txn_ids[j]
                        start1, end1 = txn_time_boundaries[tid1]
                        start2, end2 = txn_time_boundaries[tid2]
                        # Check that operations for one transaction come entirely before the other's.
                        no_interleaving = (end1 <= start2) or (end2 <= start1)
                        self.assertTrue(no_interleaving, 
                            f"Conflict on key '{key}' between transactions {tid1} and {tid2} is interleaved, violating serializability")

    def test_total_operations_scheduled(self):
        # Test that when there are no conflicts the scheduler schedules all operations.
        transactions = [
            Transaction(id=1, operations=[
                Operation(type="READ", key="M", shard_id=1, estimated_duration=12, transaction_id=1),
                Operation(type="WRITE", key="N", shard_id=2, estimated_duration=8, transaction_id=1),
            ]),
            Transaction(id=2, operations=[
                Operation(type="WRITE", key="O", shard_id=3, estimated_duration=7, transaction_id=2)
            ]),
            Transaction(id=3, operations=[
                Operation(type="READ", key="P", shard_id=2, estimated_duration=15, transaction_id=3),
                Operation(type="READ", key="Q", shard_id=3, estimated_duration=9, transaction_id=3)
            ])
        ]
        shard_map = {
            1: Shard(processing_capacity=1),
            2: Shard(processing_capacity=2),
            3: Shard(processing_capacity=2)
        }
        schedule = schedule_transactions(transactions, shard_map)
        # In case a transaction is aborted due to conflict detection, the total operations scheduled
        # would be less than the sum of all operations.
        total_requested = sum(len(txn.operations) for txn in transactions)
        self.assertLessEqual(len(schedule), total_requested, "More operations scheduled than requested")
        # If no conflicts, all operations should be scheduled.
        # For this test input there's no conflict.
        self.assertEqual(len(schedule), total_requested, "Not all operations were scheduled when no conflicts exist")

if __name__ == '__main__':
    unittest.main()