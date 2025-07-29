import unittest
from unittest.mock import patch, AsyncMock
import asyncio
import json
from http import HTTPStatus

class TestDistributedTransactionManager(unittest.TestCase):
    def setUp(self):
        self.services = [
            "http://inventory-service/api",
            "http://payment-service/api",
            "http://order-service/api"
        ]
        self.test_payload = {
            "transaction_id": "tx123",
            "inventory": {"product_id": "p1", "quantity": 5},
            "payment": {"amount": 100, "currency": "USD"},
            "order": {"customer_id": "c1", "shipping_address": "123 Main St"}
        }

    @patch('aiohttp.ClientSession.post')
    async def test_successful_transaction(self, mock_post):
        # Mock successful prepare and commit responses
        mock_post.return_value.__aenter__.return_value.status = HTTPStatus.OK
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value={})

        from dtm_transaction import DTM
        dtm = DTM(self.services)
        result = await dtm.execute_transaction(self.test_payload)
        
        self.assertTrue(result['success'])
        self.assertEqual(mock_post.call_count, len(self.services) * 2)  # prepare + commit

    @patch('aiohttp.ClientSession.post')
    async def test_prepare_failure_triggers_rollback(self, mock_post):
        # Mock failed prepare for one service
        async def mock_response(*args, **kwargs):
            if 'prepare' in args[0] and 'payment-service' in args[0]:
                response = AsyncMock()
                response.status = HTTPStatus.INTERNAL_SERVER_ERROR
                response.json = AsyncMock(return_value={"error": "Insufficient funds"})
                return response
            response = AsyncMock()
            response.status = HTTPStatus.OK
            response.json = AsyncMock(return_value={})
            return response

        mock_post.side_effect = mock_response

        from dtm_transaction import DTM
        dtm = DTM(self.services)
        result = await dtm.execute_transaction(self.test_payload)
        
        self.assertFalse(result['success'])
        self.assertIn('Insufficient funds', result['error'])

    @patch('aiohttp.ClientSession.post')
    async def test_timeout_handling(self, mock_post):
        # Mock timeout during prepare
        async def timeout_response(*args, **kwargs):
            if 'inventory-service' in args[0]:
                await asyncio.sleep(6)  # Longer than timeout
            response = AsyncMock()
            response.status = HTTPStatus.OK
            response.json = AsyncMock(return_value={})
            return response

        mock_post.side_effect = timeout_response

        from dtm_transaction import DTM
        dtm = DTM(self.services, timeout=2)
        result = await dtm.execute_transaction(self.test_payload)
        
        self.assertFalse(result['success'])
        self.assertIn('timeout', result['error'].lower())

    @patch('aiohttp.ClientSession.post')
    async def test_idempotency(self, mock_post):
        # Mock successful responses
        mock_post.return_value.__aenter__.return_value.status = HTTPStatus.OK
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value={})

        from dtm_transaction import DTM
        dtm = DTM(self.services)
        
        # Execute same transaction twice
        result1 = await dtm.execute_transaction(self.test_payload)
        result2 = await dtm.execute_transaction(self.test_payload)
        
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertEqual(result1['transaction_id'], result2['transaction_id'])

    @patch('aiohttp.ClientSession.post')
    async def test_commit_retry_mechanism(self, mock_post):
        # Mock commit failure followed by success
        commit_attempts = 0
        async def mock_response(*args, **kwargs):
            nonlocal commit_attempts
            if 'commit' in args[0]:
                commit_attempts += 1
                if commit_attempts < 3:  # Fail first two attempts
                    response = AsyncMock()
                    response.status = HTTPStatus.INTERNAL_SERVER_ERROR
                    response.json = AsyncMock(return_value={"error": "Temporary error"})
                    return response
            response = AsyncMock()
            response.status = HTTPStatus.OK
            response.json = AsyncMock(return_value={})
            return response

        mock_post.side_effect = mock_response

        from dtm_transaction import DTM
        dtm = DTM(self.services)
        result = await dtm.execute_transaction(self.test_payload)
        
        self.assertTrue(result['success'])
        self.assertEqual(commit_attempts, 3)

    def test_invalid_service_urls(self):
        invalid_services = ["not-a-url", "http://"]
        
        from dtm_transaction import DTM
        with self.assertRaises(ValueError):
            DTM(invalid_services)

    def test_invalid_payload(self):
        invalid_payload = {"missing": "transaction_id"}
        
        from dtm_transaction import DTM
        dtm = DTM(self.services)
        
        with self.assertRaises(ValueError):
            asyncio.run(dtm.execute_transaction(invalid_payload))

def run_async_tests():
    loop = asyncio.get_event_loop()
    unittest.main()

if __name__ == '__main__':
    run_async_tests()