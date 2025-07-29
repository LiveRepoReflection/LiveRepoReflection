import time
from typing import Dict, Callable, Any
from dataclasses import dataclass

@dataclass
class ServiceOperation:
    prepare: Callable[[Dict], bool]
    commit: Callable[[Dict], bool]
    rollback: Callable[[Dict], bool]

class TransactionOrchestrator:
    def __init__(self, services: Dict[str, ServiceOperation]):
        self.services = services
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _execute_with_retry(self, operation: Callable, payload: Dict) -> bool:
        for attempt in range(self.max_retries):
            try:
                return operation(payload)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay)
        return False

    def process_order(self, order_data: Dict) -> Dict[str, Any]:
        prepared_services = []
        result = {'success': False, 'error': None}

        # Prepare phase
        try:
            for service_name, service in self.services.items():
                if not self._execute_with_retry(service.prepare, order_data):
                    result['error'] = f'{service_name} prepare failed'
                    raise Exception(result['error'])
                prepared_services.append(service_name)

            # Commit phase
            for service_name in prepared_services:
                if not self._execute_with_retry(self.services[service_name].commit, order_data):
                    result['error'] = f'{service_name} commit failed'
                    raise Exception(result['error'])

            result['success'] = True
            return result

        except Exception as e:
            # Rollback phase
            for service_name in reversed(prepared_services):
                try:
                    self._execute_with_retry(self.services[service_name].rollback, order_data)
                except Exception as rollback_error:
                    result['error'] = f'Rollback failed for {service_name}: {str(rollback_error)}'
                    break

            return result