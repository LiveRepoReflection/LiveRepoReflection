use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Copy, Hash, Eq, PartialEq)]
pub enum LogLevel {
    INFO,
    WARN,
    ERROR,
}

#[derive(Debug, Clone)]
pub struct LogEntry {
    pub timestamp: u64,
    pub server_id: String,
    pub log_level: LogLevel,
    pub message: String,
}

struct TimeWindow {
    counts: HashMap<LogLevel, usize>,
    start_time: u64,
    end_time: u64,
}

impl TimeWindow {
    fn new(start_time: u64, end_time: u64) -> Self {
        TimeWindow {
            counts: HashMap::new(),
            start_time,
            end_time,
        }
    }

    fn increment(&mut self, level: LogLevel) {
        *self.counts.entry(level).or_insert(0) += 1;
    }

    fn get_count(&self, level: LogLevel) -> usize {
        *self.counts.get(&level).unwrap_or(&0)
    }
}

pub struct LogAggregator {
    windows: Arc<RwLock<Vec<TimeWindow>>>,
    window_duration: u64,
}

impl LogAggregator {
    pub fn new(window_duration: u64) -> Self {
        LogAggregator {
            windows: Arc::new(RwLock::new(Vec::new())),
            window_duration,
        }
    }

    fn current_time() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
    }

    fn cleanup_old_windows(&self, current_time: u64) {
        if let Ok(mut windows) = self.windows.write() {
            windows.retain(|window| window.end_time > current_time - self.window_duration);
        }
    }

    pub fn process_batch(&self, entries: Vec<LogEntry>) {
        let current_time = Self::current_time();
        self.cleanup_old_windows(current_time);

        // Group entries by their timestamp windows
        let mut window_entries: HashMap<(u64, u64), Vec<LogEntry>> = HashMap::new();
        
        for entry in entries {
            if entry.timestamp > current_time - self.window_duration {
                let window_start = (entry.timestamp / 60) * 60;
                let window_end = window_start + 60;
                window_entries
                    .entry((window_start, window_end))
                    .or_insert_with(Vec::new)
                    .push(entry);
            }
        }

        if let Ok(mut windows) = self.windows.write() {
            // Process each window
            for ((start_time, end_time), entries) in window_entries {
                let mut window = TimeWindow::new(start_time, end_time);
                
                // Count log levels in this window
                for entry in entries {
                    window.increment(entry.log_level);
                }

                // Insert the window in sorted order
                let insert_pos = windows
                    .binary_search_by_key(&start_time, |w| w.start_time)
                    .unwrap_or_else(|pos| pos);
                windows.insert(insert_pos, window);
            }
        }
    }

    pub fn query_count(&self, level: LogLevel) -> usize {
        let current_time = Self::current_time();
        self.cleanup_old_windows(current_time);

        if let Ok(windows) = self.windows.read() {
            windows
                .iter()
                .map(|window| window.get_count(level))
                .sum()
        } else {
            0
        }
    }
}

impl Default for LogAggregator {
    fn default() -> Self {
        Self::new(60) // Default 60-second window
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_window() {
        let aggregator = LogAggregator::new(60);
        let current_time = LogAggregator::current_time();
        
        let entries = vec![
            LogEntry {
                timestamp: current_time,
                server_id: "test1".to_string(),
                log_level: LogLevel::INFO,
                message: "test message".to_string(),
            }
        ];
        
        aggregator.process_batch(entries);
        assert_eq!(aggregator.query_count(LogLevel::INFO), 1);
        assert_eq!(aggregator.query_count(LogLevel::ERROR), 0);
    }

    #[test]
    fn test_multiple_windows() {
        let aggregator = LogAggregator::new(120); // 2-minute window
        let current_time = LogAggregator::current_time();
        
        let entries = vec![
            LogEntry {
                timestamp: current_time - 30,
                server_id: "test1".to_string(),
                log_level: LogLevel::INFO,
                message: "test message 1".to_string(),
            },
            LogEntry {
                timestamp: current_time - 90,
                server_id: "test2".to_string(),
                log_level: LogLevel::INFO,
                message: "test message 2".to_string(),
            }
        ];
        
        aggregator.process_batch(entries);
        assert_eq!(aggregator.query_count(LogLevel::INFO), 2);
    }
}