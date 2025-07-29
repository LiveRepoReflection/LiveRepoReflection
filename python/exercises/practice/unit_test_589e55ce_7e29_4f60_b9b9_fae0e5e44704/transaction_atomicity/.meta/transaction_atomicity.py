import asyncio
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import time
import aiohttp
from datetime import datetime
import uuid

class TransactionStatus(Enum):
    INITIATED = "initiated"
    PREPARING = "preparing"
    COMMITTING = "committing"
    ROLLING_BACK = "rolling_back"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RECOVERY_INITIATED = "recovery_initiated"

@dataclass
class Operation:
    service: str
    operation: str
    params: Dict

@dataclass
class Transaction:
    transaction_id: str
    operations: List[Operation]
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime
    retry_count: int = 0

class TransactionLog:
    def __init__(self):
        self._transactions: Dict[str, Transaction] = {}
        self._lock = asyncio.Lock()

    async def save_transaction(self, transaction: Transaction):
        async with self._lock:
            self._transactions[transaction.transaction_id] = transaction

    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        async with self._lock:
            return self._transactions.get(transaction_id)

    async def update_transaction_status(self, transaction_id: str, status: TransactionStatus):
        async with self._lock:
            if transaction_id in self._transactions:
                self._transactions[transaction_id].status = status
                self._transactions[transaction_id].updated_at = datetime.now()

class TransactionOrchestrator:
    def __init__(self, timeout: float = 5.0):
        self.transaction_log = TransactionLog()
        self.timeout = timeout
        self._services_lock = {}

    async def process_transaction(self, transaction_request: Dict) -> Dict:
        # Validate transaction request
        if not isinstance(transaction_request.get("operations"), list):
            raise ValueError("Invalid transaction format: operations must be a list")

        transaction_id = transaction_request.get("transaction_id", str(uuid.uuid4()))
        
        # Check for existing transaction (idempotency)
        existing_transaction = await self.transaction_log.get_transaction(transaction_id)
        if existing_transaction and existing_transaction.status in [TransactionStatus.COMMITTED, TransactionStatus.ROLLED_BACK]:
            return {
                "transaction_id": transaction_id,
                "success": existing_transaction.status == TransactionStatus.COMMITTED,
                "status": existing_transaction.status.value
            }

        # Create new transaction
        transaction = Transaction(
            transaction_id=transaction_id,
            operations=[Operation(**op) for op in transaction_request["operations"]],
            status=TransactionStatus.INITIATED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await self.transaction_log.save_transaction(transaction)

        try:
            # Phase 1: Prepare
            await self._prepare_phase(transaction)
            
            # Phase 2: Commit
            await self._commit_phase(transaction)
            
            await self.transaction_log.update_transaction_status(
                transaction.transaction_id, TransactionStatus.COMMITTED
            )
            
            return {
                "transaction_id": transaction.transaction_id,
                "success": True,
                "status": "committed"
            }

        except asyncio.TimeoutError:
            await self.transaction_log.update_transaction_status(
                transaction.transaction_id, TransactionStatus.TIMEOUT
            )
            await self._rollback_phase(transaction)
            return {
                "transaction_id": transaction.transaction_id,
                "success": False,
                "status": "timeout"
            }

        except Exception as e:
            await self.transaction_log.update_transaction_status(
                transaction.transaction_id, TransactionStatus.FAILED
            )
            await self._rollback_phase(transaction)
            return {
                "transaction_id": transaction.transaction_id,
                "success": False,
                "status": "rolled_back"
            }

    async def _prepare_phase(self, transaction: Transaction):
        await self.transaction_log.update_transaction_status(
            transaction.transaction_id, TransactionStatus.PREPARING
        )

        prepare_tasks = []
        for operation in transaction.operations:
            prepare_tasks.append(self._send_prepare_request(operation))

        prepare_results = await asyncio.gather(*prepare_tasks, return_exceptions=True)

        for result in prepare_results:
            if isinstance(result, Exception) or result != "commit-ok":
                raise Exception("Prepare phase failed")

    async def _commit_phase(self, transaction: Transaction):
        await self.transaction_log.update_transaction_status(
            transaction.transaction_id, TransactionStatus.COMMITTING
        )

        commit_tasks = []
        for operation in transaction.operations:
            commit_tasks.append(self._send_commit_request(operation))

        commit_results = await asyncio.gather(*commit_tasks, return_exceptions=True)

        for result in commit_results:
            if isinstance(result, Exception) or result != "success":
                raise Exception("Commit phase failed")

    async def _rollback_phase(self, transaction: Transaction):
        await self.transaction_log.update_transaction_status(
            transaction.transaction_id, TransactionStatus.ROLLING_BACK
        )

        rollback_tasks = []
        for operation in transaction.operations:
            rollback_tasks.append(self._send_rollback_request(operation))

        await asyncio.gather(*rollback_tasks, return_exceptions=True)
        
        await self.transaction_log.update_transaction_status(
            transaction.transaction_id, TransactionStatus.ROLLED_BACK
        )

    async def _send_prepare_request(self, operation: Operation) -> str:
        # Simulated network call
        await asyncio.sleep(0.1)
        return "commit-ok"

    async def _send_commit_request(self, operation: Operation) -> str:
        # Simulated network call
        await asyncio.sleep(0.1)
        return "success"

    async def _send_rollback_request(self, operation: Operation) -> str:
        # Simulated network call
        await asyncio.sleep(0.1)
        return "success"

    async def recover_pending_transactions(self):
        """
        Recovery method to handle orchestrator crashes
        """
        async with self.transaction_log._lock:
            for transaction in self.transaction_log._transactions.values():
                if transaction.status in [TransactionStatus.PREPARING, TransactionStatus.COMMITTING]:
                    await self._rollback_phase(transaction)