import time
import random
import logging
import threading
import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Service:
    def __init__(self, service_id: str, failure_probabilities: Dict[str, float]):
        self.service_id = service_id
        self.failure_probabilities = failure_probabilities
        self.prepared = False
        self.committed = False
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"Service-{service_id}")

    def _simulate_network_delay(self):
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)

    def _should_fail(self, operation: str) -> bool:
        return random.random() < self.failure_probabilities.get(operation, 0.0)

    def prepare(self) -> bool:
        self._simulate_network_delay()
        
        if self._should_fail("prepare"):
            self.logger.warning(f"{self.service_id}: Prepare failed")
            return False

        with self.lock:
            if not self.prepared:
                self.prepared = True
                self.logger.info(f"{self.service_id}: Prepare successful")
            return True

    def commit(self) -> bool:
        self._simulate_network_delay()

        if self._should_fail("commit"):
            self.logger.warning(f"{self.service_id}: Commit failed")
            return False

        with self.lock:
            if not self.committed and self.prepared:
                self.committed = True
                self.logger.info(f"{self.service_id}: Commit successful")
            return True

    def rollback(self) -> bool:
        self._simulate_network_delay()

        if self._should_fail("rollback"):
            self.logger.warning(f"{self.service_id}: Rollback failed")
            return False

        with self.lock:
            if self.prepared:
                self.prepared = False
                self.committed = False
                self.logger.info(f"{self.service_id}: Rollback successful")
            return True

class TransactionOrchestrator:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.logger = logging.getLogger("Orchestrator")
        self.executor = ThreadPoolExecutor(max_workers=100)

    async def _prepare_service(self, service: Service) -> bool:
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, service.prepare
            )
            return result
        except Exception as e:
            self.logger.error(f"Error during prepare phase for {service.service_id}: {str(e)}")
            return False

    async def _commit_service(self, service: Service) -> bool:
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, service.commit
            )
            return result
        except Exception as e:
            self.logger.error(f"Error during commit phase for {service.service_id}: {str(e)}")
            return False

    async def _rollback_service(self, service: Service) -> bool:
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, service.rollback
            )
            return result
        except Exception as e:
            self.logger.error(f"Error during rollback phase for {service.service_id}: {str(e)}")
            return False

    async def _prepare_phase(self, services: List[Service]) -> bool:
        self.logger.info("Phase 1: Prepare")
        prepare_tasks = [self._prepare_service(service) for service in services]
        
        try:
            results = await asyncio.gather(*prepare_tasks, return_exceptions=True)
            return all(isinstance(r, bool) and r for r in results)
        except asyncio.TimeoutError:
            self.logger.error("Prepare phase timed out")
            return False

    async def _commit_phase(self, services: List[Service]) -> bool:
        self.logger.info("Phase 2: Commit")
        commit_tasks = [self._commit_service(service) for service in services]
        
        try:
            results = await asyncio.gather(*commit_tasks)
            return all(results)
        except Exception as e:
            self.logger.error(f"Error during commit phase: {str(e)}")
            return False

    async def _rollback_phase(self, services: List[Service]) -> None:
        self.logger.info("Phase 2: Rollback")
        rollback_tasks = [self._rollback_service(service) for service in services]
        
        try:
            await asyncio.gather(*rollback_tasks)
        except Exception as e:
            self.logger.error(f"Error during rollback phase: {str(e)}")

    def execute_transaction(self, services: List[Service]) -> bool:
        async def _execute():
            try:
                # Phase 1: Prepare
                prepare_success = await asyncio.wait_for(
                    self._prepare_phase(services),
                    timeout=self.timeout
                )

                if not prepare_success:
                    self.logger.warning("Prepare phase failed, initiating rollback")
                    await self._rollback_phase(services)
                    return False

                # Phase 2: Commit
                commit_success = await self._commit_phase(services)
                if not commit_success:
                    self.logger.warning("Commit phase failed, initiating rollback")
                    await self._rollback_phase(services)
                    return False

                return True

            except asyncio.TimeoutError:
                self.logger.error("Transaction timed out")
                await self._rollback_phase(services)
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error during transaction: {str(e)}")
                await self._rollback_phase(services)
                return False

        # Create new event loop for each transaction
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_execute())
        finally:
            loop.close()