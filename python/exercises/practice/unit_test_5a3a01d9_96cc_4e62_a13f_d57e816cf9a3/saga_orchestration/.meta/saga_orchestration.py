import threading
import uuid
import time
import logging
import json
from queue import Queue
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SagaStatus(Enum):
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"

class StepStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    COMPENSATED = "COMPENSATED"

@dataclass
class SagaStep:
    name: str
    execute: callable
    compensate: callable
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    depends_on: List[str] = None

class SagaTransaction:
    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id
        self.status = SagaStatus.STARTED
        self.steps: List[SagaStep] = []
        self.current_step_index = 0
        self.start_time = time.time()
        self.end_time = None
        self.error = None
        self.compensation_status = None
        self.lock = Lock()

class SagaOrchestrator:
    def __init__(self):
        self.transactions: Dict[str, SagaTransaction] = {}
        self.transaction_lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.completed_steps: Dict[str, Queue] = {}

    def create_saga(self, order_data: dict) -> str:
        """Create a new saga transaction"""
        transaction_id = str(uuid.uuid4())
        saga = SagaTransaction(transaction_id)
        
        # Define saga steps with their execute and compensate functions
        steps = [
            SagaStep(
                name="CREATE_ORDER",
                execute=lambda: self._create_order(order_data),
                compensate=lambda: self._cancel_order(order_data),
                depends_on=[]
            ),
            SagaStep(
                name="RESERVE_INVENTORY",
                execute=lambda: self._reserve_inventory(order_data),
                compensate=lambda: self._release_inventory(order_data),
                depends_on=["CREATE_ORDER"]
            ),
            SagaStep(
                name="PROCESS_PAYMENT",
                execute=lambda: self._process_payment(order_data),
                compensate=lambda: self._refund_payment(order_data),
                depends_on=["CREATE_ORDER"]
            ),
            SagaStep(
                name="CREATE_SHIPMENT",
                execute=lambda: self._create_shipment(order_data),
                compensate=lambda: self._cancel_shipment(order_data),
                depends_on=["RESERVE_INVENTORY", "PROCESS_PAYMENT"]
            )
        ]
        
        saga.steps = steps
        with self.transaction_lock:
            self.transactions[transaction_id] = saga
        return transaction_id

    def execute_saga(self, order_data: dict) -> dict:
        """Execute the saga transaction"""
        transaction_id = self.create_saga(order_data)
        saga = self.transactions[transaction_id]
        
        try:
            # Execute steps
            self._execute_steps(saga)
            
            # Check if all steps completed successfully
            if all(step.status == StepStatus.SUCCESS for step in saga.steps):
                saga.status = SagaStatus.COMPLETED
                saga.end_time = time.time()
                return {
                    "status": "SUCCESS",
                    "transaction_id": transaction_id,
                    "execution_time": saga.end_time - saga.start_time
                }
            else:
                # Initiate compensation if any step failed
                self._compensate_transaction(saga)
                return {
                    "status": "FAILED",
                    "transaction_id": transaction_id,
                    "error": saga.error,
                    "compensation_status": saga.compensation_status
                }
                
        except Exception as e:
            logger.error(f"Saga execution failed: {str(e)}")
            saga.status = SagaStatus.FAILED
            saga.error = str(e)
            self._compensate_transaction(saga)
            return {
                "status": "FAILED",
                "transaction_id": transaction_id,
                "error": str(e)
            }

    def _execute_steps(self, saga: SagaTransaction):
        """Execute saga steps with parallel execution where possible"""
        while saga.current_step_index < len(saga.steps):
            current_steps = self._get_parallel_steps(saga)
            
            if not current_steps:
                break
                
            # Execute parallel steps
            futures = []
            for step in current_steps:
                futures.append(self.executor.submit(self._execute_step, saga, step))
                
            # Wait for all parallel steps to complete
            for future in futures:
                try:
                    future.result(timeout=30)  # 30 second timeout
                except Exception as e:
                    saga.error = str(e)
                    return
                
            saga.current_step_index += 1

    def _execute_step(self, saga: SagaTransaction, step: SagaStep):
        """Execute a single saga step with retry logic"""
        while step.retry_count < step.max_retries:
            try:
                logger.info(f"Executing step {step.name} for transaction {saga.transaction_id}")
                result = step.execute()
                step.status = StepStatus.SUCCESS
                return result
            except Exception as e:
                step.retry_count += 1
                if step.retry_count >= step.max_retries:
                    step.status = StepStatus.FAILED
                    raise e
                time.sleep(1)  # Wait before retry

    def _compensate_transaction(self, saga: SagaTransaction):
        """Compensate the saga transaction"""
        saga.status = SagaStatus.COMPENSATING
        
        # Compensate steps in reverse order
        for step in reversed(saga.steps):
            if step.status == StepStatus.SUCCESS:
                try:
                    step.compensate()
                    step.status = StepStatus.COMPENSATED
                except Exception as e:
                    logger.error(f"Compensation failed for step {step.name}: {str(e)}")
                    saga.compensation_status = "PARTIAL"
                    return
                    
        saga.compensation_status = "SUCCESS"

    def _get_parallel_steps(self, saga: SagaTransaction) -> List[SagaStep]:
        """Get steps that can be executed in parallel"""
        parallel_steps = []
        for step in saga.steps:
            if step.status == StepStatus.PENDING:
                if not step.depends_on or all(
                    self._is_step_completed(saga, dep) for dep in step.depends_on
                ):
                    parallel_steps.append(step)
        return parallel_steps

    def _is_step_completed(self, saga: SagaTransaction, step_name: str) -> bool:
        """Check if a step is completed successfully"""
        return any(
            step.name == step_name and step.status == StepStatus.SUCCESS
            for step in saga.steps
        )

    # Mock service implementations
    def _create_order(self, order_data: dict) -> dict:
        time.sleep(0.1)  # Simulate service call
        return {"order_id": str(uuid.uuid4())}

    def _cancel_order(self, order_data: dict):
        time.sleep(0.1)  # Simulate service call
        pass

    def _reserve_inventory(self, order_data: dict) -> dict:
        time.sleep(0.1)  # Simulate service call
        return {"reservation_id": str(uuid.uuid4())}

    def _release_inventory(self, order_data: dict):
        time.sleep(0.1)  # Simulate service call
        pass

    def _process_payment(self, order_data: dict) -> dict:
        time.sleep(0.1)  # Simulate service call
        return {"payment_id": str(uuid.uuid4())}

    def _refund_payment(self, order_data: dict):
        time.sleep(0.1)  # Simulate service call
        pass

    def _create_shipment(self, order_data: dict) -> dict:
        time.sleep(0.1)  # Simulate service call
        return {"shipment_id": str(uuid.uuid4())}

    def _cancel_shipment(self, order_data: dict):
        time.sleep(0.1)  # Simulate service call
        pass

    def get_saga_status(self, transaction_id: str) -> dict:
        """Get the current status of a saga transaction"""
        if transaction_id in self.transactions:
            saga = self.transactions[transaction_id]
            return {
                "transaction_id": saga.transaction_id,
                "status": saga.status.value,
                "steps": [
                    {
                        "name": step.name,
                        "status": step.status.value,
                        "retry_count": step.retry_count
                    }
                    for step in saga.steps
                ],
                "start_time": saga.start_time,
                "end_time": saga.end_time,
                "error": saga.error,
                "compensation_status": saga.compensation_status
            }
        return None

    def get_resource_status(self) -> dict:
        """Get the current resource usage status"""
        return {
            "active_transactions": len(self.transactions),
            "executor_threads": self.executor._max_workers,
            "thread_pool_status": {
                "running": len(self.executor._threads),
                "tasks": len(self.executor._work_queue.queue)
            }
        }