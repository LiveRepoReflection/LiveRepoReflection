import unittest
import threading
import time
from dist_tx import process_transactions

class TestDistTx(unittest.TestCase):
    def test_all_committed(self):
        # All microservices always succeed in prepare and commit.
        def always_prepare(tx_id, data):
            return True

        def always_commit(tx_id):
            return True

        microservices = [
            {'name': 'ServiceA', 'prepare': always_prepare, 'commit': always_commit, 'max_concurrency': 2},
            {'name': 'ServiceB', 'prepare': always_prepare, 'commit': always_commit, 'max_concurrency': 2},
        ]

        transactions = [
            {'id': 'TX1', 'involved_services': ['ServiceA', 'ServiceB'], 'data': {'value': 10}},
            {'id': 'TX2', 'involved_services': ['ServiceA'], 'data': {'value': 20}},
        ]

        result = process_transactions(microservices, transactions)
        expected = [
            {'id': 'TX1', 'status': 'COMMITTED'},
            {'id': 'TX2', 'status': 'COMMITTED'},
        ]
        # Order may vary: sort by id for comparison.
        self.assertEqual(sorted(result, key=lambda x: x['id']), sorted(expected, key=lambda x: x['id']))

    def test_prepare_failure(self):
        # One microservice fails in the prepare phase.
        def good_prepare(tx_id, data):
            return True

        def bad_prepare(tx_id, data):
            return False

        def always_commit(tx_id):
            return True

        microservices = [
            {'name': 'ServiceGood', 'prepare': good_prepare, 'commit': always_commit, 'max_concurrency': 2},
            {'name': 'ServiceBad', 'prepare': bad_prepare, 'commit': always_commit, 'max_concurrency': 2},
        ]

        transactions = [
            {'id': 'TX_FAIL', 'involved_services': ['ServiceGood', 'ServiceBad'], 'data': {'order': 1}},
        ]

        result = process_transactions(microservices, transactions)
        expected = [{'id': 'TX_FAIL', 'status': 'ABORTED'}]
        self.assertEqual(result, expected)

    def test_commit_with_retry_success(self):
        # Simulate commit failures that eventually succeed after retries.
        commit_attempts = {}
        def good_prepare(tx_id, data):
            return True

        def flaky_commit(tx_id):
            attempts = commit_attempts.get(tx_id, 0)
            commit_attempts[tx_id] = attempts + 1
            # Fail first 2 times, succeed on 3rd attempt.
            if commit_attempts[tx_id] < 3:
                raise Exception("Temporary commit failure")
            return True

        microservices = [
            {'name': 'ServiceFlaky', 'prepare': good_prepare, 'commit': flaky_commit, 'max_concurrency': 2},
        ]

        transactions = [
            {'id': 'TX_RETRY', 'involved_services': ['ServiceFlaky'], 'data': {'retry': True}},
        ]

        result = process_transactions(microservices, transactions)
        expected = [{'id': 'TX_RETRY', 'status': 'COMMITTED'}]
        self.assertEqual(result, expected)
        # Ensure we attempted commit at least 3 times.
        self.assertTrue(commit_attempts.get('TX_RETRY', 0) >= 3)

    def test_commit_with_retry_fail(self):
        # Simulate commit failures that persist even after allowed retries.
        commit_attempts = {}
        def good_prepare(tx_id, data):
            return True

        def always_fail_commit(tx_id):
            attempts = commit_attempts.get(tx_id, 0)
            commit_attempts[tx_id] = attempts + 1
            raise Exception("Persistent commit failure")

        microservices = [
            {'name': 'ServiceAlwaysFail', 'prepare': good_prepare, 'commit': always_fail_commit, 'max_concurrency': 2},
            {'name': 'ServiceGood', 'prepare': good_prepare, 'commit': lambda tx_id: True, 'max_concurrency': 2},
        ]

        transactions = [
            {'id': 'TX_PARTIAL', 'involved_services': ['ServiceAlwaysFail', 'ServiceGood'], 'data': {'attempt': 'fail_commit'}},
        ]

        result = process_transactions(microservices, transactions)
        # Even if one service fails to commit after retries, the transaction is considered COMMITTED
        expected = [{'id': 'TX_PARTIAL', 'status': 'COMMITTED'}]
        self.assertEqual(result, expected)
        # Ensure retries were attempted for the failing service (at least 3 times).
        self.assertTrue(commit_attempts.get('TX_PARTIAL', 0) >= 3)

    def test_multiple_transactions(self):
        # Test multiple transactions running concurrently.
        def good_prepare(tx_id, data):
            return True

        def good_commit(tx_id):
            return True

        microservices = [
            {'name': 'Service1', 'prepare': good_prepare, 'commit': good_commit, 'max_concurrency': 3},
            {'name': 'Service2', 'prepare': good_prepare, 'commit': good_commit, 'max_concurrency': 3},
            {'name': 'Service3', 'prepare': good_prepare, 'commit': good_commit, 'max_concurrency': 3}
        ]

        transactions = []
        for i in range(10):
            involved = ['Service1', 'Service2'] if i % 2 == 0 else ['Service2', 'Service3']
            transactions.append({'id': f'TX_{i}', 'involved_services': involved, 'data': {'val': i}})

        result = process_transactions(microservices, transactions)
        # All transactions should be committed.
        for tx_status in result:
            self.assertEqual(tx_status['status'], 'COMMITTED')
        self.assertEqual(len(result), 10)

    def test_max_concurrency(self):
        # Test that the microservice's max_concurrency is respected.
        lock = threading.Lock()
        current_concurrency = [0]  # use list as mutable container

        def limited_prepare(tx_id, data):
            with lock:
                current_concurrency[0] += 1
                active = current_concurrency[0]
            # Simulate processing delay
            time.sleep(0.1)
            with lock:
                current_concurrency[0] -= 1
            # If active exceeds max_concurrency (which is 1), simulate failure.
            if active > 1:
                return False
            return True

        def always_commit(tx_id):
            return True

        microservices = [
            {'name': 'LimitedService', 'prepare': limited_prepare, 'commit': always_commit, 'max_concurrency': 1},
        ]

        # Create two transactions that both require LimitedService.
        transactions = [
            {'id': 'TX_CONC_1', 'involved_services': ['LimitedService'], 'data': {}},
            {'id': 'TX_CONC_2', 'involved_services': ['LimitedService'], 'data': {}},
        ]

        # Run process_transactions in a separate thread to simulate concurrency.
        result = process_transactions(microservices, transactions)
        # At least one of the transactions should be aborted because of concurrency limit violation.
        statuses = {tx['id']: tx['status'] for tx in result}
        self.assertIn(statuses['TX_CONC_1'], ['COMMITTED', 'ABORTED'])
        self.assertIn(statuses['TX_CONC_2'], ['COMMITTED', 'ABORTED'])
        # It cannot be that both are committed because with max concurrency of 1 and overlapping delays,
        # one must have failed its prepare if they truly ran concurrently.
        self.assertNotEqual(statuses['TX_CONC_1'], statuses['TX_CONC_2'] == 'COMMITTED' and 'COMMITTED')

if __name__ == '__main__':
    unittest.main()