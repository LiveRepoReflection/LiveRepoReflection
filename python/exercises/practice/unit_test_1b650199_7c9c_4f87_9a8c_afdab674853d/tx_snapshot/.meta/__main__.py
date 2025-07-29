import time
import threading
import random
from .tx_snapshot import DistributedTransactionManager

def run_simple_example():
    """Run a simple example to demonstrate the DTM in action."""
    # Create a DTM with 3 shards
    dtm = DistributedTransactionManager(num_shards=3)
    
    # Start a transaction and add some data
    print("Creating initial data...")
    tid = dtm.begin_transaction()
    dtm.write(tid, 0, "key1", "value1")
    dtm.write(tid, 1, "key2", "value2")
    dtm.write(tid, 2, "key3", "value3")
    if dtm.commit_transaction(tid):
        print("Initial data committed successfully.")
    else:
        print("Failed to commit initial data.")
    
    # Start a long-running transaction to demonstrate snapshot isolation
    print("\nStarting a long-running transaction...")
    tid1 = dtm.begin_transaction()
    val1 = dtm.read(tid1, 0, "key1")
    print(f"Transaction {tid1} reads key1 = {val1}")
    
    # Start another transaction that modifies key1
    print("\nStarting another transaction that modifies key1...")
    tid2 = dtm.begin_transaction()
    dtm.write(tid2, 0, "key1", "new_value1")
    if dtm.commit_transaction(tid2):
        print(f"Transaction {tid2} committed successfully, changing key1 to new_value1")
    
    # The first transaction should still see the old value
    val1_again = dtm.read(tid1, 0, "key1")
    print(f"Transaction {tid1} still reads key1 = {val1_again} (demonstrating snapshot isolation)")
    
    # Trying to update the same key in the first transaction will cause a conflict
    print("\nTrying to modify key1 in the first transaction...")
    dtm.write(tid1, 0, "key1", "conflict_value")
    if dtm.commit_transaction(tid1):
        print("Transaction committed successfully (unexpected).")
    else:
        print("Transaction failed to commit due to write conflict (as expected).")
    
    # Start a new transaction to see the current state
    print("\nChecking current state of the database...")
    tid3 = dtm.begin_transaction()
    for shard_id, key in [(0, "key1"), (1, "key2"), (2, "key3")]:
        value = dtm.read(tid3, shard_id, key)
        print(f"Shard {shard_id}, {key} = {value}")
    dtm.commit_transaction(tid3)

def worker(dtm, worker_id, num_ops):
    """Worker function for concurrent transaction testing."""
    successes = 0
    failures = 0
    
    for i in range(num_ops):
        # Start a transaction
        tid = dtm.begin_transaction()
        
        # Perform some reads and writes
        shard_id = random.randint(0, dtm.num_shards - 1)
        key = f"key{random.randint(0, 9)}"
        
        # Read the current value
        current_value = dtm.read(tid, shard_id, key)
        
        # Write a new value
        new_value = f"value{worker_id}-{i}"
        dtm.write(tid, shard_id, key, new_value)
        
        # Try to commit
        if dtm.commit_transaction(tid):
            successes += 1
        else:
            failures += 1
    
    return successes, failures

def run_concurrency_test():
    """Run a concurrency test with multiple threads."""
    print("\nRunning concurrency test...")
    
    # Create a DTM with 5 shards
    dtm = DistributedTransactionManager(num_shards=5)
    
    # Create some initial data
    tid = dtm.begin_transaction()
    for i in range(10):
        dtm.write(tid, i % 5, f"key{i}", f"initial{i}")
    dtm.commit_transaction(tid)
    
    # Create threads
    num_threads = 10
    num_ops_per_thread = 50
    threads = []
    results = [None] * num_threads
    
    def thread_func(thread_id):
        successes, failures = worker(dtm, thread_id, num_ops_per_thread)
        results[thread_id] = (successes, failures)
    
    # Start threads
    start_time = time.time()
    for i in range(num_threads):
        t = threading.Thread(target=thread_func, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # Calculate statistics
    total_ops = num_threads * num_ops_per_thread
    total_successes = sum(r[0] for r in results)
    total_failures = sum(r[1] for r in results)
    duration = end_time - start_time
    
    print(f"Concurrency test completed in {duration:.2f} seconds")
    print(f"Total operations: {total_ops}")
    print(f"Successful commits: {total_successes}")
    print(f"Failed commits: {total_failures}")
    print(f"Success rate: {total_successes/total_ops*100:.1f}%")
    print(f"Transactions per second: {total_ops/duration:.1f}")

if __name__ == "__main__":
    run_simple_example()
    run_concurrency_test()