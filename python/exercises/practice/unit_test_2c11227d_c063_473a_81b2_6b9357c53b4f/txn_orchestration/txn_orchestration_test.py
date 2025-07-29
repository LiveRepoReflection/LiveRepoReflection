import unittest
import asyncio
import uuid

from txn_orchestration import orchestrate_transaction

class TestTxnOrchestration(unittest.TestCase):
    def setUp(self):
        # Define dummy asynchronous service operation and compensation functions.
        async def op_success(transaction_id, payload):
            await asyncio.sleep(0.1)
            return True

        async def op_failure(transaction_id, payload):
            await asyncio.sleep(0.1)
            return False

        async def comp_success(transaction_id, payload):
            await asyncio.sleep(0.05)
            return True

        async def comp_failure(transaction_id, payload):
            await asyncio.sleep(0.05)
            return False

        # Services dictionaries for testing successful operations.
        self.services_success = {
            "AccountService": {"debit": op_success},
            "FraudDetectionService": {"verify": op_success},
            "NotificationService": {"notify": op_success}
        }
        self.compensations_success = {
            "AccountService": {"debit": comp_success},
            "FraudDetectionService": {"verify": comp_success},
            "NotificationService": {"notify": comp_success}
        }

        # Services dictionaries where a middle operation fails.
        self.services_failure = {
            "AccountService": {"debit": op_success},
            "FraudDetectionService": {"verify": op_failure},
            "NotificationService": {"notify": op_success}
        }
        self.compensations_mixed = {
            "AccountService": {"debit": comp_success},
            "FraudDetectionService": {"verify": comp_success},
            "NotificationService": {"notify": comp_success}
        }

        # Define a linear graph (dependency chain): op1 -> op2 -> op3
        self.graph_linear = {
            "op1": {"service": "AccountService", "operation": "debit", "dependencies": []},
            "op2": {"service": "FraudDetectionService", "operation": "verify", "dependencies": ["op1"]},
            "op3": {"service": "NotificationService", "operation": "notify", "dependencies": ["op2"]}
        }

        # Define a parallel graph: three independent operations.
        self.graph_parallel = {
            "op1": {"service": "AccountService", "operation": "debit", "dependencies": []},
            "op2": {"service": "FraudDetectionService", "operation": "verify", "dependencies": []},
            "op3": {"service": "NotificationService", "operation": "notify", "dependencies": []}
        }

        self.payload = {"amount": 100}

    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_successful_linear_transaction(self):
        # All operations succeed in linear dependency.
        result = self.run_async(
            orchestrate_transaction(self.graph_linear, self.services_success, self.compensations_success, self.payload)
        )
        expected = {
            "op1": "completed",
            "op2": "completed",
            "op3": "completed"
        }
        self.assertEqual(result, expected)

    def test_failure_triggers_rollback(self):
        # In a linear graph, op2 fails and should trigger rollback of op1.
        result = self.run_async(
            orchestrate_transaction(self.graph_linear, self.services_failure, self.compensations_mixed, self.payload)
        )
        # Expected:
        # op1: was completed then rolled back successfully => "compensated"
        # op2: failed => "failed"
        # op3: not executed due to dependency => "pending"
        expected = {
            "op1": "compensated",
            "op2": "failed",
            "op3": "pending"
        }
        self.assertEqual(result, expected)

    def test_parallel_execution(self):
        # In a parallel graph, all independent operations should complete.
        result = self.run_async(
            orchestrate_transaction(self.graph_parallel, self.services_success, self.compensations_success, self.payload)
        )
        expected = {
            "op1": "completed",
            "op2": "completed",
            "op3": "completed"
        }
        self.assertEqual(result, expected)

    def test_mixed_failure_compensation(self):
        # Test scenario: op2 fails and its rollback for a dependency (op1) fails.
        async def comp_success(transaction_id, payload):
            await asyncio.sleep(0.05)
            return True

        async def comp_failure(transaction_id, payload):
            await asyncio.sleep(0.05)
            return False

        compensations = {
            "AccountService": {"debit": comp_failure},  # Fail to compensate op1
            "FraudDetectionService": {"verify": comp_success},
            "NotificationService": {"notify": comp_success}
        }
        result = self.run_async(
            orchestrate_transaction(self.graph_linear, self.services_failure, compensations, self.payload)
        )
        # Expected:
        # op1: compensation attempted but failed => "compensate_failed"
        # op2: failed => "failed"
        # op3: not executed => "pending"
        expected = {
            "op1": "compensate_failed",
            "op2": "failed",
            "op3": "pending"
        }
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()