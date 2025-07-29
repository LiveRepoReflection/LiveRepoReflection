import unittest
from unittest.mock import Mock, patch
import uuid
import asyncio
from datetime import datetime, timedelta

class TestDistributedBooking(unittest.TestCase):
    def setUp(self):
        self.coordinator_mock = Mock()
        self.transaction_id = str(uuid.uuid4())
        self.user_id = "user123"
        self.flight_id = "flight456"
        self.hotel_id = "hotel789"
        self.amount = 1000.0

    @patch('distributed_booking.TransactionCoordinator')
    async def test_successful_booking(self, mock_coordinator):
        # Mock successful responses from all services
        mock_coordinator.process_user_reservation.return_value = True
        mock_coordinator.process_flight_booking.return_value = True
        mock_coordinator.process_hotel_booking.return_value = True
        mock_coordinator.process_payment.return_value = True

        result = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.status, "COMPLETED")

    @patch('distributed_booking.TransactionCoordinator')
    async def test_booking_with_flight_failure(self, mock_coordinator):
        # Mock failure in flight booking
        mock_coordinator.process_user_reservation.return_value = True
        mock_coordinator.process_flight_booking.side_effect = Exception("Flight unavailable")
        
        result = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.status, "FAILED")
        # Verify compensation was called for user reservation
        mock_coordinator.compensate_user_reservation.assert_called_once()

    @patch('distributed_booking.TransactionCoordinator')
    async def test_concurrent_bookings(self, mock_coordinator):
        # Test multiple concurrent bookings
        booking_tasks = []
        for _ in range(5):
            task = mock_coordinator.execute_booking(
                str(uuid.uuid4()),
                self.user_id,
                self.flight_id,
                self.hotel_id,
                self.amount
            )
            booking_tasks.append(task)
        
        results = await asyncio.gather(*booking_tasks, return_exceptions=True)
        self.assertEqual(len(results), 5)

    @patch('distributed_booking.TransactionCoordinator')
    async def test_timeout_scenario(self, mock_coordinator):
        # Mock a slow service response
        async def slow_flight_booking(*args):
            await asyncio.sleep(65)  # Longer than the 60-second timeout
            return True

        mock_coordinator.process_flight_booking.side_effect = slow_flight_booking
        
        result = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.status, "TIMEOUT")

    @patch('distributed_booking.TransactionCoordinator')
    async def test_idempotency(self, mock_coordinator):
        # Test same transaction ID multiple times
        result1 = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        result2 = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        self.assertEqual(result1.transaction_id, result2.transaction_id)

    @patch('distributed_booking.TransactionCoordinator')
    async def test_partial_compensation_failure(self, mock_coordinator):
        # Mock successful initial booking but failed compensation
        mock_coordinator.process_user_reservation.return_value = True
        mock_coordinator.process_flight_booking.return_value = True
        mock_coordinator.process_hotel_booking.side_effect = Exception("Hotel booking failed")
        mock_coordinator.compensate_flight_booking.side_effect = Exception("Compensation failed")
        
        result = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.status, "COMPENSATION_FAILED")

    @patch('distributed_booking.TransactionCoordinator')
    async def test_optimistic_locking(self, mock_coordinator):
        # Test version conflicts
        mock_coordinator.get_resource_version.return_value = 1
        mock_coordinator.process_flight_booking.side_effect = Exception("Version conflict")
        
        result = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.status, "VERSION_CONFLICT")

    @patch('distributed_booking.TransactionCoordinator')
    async def test_retry_mechanism(self, mock_coordinator):
        # Test retry behavior for transient failures
        mock_coordinator.process_payment.side_effect = [
            Exception("Temporary failure"),
            Exception("Temporary failure"),
            True
        ]
        
        result = await mock_coordinator.execute_booking(
            self.transaction_id,
            self.user_id,
            self.flight_id,
            self.hotel_id,
            self.amount
        )
        
        self.assertTrue(result.success)
        self.assertEqual(mock_coordinator.process_payment.call_count, 3)

if __name__ == '__main__':
    unittest.main()