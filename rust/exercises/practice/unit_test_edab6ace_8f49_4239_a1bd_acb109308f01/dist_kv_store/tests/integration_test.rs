use std::future::Future;
use std::pin::Pin;
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};
use std::thread;
use std::time::Duration;

// A simple async executor to run our futures to completion.
fn noop_raw_waker() -> RawWaker {
    fn no_op(_: *const ()) {}
    fn clone(_: *const ()) -> RawWaker {
        noop_raw_waker()
    }
    static VTABLE: RawWakerVTable =
        RawWakerVTable::new(clone, no_op, no_op, no_op);
    RawWaker::new(std::ptr::null(), &VTABLE)
}

fn noop_waker() -> Waker {
    unsafe { Waker::from_raw(noop_raw_waker()) }
}

fn block_on<F: Future>(mut fut: F) -> F::Output {
    let waker = noop_waker();
    let mut context = Context::from_waker(&waker);
    // Safety: we will never move the future after pinning.
    let mut fut = unsafe { Pin::new_unchecked(&mut fut) };
    loop {
        match fut.as_mut().poll(&mut context) {
            Poll::Ready(val) => return val,
            Poll::Pending => {
                // In a real executor, we would yield control until the waker is signaled.
                thread::sleep(Duration::from_millis(10));
            }
        }
    }
}

// Assume the following API is defined in the library:
// - DistKVStore::new(node_count: usize) -> Self
// - async fn put(&self, key: String, value: String) -> Result<(), String>
// - async fn get(&self, key: String) -> Result<Option<String>, String>
// - async fn delete(&self, key: String) -> Result<bool, String>
// - async fn begin_transaction(&self) -> Result<Transaction, String>
// - Transaction has async fn put(&mut self, key: String, value: String) -> Result<(), String>
//                async fn get(&mut self, key: String) -> Result<Option<String>, String>
//                async fn delete(&mut self, key: String) -> Result<bool, String>
//                async fn commit(self) -> Result<(), String>
//                async fn rollback(self) -> Result<(), String>
// - async fn simulate_failure(&self, node_index: usize) -> Result<(), String>
// - The API methods are asynchronous and return a Result with error description as String.
//
// For the purpose of these tests, we assume that such methods are implemented.

use dist_kv_store::{DistKVStore, Transaction};

#[test]
fn test_basic_operations() {
    let store = DistKVStore::new(3);
    // Test put
    block_on(async {
        store.put("key1".to_string(), "value1".to_string()).await.expect("put failed");
    });
    // Test get
    let value = block_on(async {
        store.get("key1".to_string()).await.expect("get failed")
    });
    assert_eq!(value, Some("value1".to_string()));
    // Test delete
    let deleted = block_on(async {
        store.delete("key1".to_string()).await.expect("delete failed")
    });
    assert!(deleted);
    // Get after delete
    let value = block_on(async { store.get("key1".to_string()).await.expect("get failed") });
    assert_eq!(value, None);
}

#[test]
fn test_transaction_commit() {
    let store = DistKVStore::new(3);
    block_on(async {
        // Pre-populate with a key.
        store.put("tx_key".to_string(), "initial".to_string()).await.expect("put failed");
        // Begin a transaction.
        let mut tx = store.begin_transaction().await.expect("failed to begin transaction");
        // Update the key.
        tx.put("tx_key".to_string(), "updated".to_string())
            .await
            .expect("transaction put failed");
        // Insert a new key.
        tx.put("new_key".to_string(), "new_value".to_string())
            .await
            .expect("transaction put failed");
        // Commit the transaction.
        tx.commit().await.expect("commit failed");
    });
    // Validate changes after commit.
    let value = block_on(async { store.get("tx_key".to_string()).await.expect("get failed") });
    assert_eq!(value, Some("updated".to_string()));
    let new_value = block_on(async { store.get("new_key".to_string()).await.expect("get failed") });
    assert_eq!(new_value, Some("new_value".to_string()));
}

#[test]
fn test_transaction_rollback() {
    let store = DistKVStore::new(3);
    block_on(async {
        // Pre-populate with a key.
        store.put("roll_key".to_string(), "initial".to_string())
            .await.expect("put failed");
        // Begin a transaction.
        let mut tx = store.begin_transaction().await.expect("failed to begin transaction");
        // Modify the key.
        tx.put("roll_key".to_string(), "modified".to_string())
            .await.expect("transaction put failed");
        // Insert another key.
        tx.put("temp_key".to_string(), "temp_value".to_string())
            .await.expect("transaction put failed");
        // Rollback the transaction.
        tx.rollback().await.expect("rollback failed");
    });
    // Validate that no changes took effect:
    let value = block_on(async { store.get("roll_key".to_string()).await.expect("get failed") });
    assert_eq!(value, Some("initial".to_string()));
    let temp_value = block_on(async { store.get("temp_key".to_string()).await.expect("get failed") });
    assert_eq!(temp_value, None);
}

#[test]
fn test_fault_tolerance() {
    let store = DistKVStore::new(5);
    block_on(async {
        // Pre-populate the store
        for i in 0..10 {
            let key = format!("key_fault_{}", i);
            let value = format!("value_fault_{}", i);
            store.put(key.clone(), value.clone()).await.expect("put failed");
        }
        // Simulate failure on one node (assume node 2 fails)
        store.simulate_failure(2).await.expect("simulate failure failed");
        // Continue with operations
        store.put("post_fail_key".to_string(), "post_fail_value".to_string())
            .await.expect("put after failure failed");
        let val = store.get("post_fail_key".to_string()).await.expect("get after failure failed");
        assert_eq!(val, Some("post_fail_value".to_string()));
        // Ensure all pre-populated keys are still available.
        for i in 0..10 {
            let key = format!("key_fault_{}", i);
            let expected = format!("value_fault_{}", i);
            let value = store.get(key).await.expect("get failed");
            assert_eq!(value, Some(expected));
        }
    });
}

#[test]
fn test_concurrent_requests() {
    let store = Arc::new(DistKVStore::new(3));
    let mut handles = vec![];

    // Spawn threads that perform put operations concurrently.
    for i in 0..5 {
        let store_clone = Arc::clone(&store);
        let handle = thread::spawn(move || {
            block_on(async {
                for j in 0..20 {
                    let key = format!("concurrent_{}_{}", i, j);
                    let value = format!("value_{}_{}", i, j);
                    store_clone.put(key, value).await.expect("concurrent put failed");
                }
            });
        });
        handles.push(handle);
    }
    // Wait for all threads to finish.
    for handle in handles {
        handle.join().expect("thread panicked");
    }
    // Validate concurrent writes
    block_on(async {
        for i in 0..5 {
            for j in 0..20 {
                let key = format!("concurrent_{}_{}", i, j);
                let value = store.get(key).await.expect("get failed");
                assert!(value.is_some());
            }
        }
    });
}