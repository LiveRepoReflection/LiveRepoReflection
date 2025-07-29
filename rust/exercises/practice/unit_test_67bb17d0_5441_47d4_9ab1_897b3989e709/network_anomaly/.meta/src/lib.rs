use std::collections::{HashMap, VecDeque};

#[derive(Debug, Clone)]
pub struct ConnectionRecord {
    pub timestamp: u64,
    pub source_ip: String,
    pub destination_ip: String,
    pub source_port: u16,
    pub destination_port: u16,
    pub protocol: String,
    pub packet_size: u32,
}

// This struct maintains a sliding window for packet sizes.
// It keeps the sum and sum of squares to compute mean and standard deviation efficiently.
struct SlidingWindow {
    window: VecDeque<f64>,
    sum: f64,
    sum_sq: f64,
    capacity: usize,
}

impl SlidingWindow {
    fn new(capacity: usize) -> Self {
        SlidingWindow {
            window: VecDeque::with_capacity(capacity),
            sum: 0.0,
            sum_sq: 0.0,
            capacity,
        }
    }

    // Add a new value to the sliding window,
    // remove the oldest value if the window is full.
    fn add(&mut self, value: f64) {
        if self.window.len() == self.capacity {
            if let Some(old) = self.window.pop_front() {
                self.sum -= old;
                self.sum_sq -= old * old;
            }
        }
        self.window.push_back(value);
        self.sum += value;
        self.sum_sq += value * value;
    }

    // Returns the mean of the window.
    fn mean(&self) -> f64 {
        if self.window.is_empty() {
            0.0
        } else {
            self.sum / self.window.len() as f64
        }
    }

    // Returns the standard deviation of the window.
    fn std_dev(&self) -> f64 {
        let n = self.window.len() as f64;
        if n == 0.0 {
            0.0
        } else {
            let mean = self.mean();
            // variance = (sum_sq / n) - (mean^2)
            let variance = (self.sum_sq / n) - (mean * mean);
            if variance < 0.0 {
                0.0
            } else {
                variance.sqrt()
            }
        }
    }
}

// Key based on the combination of source_ip, destination_ip, and protocol.
type Key = (String, String, String);

// Public function to detect anomalies. The first `baseline_size` records are used to
// establish the baseline for each key. For each subsequent record, an anomaly is detected
// if its packet_size deviates by more than `threshold` standard deviations from the baseline mean.
pub fn detect_anomalies(records: Vec<ConnectionRecord>, baseline_size: usize, threshold: f64) -> Vec<bool> {
    // Map to store sliding windows for each key.
    let mut baseline_map: HashMap<Key, SlidingWindow> = HashMap::new();
    let mut anomalies = Vec::new();

    // Process each record in order.
    for (i, record) in records.into_iter().enumerate() {
        let key = (record.source_ip.clone(), record.destination_ip.clone(), record.protocol.clone());
        // Initialize sliding window for new keys.
        let window = baseline_map.entry(key.clone()).or_insert_with(|| SlidingWindow::new(baseline_size));

        // For the first `baseline_size` records overall, we are building the baseline for each key.
        if i < baseline_size {
            window.add(record.packet_size as f64);
            // No anomaly check during baseline establishment.
            continue;
        } else {
            // If the window is empty, it is a cold start, treat as normal.
            if window.window.is_empty() {
                anomalies.push(false);
                window.add(record.packet_size as f64);
                continue;
            }
            let mean = window.mean();
            let std_dev = window.std_dev();

            // Determine if the record is anomalous.
            let anomaly = if std_dev == 0.0 {
                // If std_dev is zero, if value deviates from the mean, it's anomalous.
                (record.packet_size as f64 - mean).abs() > 0.0
            } else {
                (record.packet_size as f64 - mean).abs() > threshold * std_dev
            };

            anomalies.push(anomaly);
            window.add(record.packet_size as f64);
        }
    }
    anomalies
}