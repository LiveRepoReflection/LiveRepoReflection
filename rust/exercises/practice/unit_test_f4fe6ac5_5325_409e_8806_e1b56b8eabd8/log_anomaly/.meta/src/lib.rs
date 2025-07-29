use std::collections::HashMap;
use std::error::Error;

#[derive(Debug, PartialEq, Eq)]
pub struct LogEntry {
    pub timestamp: u64,
    pub server_id: String,
    pub log_level: String,
    pub message: String,
}

#[derive(Debug, PartialEq)]
pub struct AnomalyReport {
    pub server_id: String,
    pub log_level: String,
    pub worker_id: usize,
    pub current_count: f64,
    pub global_avg: f64,
}

pub fn parse_log_entry(log: &str) -> Result<LogEntry, Box<dyn Error>> {
    let parts: Vec<&str> = log.splitn(4, ',').collect();
    if parts.len() != 4 {
        return Err("Invalid log format".into());
    }
    let timestamp: u64 = parts[0].trim().parse()?;
    let server_id = parts[1].trim().to_string();
    let log_level = parts[2].trim().to_string();
    let message = parts[3].trim().to_string();
    Ok(LogEntry {
        timestamp,
        server_id,
        log_level,
        message,
    })
}

pub fn worker_aggregate(logs: &[String], _time_window: u64, _aggregation_interval: u64) -> HashMap<(String, String), f64> {
    let mut counts: HashMap<(String, String), f64> = HashMap::new();
    // In a real system, you would filter logs based on the provided time_window.
    // For simplicity, we aggregate all provided logs.
    for log in logs {
        if let Ok(entry) = parse_log_entry(log) {
            let key = (entry.server_id, entry.log_level);
            *counts.entry(key).or_insert(0.0) += 1.0;
        }
    }
    counts
}

pub fn coordinator_detect(workers_stats: &[HashMap<(String, String), f64>], anomaly_threshold: f64) -> Vec<AnomalyReport> {
    let mut global_totals: HashMap<(String, String), (f64, usize)> = HashMap::new();
    // Sum up counts for each (server_id, log_level) from all workers.
    for stats in workers_stats {
        for (key, count) in stats {
            let entry = global_totals.entry(key.clone()).or_insert((0.0, 0));
            entry.0 += count;
            entry.1 += 1;
        }
    }

    let mut global_avg: HashMap<(String, String), f64> = HashMap::new();
    for (key, (total, workers)) in &global_totals {
        let avg = total / *workers as f64;
        global_avg.insert(key.clone(), avg);
    }

    let mut anomalies = Vec::new();
    // Evaluate each worker's counts against the global average.
    for (worker_id, stats) in workers_stats.iter().enumerate() {
        for (key, &worker_count) in stats {
            if let Some(&avg) = global_avg.get(key) {
                // Calculate the deviation ratio.
                let ratio = if worker_count > avg {
                    worker_count / avg
                } else {
                    avg / worker_count
                };
                if ratio > anomaly_threshold {
                    anomalies.push(AnomalyReport {
                        server_id: key.0.clone(),
                        log_level: key.1.clone(),
                        worker_id,
                        current_count: worker_count,
                        global_avg: avg,
                    });
                }
            }
        }
    }
    anomalies
}