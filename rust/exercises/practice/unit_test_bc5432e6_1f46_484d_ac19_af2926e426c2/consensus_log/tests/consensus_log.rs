use std::sync::{Arc, Barrier, Mutex};
use std::thread;
use consensus_log::{Log, LogError};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_append_and_last_log() {
        let mut log = Log::new();
        let payload1 = vec![1, 2, 3];
        let index1 = log.append(1, payload1.clone()).expect("append failed");
        assert_eq!(index1, 1);

        let (last_term, last_index) = log.last_log_term_index();
        assert_eq!(last_term, 1);
        assert_eq!(last_index, 1);

        let payload2 = vec![4, 5];
        let index2 = log.append(2, payload2.clone()).expect("append failed");
        assert_eq!(index2, 2);

        let (term, index) = log.last_log_term_index();
        assert_eq!(term, 2);
        assert_eq!(index, 2);
    }

    #[test]
    fn test_entries_range() {
        let mut log = Log::new();
        let payloads = vec![vec![1], vec![2, 3], vec![4, 5, 6]];
        for (i, payload) in payloads.iter().enumerate() {
            let term = (i + 1) as u64;
            let idx = log.append(term, payload.clone()).expect("append failed");
            assert_eq!(idx, (i + 1) as u64);
        }

        let entries = log.entries(1, 10).expect("entries failed");
        assert_eq!(entries.len(), 3);
        for (i, (term, index, payload)) in entries.iter().enumerate() {
            assert_eq!(*term, (i + 1) as u64);
            assert_eq!(*index, (i + 1) as u64);
            assert_eq!(*payload, payloads[i]);
        }

        let entries_slice = log.entries(2, 1).expect("entries failed");
        assert_eq!(entries_slice.len(), 1);
        let (term, index, payload) = &entries_slice[0];
        assert_eq!(*term, 2);
        assert_eq!(*index, 2);
        assert_eq!(*payload, vec![2, 3]);
    }

    #[test]
    fn test_match_entries_success() {
        let mut log = Log::new();
        let initial_payloads = vec![vec![10], vec![20], vec![30]];
        for payload in initial_payloads.iter() {
            let _ = log.append(1, payload.clone()).expect("append failed");
        }

        let incoming_entries = vec![
            (1, 1, vec![10]),
            (1, 2, vec![20]),
            (1, 3, vec![30]),
        ];
        let last_index = log.match_entries(incoming_entries).expect("match_entries failed");
        assert_eq!(last_index, 3);
    }

    #[test]
    fn test_match_entries_conflict() {
        let mut log = Log::new();
        let initial_entries = vec![
            (1, vec![100]),
            (1, vec![101]),
            (2, vec![102]),
        ];
        for (term, payload) in initial_entries.iter() {
            let _ = log.append(*term, payload.clone()).expect("append failed");
        }

        let incoming_entries = vec![
            (1, 1, vec![100]),
            (2, 2, vec![201]),
            (2, 3, vec![202]),
        ];
        let result = log.match_entries(incoming_entries);
        assert!(result.is_err());
    }

    #[test]
    fn test_commit() {
        let mut log = Log::new();
        for i in 1..=5 {
            let _ = log.append(i, vec![i as u8]).expect("append failed");
        }

        assert!(log.commit(3).is_ok());
        assert_eq!(log.last_committed_index(), 3);

        let commit_result = log.commit(10);
        assert!(commit_result.is_err());
    }

    #[test]
    fn test_last_indices() {
        let mut log = Log::new();
        let (term, index) = log.last_log_term_index();
        assert_eq!(term, 0);
        assert_eq!(index, 0);
        assert_eq!(log.last_committed_index(), 0);

        let payload = vec![42];
        let _ = log.append(3, payload).expect("append failed");
        let (term, index) = log.last_log_term_index();
        assert_eq!(term, 3);
        assert_eq!(index, 1);
    }

    #[test]
    fn test_concurrent_appends() {
        let log = Arc::new(Mutex::new(Log::new()));
        let thread_count = 10;
        let appends_per_thread = 50;
        let barrier = Arc::new(Barrier::new(thread_count));
        let mut handles = Vec::new();

        for i in 0..thread_count {
            let log_clone = Arc::clone(&log);
            let barrier_clone = Arc::clone(&barrier);
            let handle = thread::spawn(move || {
                barrier_clone.wait();
                for j in 0..appends_per_thread {
                    let payload = vec![i as u8, j as u8];
                    let mut log_guard = log_clone.lock().unwrap();
                    let _ = log_guard.append(1, payload).expect("append failed");
                }
            });
            handles.push(handle);
        }
        for handle in handles {
            handle.join().expect("thread join failed");
        }

        let log_guard = log.lock().unwrap();
        let entries = log_guard.entries(1, thread_count * appends_per_thread)
            .expect("entries retrieval failed");
        assert_eq!(entries.len() as u64, (thread_count * appends_per_thread) as u64);
    }
}