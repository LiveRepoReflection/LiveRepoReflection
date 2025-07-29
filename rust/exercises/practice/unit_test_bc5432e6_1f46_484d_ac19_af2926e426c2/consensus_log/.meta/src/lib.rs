use std::fmt;

#[derive(Debug, PartialEq)]
pub enum LogError {
    InvalidCommitIndex,
    LogConflict,
    InvalidEntryIndex,
    Other(String),
}

impl fmt::Display for LogError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LogError::InvalidCommitIndex => write!(f, "Invalid commit index"),
            LogError::LogConflict => write!(f, "Log conflict detected"),
            LogError::InvalidEntryIndex => write!(f, "Invalid entry index"),
            LogError::Other(msg) => write!(f, "Other error: {}", msg),
        }
    }
}

#[derive(Clone, Debug)]
struct LogEntry {
    term: u64,
    index: u64,
    payload: Vec<u8>,
}

pub struct Log {
    entries: Vec<LogEntry>,
    commit_index: u64,
}

impl Log {
    pub fn new() -> Self {
        Log {
            entries: Vec::new(),
            commit_index: 0,
        }
    }

    pub fn append(&mut self, term: u64, payload: Vec<u8>) -> Result<u64, LogError> {
        let index = self.entries.len() as u64 + 1;
        let entry = LogEntry { term, index, payload };
        self.entries.push(entry);
        Ok(index)
    }

    pub fn entries(&self, start_index: u64, max_entries: usize) -> Result<Vec<(u64, u64, Vec<u8>)>, LogError> {
        if start_index < 1 {
            return Err(LogError::InvalidEntryIndex);
        }
        let start = (start_index - 1) as usize;
        if start > self.entries.len() {
            return Ok(Vec::new());
        }
        let end = usize::min(start + max_entries, self.entries.len());
        let slice = &self.entries[start..end];
        let result = slice.iter().map(|entry| (entry.term, entry.index, entry.payload.clone())).collect();
        Ok(result)
    }

    pub fn match_entries(&mut self, incoming: Vec<(u64, u64, Vec<u8>)>) -> Result<u64, LogError> {
        let mut last_matching_index = 0;
        for (entry_term, entry_index, payload) in incoming.into_iter() {
            let current_len = self.entries.len() as u64;
            if entry_index <= current_len {
                let existing = &self.entries[(entry_index - 1) as usize];
                if existing.term != entry_term || existing.payload != payload {
                    return Err(LogError::LogConflict);
                }
                last_matching_index = entry_index;
            } else if entry_index == current_len + 1 {
                // Append new entry
                let new_entry = LogEntry { term: entry_term, index: entry_index, payload };
                self.entries.push(new_entry);
                last_matching_index = entry_index;
            } else {
                return Err(LogError::InvalidEntryIndex);
            }
        }
        Ok(last_matching_index)
    }

    pub fn commit(&mut self, index: u64) -> Result<(), LogError> {
        if index > self.entries.len() as u64 || index < self.commit_index {
            return Err(LogError::InvalidCommitIndex);
        }
        self.commit_index = index;
        Ok(())
    }

    pub fn last_log_term_index(&self) -> (u64, u64) {
        if let Some(last) = self.entries.last() {
            (last.term, last.index)
        } else {
            (0, 0)
        }
    }

    pub fn last_committed_index(&self) -> u64 {
        self.commit_index
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{Arc, Barrier, Mutex};
    use std::thread;

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