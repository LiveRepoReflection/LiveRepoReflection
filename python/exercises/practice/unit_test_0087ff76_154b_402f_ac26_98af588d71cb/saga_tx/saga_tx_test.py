import unittest
import asyncio
from saga_tx import execute_transaction

class SagaTxTest(unittest.IsolatedAsyncioTestCase):
    async def test_successful_transaction(self):
        transaction_definition = {
            'txn1': {
                'service': 'AccountService',
                'operation': 'DebitAccount',
                'data': {'account_id': 'A1', 'amount': 100},
                'compensating_operation': 'CreditAccount',
                'compensating_data': {'account_id': 'A1', 'amount': 100},
                'dependencies': []
            },
            'txn2': {
                'service': 'TransactionLogService',
                'operation': 'LogTransaction',
                'data': {'transaction_id': 'TXN-001'},
                'compensating_operation': 'DeleteLog',
                'compensating_data': {'transaction_id': 'TXN-001'},
                'dependencies': ['txn1']
            },
            'txn3': {
                'service': 'FraudService',
                'operation': 'CheckFraud',
                'data': {'account_id': 'A1', 'transaction_id': 'TXN-001'},
                'compensating_operation': 'RevertFraudCheck',
                'compensating_data': {'account_id': 'A1', 'transaction_id': 'TXN-001'},
                'dependencies': ['txn1']
            },
            'txn4': {
                'service': 'NotificationService',
                'operation': 'SendNotification',
                'data': {'account_id': 'A1', 'message': 'Transaction complete'},
                'compensating_operation': 'RevokeNotification',
                'compensating_data': {'account_id': 'A1'},
                'dependencies': ['txn2', 'txn3']
            }
        }
        result = await execute_transaction(transaction_definition)
        self.assertTrue(result)

    async def test_failure_in_transaction(self):
        # This transaction is designed to fail because the AccountService DebitAccount
        # will raise an exception if the amount exceeds a threshold.
        transaction_definition = {
            'txn1': {
                'service': 'AccountService',
                'operation': 'DebitAccount',
                'data': {'account_id': 'A1', 'amount': 600},
                'compensating_operation': 'CreditAccount',
                'compensating_data': {'account_id': 'A1', 'amount': 600},
                'dependencies': []
            },
            'txn2': {
                'service': 'TransactionLogService',
                'operation': 'LogTransaction',
                'data': {'transaction_id': 'TXN-002'},
                'compensating_operation': 'DeleteLog',
                'compensating_data': {'transaction_id': 'TXN-002'},
                'dependencies': ['txn1']
            }
        }
        result = await execute_transaction(transaction_definition)
        self.assertFalse(result)

    async def test_invalid_dag_cycle(self):
        # This transaction definition has a cycle: txn1 depends on txn2 and txn2 depends on txn1.
        transaction_definition = {
            'txn1': {
                'service': 'AccountService',
                'operation': 'DebitAccount',
                'data': {'account_id': 'A1', 'amount': 100},
                'compensating_operation': 'CreditAccount',
                'compensating_data': {'account_id': 'A1', 'amount': 100},
                'dependencies': ['txn2']
            },
            'txn2': {
                'service': 'TransactionLogService',
                'operation': 'LogTransaction',
                'data': {'transaction_id': 'TXN-003'},
                'compensating_operation': 'DeleteLog',
                'compensating_data': {'transaction_id': 'TXN-003'},
                'dependencies': ['txn1']
            }
        }
        with self.assertRaises(Exception):
            await execute_transaction(transaction_definition)

if __name__ == '__main__':
    asyncio.run(unittest.main())