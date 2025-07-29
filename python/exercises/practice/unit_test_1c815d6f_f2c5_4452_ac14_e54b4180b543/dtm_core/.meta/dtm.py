import threading
import time

class DistributedTransactionManager:
    def __init__(self, timeout=1.0):
        self.timeout = timeout

    def call_with_timeout(self, func, args=(), kwargs={}):
        result = {}

        def wrapper():
            try:
                result['value'] = func(*args, **kwargs)
            except Exception as e:
                result['exception'] = e

        thread = threading.Thread(target=wrapper)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            raise Exception("timeout during call to " + func.__name__)
        if 'exception' in result:
            raise result['exception']
        return result.get('value', None)

    def execute_transaction(self, transaction_id, services):
        prepared_services = []
        try:
            # Phase 1: Prepare all services
            for svc in services:
                self.call_with_timeout(svc.prepare, args=(transaction_id,))
                prepared_services.append(svc)
            # Phase 2: Commit all services
            for svc in services:
                svc.commit(transaction_id)
            return True
        except Exception as e:
            # If an exception occurs in prepare phase, rollback all services that prepared successfully.
            for svc in prepared_services:
                try:
                    svc.rollback(transaction_id)
                except Exception:
                    pass
            raise e