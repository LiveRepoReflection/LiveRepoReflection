import asyncio
import uuid
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    COMPENSATION_FAILED = "COMPENSATION_FAILED"
    VERSION_CONFLICT = "VERSION_CONFLICT"

@dataclass
class TransactionResult:
    transaction_id: str
    success: bool
    status: TransactionStatus
    error_message: Optional[str] = None

class RetryConfig:
    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0, max_delay: float = 10.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay

class TransactionCoordinator:
    def __init__(self):
        self.transactions: Dict[str, Dict[str, Any]] = {}
        self.resource_versions: Dict[str, int] = {}
        self.retry_config = RetryConfig()
        self.timeout = 60  # seconds

    async def execute_booking(
        self,
        transaction_id: str,
        user_id: str,
        flight_id: str,
        hotel_id: str,
        amount: float
    ) -> TransactionResult:
        # Check for idempotency
        if transaction_id in self.transactions:
            logger.info(f"Return cached result for transaction {transaction_id}")
            return self.transactions[transaction_id]["result"]

        self.transactions[transaction_id] = {
            "start_time": datetime.now(),
            "status": TransactionStatus.PENDING
        }

        try:
            # Start timer for timeout
            task = asyncio.create_task(
                self._execute_booking_steps(
                    transaction_id, user_id, flight_id, hotel_id, amount
                )
            )
            result = await asyncio.wait_for(task, timeout=self.timeout)
            return result
        except asyncio.TimeoutError:
            logger.error(f"Transaction {transaction_id} timed out")
            await self._handle_timeout(transaction_id, user_id, flight_id, hotel_id)
            return TransactionResult(
                transaction_id=transaction_id,
                success=False,
                status=TransactionStatus.TIMEOUT
            )

    async def _execute_booking_steps(
        self,
        transaction_id: str,
        user_id: str,
        flight_id: str,
        hotel_id: str,
        amount: float
    ) -> TransactionResult:
        completed_steps = []
        try:
            # Step 1: Reserve user balance
            if await self._execute_with_retry(
                self.process_user_reservation,
                user_id,
                amount
            ):
                completed_steps.append(("user", user_id))

            # Step 2: Book flight
            if await self._execute_with_retry(
                self.process_flight_booking,
                flight_id
            ):
                completed_steps.append(("flight", flight_id))

            # Step 3: Book hotel
            if await self._execute_with_retry(
                self.process_hotel_booking,
                hotel_id
            ):
                completed_steps.append(("hotel", hotel_id))

            # Step 4: Process payment
            if await self._execute_with_retry(
                self.process_payment,
                user_id,
                amount
            ):
                completed_steps.append(("payment", amount))

            result = TransactionResult(
                transaction_id=transaction_id,
                success=True,
                status=TransactionStatus.COMPLETED
            )
            self.transactions[transaction_id]["result"] = result
            return result

        except Exception as e:
            logger.error(f"Transaction {transaction_id} failed: {str(e)}")
            await self._compensate_transaction(completed_steps)
            result = TransactionResult(
                transaction_id=transaction_id,
                success=False,
                status=TransactionStatus.FAILED,
                error_message=str(e)
            )
            self.transactions[transaction_id]["result"] = result
            return result

    async def _execute_with_retry(self, func, *args, **kwargs):
        retries = 0
        while retries < self.retry_config.max_retries:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries == self.retry_config.max_retries:
                    raise e
                delay = min(
                    self.retry_config.initial_delay * (2 ** retries),
                    self.retry_config.max_delay
                )
                await asyncio.sleep(delay)

    async def _compensate_transaction(self, completed_steps):
        for step_type, step_id in reversed(completed_steps):
            try:
                if step_type == "payment":
                    await self.compensate_payment(step_id)
                elif step_type == "hotel":
                    await self.compensate_hotel_booking(step_id)
                elif step_type == "flight":
                    await self.compensate_flight_booking(step_id)
                elif step_type == "user":
                    await self.compensate_user_reservation(step_id)
            except Exception as e:
                logger.error(f"Compensation failed for {step_type}: {str(e)}")
                raise Exception(f"Compensation failed: {str(e)}")

    async def _handle_timeout(self, transaction_id, user_id, flight_id, hotel_id):
        completed_steps = []
        for step_type, step_id in self.transactions[transaction_id].get("completed_steps", []):
            completed_steps.append((step_type, step_id))
        await self._compensate_transaction(completed_steps)

    # Mock service methods
    async def process_user_reservation(self, user_id: str, amount: float) -> bool:
        logger.info(f"Processing user reservation for user {user_id}")
        return True

    async def process_flight_booking(self, flight_id: str) -> bool:
        logger.info(f"Processing flight booking for flight {flight_id}")
        version = self.get_resource_version(f"flight_{flight_id}")
        if version != self.resource_versions.get(f"flight_{flight_id}", 0):
            raise Exception("Version conflict detected")
        return True

    async def process_hotel_booking(self, hotel_id: str) -> bool:
        logger.info(f"Processing hotel booking for hotel {hotel_id}")
        return True

    async def process_payment(self, user_id: str, amount: float) -> bool:
        logger.info(f"Processing payment for user {user_id}")
        return True

    # Compensation methods
    async def compensate_user_reservation(self, user_id: str):
        logger.info(f"Compensating user reservation for user {user_id}")
        return True

    async def compensate_flight_booking(self, flight_id: str):
        logger.info(f"Compensating flight booking for flight {flight_id}")
        return True

    async def compensate_hotel_booking(self, hotel_id: str):
        logger.info(f"Compensating hotel booking for hotel {hotel_id}")
        return True

    async def compensate_payment(self, amount: float):
        logger.info(f"Compensating payment of amount {amount}")
        return True

    def get_resource_version(self, resource_id: str) -> int:
        return self.resource_versions.get(resource_id, 0)
