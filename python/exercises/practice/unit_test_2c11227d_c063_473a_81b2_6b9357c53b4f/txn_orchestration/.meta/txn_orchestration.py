import asyncio
import uuid
import logging

logging.basicConfig(level=logging.ERROR)


async def orchestrate_transaction(transaction_graph, services, compensating_transactions, initial_payload):
    transaction_id = uuid.uuid4()
    # Dictionary to record the state of each operation.
    # Valid states: "pending", "running", "completed", "failed", "compensated", "compensate_failed"
    state = {op_id: "pending" for op_id in transaction_graph.keys()}
    # List to record the order in which operations completed successfully.
    execution_history = []
    # Lock for synchronizing state and history modifications.
    lock = asyncio.Lock()

    async def execute_operation(op_id):
        nonlocal state, execution_history
        op_detail = transaction_graph[op_id]
        service_name = op_detail["service"]
        operation_name = op_detail["operation"]
        service_fn = services[service_name][operation_name]

        async with lock:
            state[op_id] = "running"
        try:
            result = await service_fn(transaction_id, initial_payload)
            async with lock:
                if result:
                    state[op_id] = "completed"
                    execution_history.append(op_id)
                else:
                    state[op_id] = "failed"
                    logging.error(f"Operation {op_id} from {service_name}.{operation_name} failed.")
        except Exception as e:
            async with lock:
                state[op_id] = "failed"
            logging.error(f"Exception in operation {op_id} from {service_name}.{operation_name}: {e}")

    # Helper function to check if an operation is ready to run.
    async def is_ready(op_id):
        deps = transaction_graph[op_id]["dependencies"]
        async with lock:
            # An op is ready if it is pending and all its dependencies are completed.
            return state[op_id] == "pending" and all(state.get(dep) == "completed" for dep in deps)

    # Main execution loop: run ready operations concurrently in rounds.
    while True:
        ready_ops = []
        for op_id in transaction_graph:
            # Check readiness without blocking the loop.
            if await is_ready(op_id):
                ready_ops.append(op_id)
        if not ready_ops:
            # No ready operations found.
            break

        # Execute all ready operations concurrently.
        tasks = [asyncio.create_task(execute_operation(op_id)) for op_id in ready_ops]
        await asyncio.gather(*tasks)

        # If any operation in this round failed, break out to initiate rollback.
        async with lock:
            if any(state[op_id] == "failed" for op_id in ready_ops):
                break

    # If any operation has failed, initiate rollback for successfully completed operations.
    if any(state[op] == "failed" for op in transaction_graph):
        # Rollback in the reverse order of successful execution.
        for op_id in reversed(execution_history):
            service_name = transaction_graph[op_id]["service"]
            operation_name = transaction_graph[op_id]["operation"]
            compensating_fn = compensating_transactions[service_name][operation_name]
            try:
                comp_result = await compensating_fn(transaction_id, initial_payload)
                async with lock:
                    if comp_result:
                        state[op_id] = "compensated"
                    else:
                        state[op_id] = "compensate_failed"
                        logging.error(f"Compensation for operation {op_id} ({service_name}.{operation_name}) returned False.")
            except Exception as e:
                async with lock:
                    state[op_id] = "compensate_failed"
                logging.error(f"Exception during compensation for operation {op_id} ({service_name}.{operation_name}): {e}")

    return state