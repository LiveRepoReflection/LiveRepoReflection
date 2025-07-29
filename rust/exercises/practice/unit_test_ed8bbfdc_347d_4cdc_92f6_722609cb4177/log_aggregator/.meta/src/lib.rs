use std::collections::HashSet;

pub const ONE_HOUR_MS: u64 = 3600000;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LogEntry {
    pub timestamp: u64,
    pub service_id: u32,
    pub transaction_id: u64,
    pub log_message: String,
}

pub fn aggregate_logs(logs: Vec<LogEntry>, current_time: u64) -> Vec<LogEntry> {
    let mut unique_logs = Vec::with_capacity(logs.len());
    let mut seen = HashSet::new();
    let lower_bound = current_time.saturating_sub(ONE_HOUR_MS);

    for log in logs.into_iter() {
        if log.timestamp < lower_bound {
            continue;
        }
        if seen.contains(&log.transaction_id) {
            continue;
        }
        seen.insert(log.transaction_id);
        unique_logs.push(log);
    }
    unique_logs.sort_by_key(|log| log.timestamp);
    unique_logs
}