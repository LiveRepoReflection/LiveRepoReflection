import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_transactions(microservices, transactions):
    # Build a mapping for each microservice with its concurrency semaphore.
    service_map = {}
    for ms in microservices:
        service_map[ms['name']] = {
            'service': ms,
            'semaphore': threading.Semaphore(ms['max_concurrency'])
        }

    def process_single_transaction(tx):
        tx_id = tx['id']
        involved = tx['involved_services']
        prepare_success = True

        # Prepare Phase: Try to prepare on all involved microservices.
        for svc_name in involved:
            if svc_name not in service_map:
                prepare_success = False
                break
            sem = service_map[svc_name]['semaphore']
            ms = service_map[svc_name]['service']
            # Acquire semaphore non-blocking to respect concurrency limits.
            acquired = sem.acquire(blocking=False)
            if not acquired:
                prepare_success = False
                break
            try:
                result = ms['prepare'](tx_id, tx['data'])
                if result is not True:
                    prepare_success = False
                    break
            except Exception:
                prepare_success = False
                break
            finally:
                sem.release()

        if not prepare_success:
            return {'id': tx_id, 'status': 'ABORTED'}

        # Commit Phase: For each involved microservice, attempt commit with retries.
        for svc_name in involved:
            sem = service_map[svc_name]['semaphore']
            ms = service_map[svc_name]['service']
            retries = 0
            commit_done = False
            while retries < 3 and not commit_done:
                acquired = sem.acquire(timeout=1)
                if not acquired:
                    retries += 1
                    continue
                try:
                    ms['commit'](tx_id)
                    commit_done = True
                except Exception:
                    retries += 1
                    time.sleep(0.01)  # brief delay before retrying
                finally:
                    sem.release()
            if not commit_done:
                # Log error if commit still fails after retries, but do not abort overall transaction.
                print(f"Error: commit failed for service {svc_name} in transaction {tx_id}")

        return {'id': tx_id, 'status': 'COMMITTED'}

    results = []
    # Process transactions concurrently.
    with ThreadPoolExecutor(max_workers=len(transactions)) as executor:
        future_to_tx = {executor.submit(process_single_transaction, tx): tx for tx in transactions}
        for future in as_completed(future_to_tx):
            results.append(future.result())
    return results