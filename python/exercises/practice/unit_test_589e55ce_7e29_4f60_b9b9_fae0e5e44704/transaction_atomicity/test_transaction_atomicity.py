import unittest
from unittest.mock import patch, AsyncMock
import asyncio
from typing import List, Dict
import json

class TestTransactionOrchestrator(unittest.TestCase):
    def setUp(self):
        # This will be imported from your implementation
        from transaction_atomicity import TransactionOrchestrator
        self.orchestrator = TransactionOrchestrator()

    @patch('transaction_atomicity.TransactionOrchestrator._send_prepare_request')
    @patch('transaction_atomicity.TransactionOrchestrator._send_commit_request')
    async def test_successful_transaction(self, mock_commit, mock_prepare):
        # Setup mock responses
        mock_prepare.return_value = "commit-ok"
        mock_commit.return_value = "success"

        # Sample transaction request
        transaction = {
            "transaction_id": "tx123",
            "operations": [
                {
                    "service": "AccountService",
                    "operation": "debit",
                    "params": {"account_id": "acc1", "amount": 100}
                },
                {
                    "service": "PaymentService",
                    "operation": "process",
                    "params": {"payment_id": "p1", "amount": 100}
                }
            ]
        }

        result = await self.orchestrator.process_transaction(transaction)
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "committed")

    @patch('transaction_atomicity.TransactionOrchestrator._send_prepare_request')
    @patch('transaction_atomicity.TransactionOrchestrator._send_rollback_request')
    async def test_rollback_on_prepare_failure(self, mock_rollback, mock_prepare):
        mock_prepare.side_effect = ["commit-ok", "rollback-required"]
        mock_rollback.return_value = "success"

        transaction = {
            "transaction_id": "tx124",
            "operations": [
                {
                    "service": "AccountService",
                    "operation": "debit",
                    "params": {"account_id": "acc1", "amount": 100}
                },
                {
                    "service": "PaymentService",
                    "operation": "process",
                    "params": {"payment_id": "p1", "amount": 100}
                }
            ]
        }

        result = await self.orchestrator.process_transaction(transaction)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "rolled_back")

    @patch('transaction_atomicity.TransactionOrchestrator._send_prepare_request')
    async def test_timeout_handling(self, mock_prepare):
        mock_prepare.side_effect = asyncio.TimeoutError()

        transaction = {
            "transaction_id": "tx125",
            "operations": [
                {
                    "service": "AccountService",
                    "operation": "debit",
                    "params": {"account_id": "acc1", "amount": 100}
                }
            ]
        }

        result = await self.orchestrator.process_transaction(transaction)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "timeout")

    async def test_concurrent_transactions(self):
        transactions = [
            {
                "transaction_id": f"tx{i}",
                "operations": [
                    {
                        "service": "AccountService",
                        "operation": "debit",
                        "params": {"account_id": f"acc{i}", "amount": 100}
                    }
                ]
            }
            for i in range(10)
        ]

        tasks = [
            self.orchestrator.process_transaction(tx)
            for tx in transactions
        ]
        
        results = await asyncio.gather(*tasks)
        self.assertEqual(len(results), 10)

    @patch('transaction_atomicity.TransactionOrchestrator._send_prepare_request')
    @patch('transaction_atomicity.TransactionOrchestrator._send_commit_request')
    async def test_idempotency(self, mock_commit, mock_prepare):
        mock_prepare.return_value = "commit-ok"
        mock_commit.return_value = "success"

        transaction = {
            "transaction_id": "tx126",
            "operations": [
                {
                    "service": "AccountService",
                    "operation": "debit",
                    "params": {"account_id": "acc1", "amount": 100}
                }
            ]
        }

        # Process the same transaction twice
        result1 = await self.orchestrator.process_transaction(transaction)
        result2 = await self.orchestrator.process_transaction(transaction)

        self.assertEqual(result1["transaction_id"], result2["transaction_id"])
        self.assertEqual(result1["status"], result2["status"])

    @patch('transaction_atomicity.TransactionOrchestrator._send_prepare_request')
    @patch('transaction_atomicity.TransactionOrchestrator._send_commit_request')
    @patch('transaction_atomicity.TransactionOrchestrator._send_rollback_request')
    async def test_partial_failure_recovery(self, mock_rollback, mock_commit, mock_prepare):
        mock_prepare.return_value = "commit-ok"
        mock_commit.side_effect = ["success", asyncio.TimeoutError()]
        mock_rollback.return_value = "success"

        transaction = {
            "transaction_id": "tx127",
            "operations": [
                {
                    "service": "AccountService",
                    "operation": "debit",
                    "params": {"account_id": "acc1", "amount": 100}
                },
                {
                    "service": "PaymentService",
                    "operation": "process",
                    "params": {"payment_id": "p1", "amount": 100}
                }
            ]
        }

        result = await self.orchestrator.process_transaction(transaction)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "recovery_initiated")

    def test_invalid_transaction_format(self):
        invalid_transaction = {
            "transaction_id": "tx128",
            "operations": "invalid"  # Should be a list
        }

        with self.assertRaises(ValueError):
            asyncio.run(self.orchestrator.process_transaction(invalid_transaction))

if __name__ == '__main__':
    unittest.main()