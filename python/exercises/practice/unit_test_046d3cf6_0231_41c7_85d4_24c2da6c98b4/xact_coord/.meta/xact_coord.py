import time

class TransactionCoordinator:
    def __init__(self, timeout=1.0, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.log = []

    def send_request(self, service_url, transaction_id, command):
        """
        Simulate sending a request to a service endpoint.
        In a real-world scenario, this would use network I/O.
        For simulation, this method should be overridden or mocked in tests.
        """
        # Default implementation always succeeds.
        return True

    def _attempt_command(self, service_url, transaction_id, command):
        attempts = 0
        while attempts <= self.max_retries:
            result = self.send_request(service_url, transaction_id, command)
            self.log.append((service_url, command, result, attempts+1))
            if result:
                return True
            attempts += 1
            time.sleep(self.timeout)
        return False

    def rollback_all(self, services, transaction_id):
        # Rollback for all services regardless of previous operations.
        for service in services:
            # Even if the service has duplicate operations, we send rollback only once per service.
            self._attempt_command(service['url'], transaction_id, "rollback")

    def coordinate_transaction(self, services, transaction_id):
        """
        Coordinates the transaction across services.
        Each service is expected to be a dictionary with fields:
            - 'url': the service endpoint URL.
            - 'operations': a list of commands (e.g., ['prepare', 'commit']).
        The coordinator sends each operation sequentially. If any operation fails,
        it triggers a rollback across all services and returns a rolledback status.
        """
        # Iterate through each service and perform its operations in order.
        for service in services:
            service_url = service['url']
            for command in service.get('operations', []):
                success = self._attempt_command(service_url, transaction_id, command)
                if not success:
                    # If any command fails, rollback all services.
                    self.rollback_all(services, transaction_id)
                    return {'status': 'rolledback', 'error': f"Failed to {command} for service {service_url}"}
        return {'status': 'committed'}