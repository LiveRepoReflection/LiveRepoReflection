import asyncio
import logging
from collections import deque, defaultdict

logging.basicConfig(level=logging.INFO)

class ServiceException(Exception):
    pass

class AccountServiceException(ServiceException):
    pass

class TransactionLogServiceException(ServiceException):
    pass

async def call_service(service_name, operation, data):
    await asyncio.sleep(0.1)
    logging.info(f"Calling {service_name}.{operation} with data: {data}")
    if service_name == "AccountService" and operation == "DebitAccount" and data.get("amount", 0) > 500:
        raise AccountServiceException("Insufficient funds")
    if service_name == "TransactionLogService" and operation == "LogTransaction":
        if data.get("transaction_id") == "TXN-002":
            raise TransactionLogServiceException("Transaction Log Service unavailable")
    return "success"

async def execute_transaction(transaction_definition):
    if not isinstance(transaction_definition, dict):
        raise ValueError("Transaction definition must be a dictionary.")

    # Build dependency graph and in-degree mapping
    in_degree = {txn: 0 for txn in transaction_definition}
    graph = defaultdict(list)
    for txn_id, details in transaction_definition.items():
        dependencies = details.get("dependencies", [])
        if not isinstance(dependencies, list):
            raise ValueError("Dependencies must be a list.")
        for dep in dependencies:
            if dep not in transaction_definition:
                raise ValueError(f"Dependency {dep} for transaction {txn_id} not found in transaction definition.")
            graph[dep].append(txn_id)
            in_degree[txn_id] += 1

    # Topological sort and level computation
    topo_order = []
    level = {}
    queue = deque()
    for txn_id in transaction_definition:
        if in_degree[txn_id] == 0:
            queue.append(txn_id)
            level[txn_id] = 0

    while queue:
        current = queue.popleft()
        topo_order.append(current)
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            level[neighbor] = max(level.get(neighbor, 0), level[current] + 1)
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(topo_order) != len(transaction_definition):
        raise Exception("Invalid DAG: cycle detected in transaction definition.")

    # Group transactions by level for asynchronous concurrent execution
    level_groups = defaultdict(list)
    for txn_id, lvl in level.items():
        level_groups[lvl].append(txn_id)

    executed_order = []
    failure_occurred = False

    async def execute_txn_call(txn_id, details):
        result = await call_service(details["service"], details["operation"], details["data"])
        return txn_id

    sorted_levels = sorted(level_groups.keys())
    for lvl in sorted_levels:
        tasks = []
        txn_ids = level_groups[lvl]
        for txn_id in txn_ids:
            details = transaction_definition[txn_id]
            tasks.append(asyncio.create_task(execute_txn_call(txn_id, details)))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for txn_id, res in zip(txn_ids, results):
            if isinstance(res, Exception):
                logging.error(f"Transaction {txn_id} failed with error: {res}")
                failure_occurred = True
            else:
                logging.info(f"Transaction {txn_id} succeeded.")
                executed_order.append(txn_id)
        if failure_occurred:
            break

    if failure_occurred:
        logging.info("Initiating compensating transactions.")
        for txn_id in reversed(executed_order):
            comp_details = transaction_definition[txn_id]
            try:
                await call_service(comp_details["service"], comp_details["compensating_operation"], comp_details["compensating_data"])
                logging.info(f"Compensation for {txn_id} succeeded.")
            except Exception as e:
                logging.error(f"Compensation for {txn_id} failed with error: {e}")
        return False

    return True