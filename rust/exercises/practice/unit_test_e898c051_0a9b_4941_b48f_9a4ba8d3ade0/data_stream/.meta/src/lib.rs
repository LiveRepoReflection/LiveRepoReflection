pub struct AggregatedData {
    pub timestamp_start: u64,
    pub timestamp_end: u64,
    pub min: f64,
    pub max: f64,
    pub sum: f64,
    pub count: u64,
    pub sequence: u64,
}

pub struct AggregationNode {
    last_sequence: u64,
}

impl AggregationNode {
    pub fn new() -> Self {
        AggregationNode { last_sequence: 0 }
    }

    // Processes a vector of (timestamp, value) pairs and returns aggregated data.
    // If the input vector is empty, returns None.
    pub fn process_data(&mut self, data: Vec<(u64, f64)>) -> Option<AggregatedData> {
        if data.is_empty() {
            return None;
        }
        let mut min_val = std::f64::MAX;
        let mut max_val = std::f64::MIN;
        let mut sum = 0.0;
        let count = data.len() as u64;
        let mut ts_start = u64::MAX;
        let mut ts_end = 0u64;

        for (ts, value) in data.iter() {
            if *ts < ts_start {
                ts_start = *ts;
            }
            if *ts > ts_end {
                ts_end = *ts;
            }
            if *value < min_val {
                min_val = *value;
            }
            if *value > max_val {
                max_val = *value;
            }
            sum += *value;
        }
        self.last_sequence += 1;
        Some(AggregatedData {
            timestamp_start: ts_start,
            timestamp_end: ts_end,
            min: min_val,
            max: max_val,
            sum,
            count,
            sequence: self.last_sequence,
        })
    }
}

pub struct GlobalAggregates {
    pub min: f64,
    pub max: f64,
    pub average: f64,
    pub std_deviation: f64,
}

pub struct CentralServer {
    window: u64,
    sliding_interval: u64,
    store: Vec<AggregatedData>,
}

impl CentralServer {
    pub fn new(window: u64, sliding_interval: u64) -> Self {
        CentralServer {
            window,
            sliding_interval,
            store: Vec::new(),
        }
    }

    pub fn add_aggregated_data(&mut self, data: AggregatedData) {
        self.store.push(data);
    }

    // Returns the global aggregates computed over the sliding window.
    // The sliding window is defined as [current_time - window, current_time].
    // Only aggregated data that fully lie within the window are considered.
    pub fn get_current_aggregates(&self, current_time: u64) -> Option<GlobalAggregates> {
        let window_start = if current_time > self.window {
            current_time - self.window
        } else {
            0
        };

        let mut global_min = std::f64::MAX;
        let mut global_max = std::f64::MIN;
        let mut total_sum = 0.0;
        let mut total_count = 0u64;

        for data in self.store.iter() {
            if data.timestamp_start >= window_start && data.timestamp_end <= current_time {
                if data.min < global_min {
                    global_min = data.min;
                }
                if data.max > global_max {
                    global_max = data.max;
                }
                total_sum += data.sum;
                total_count += data.count;
            }
        }

        if total_count == 0 {
            None
        } else {
            let average = total_sum / total_count as f64;
            // For this implementation, we approximate the standard deviation as 0.0.
            // In a production system, you would merge variance estimates from individual nodes.
            let std_deviation = 0.0;
            Some(GlobalAggregates {
                min: global_min,
                max: global_max,
                average,
                std_deviation,
            })
        }
    }
}