use std::collections::HashMap;
use std::sync::mpsc::Sender;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

/// Represents a log message with a timestamp, a message and additional fields.
#[derive(Debug, Clone)]
pub struct LogMessage {
    pub timestamp: i64,
    pub message: String,
    pub fields: HashMap<String, String>,
}

/// A simple JSON parser for log messages that works for a limited and predictable format.
/// It expects a JSON object with keys: "timestamp" (number), "message" (string), and optionally other string fields.
fn parse_log_message(input: &str) -> Option<LogMessage> {
    let trimmed = input.trim();
    if !trimmed.starts_with('{') || !trimmed.ends_with('}') {
        return None;
    }
    // Remove the surrounding braces.
    let content = &trimmed[1..trimmed.len() - 1];
    let mut timestamp_opt: Option<i64> = None;
    let mut message_opt: Option<String> = None;
    let mut fields = HashMap::new();

    // Split by comma. Note: This is a naive split that assumes values do not contain unescaped commas.
    for pair in content.split(',') {
        let parts: Vec<&str> = pair.splitn(2, ':').collect();
        if parts.len() != 2 {
            return None;
        }
        let key = parts[0].trim().trim_matches('"');
        let value = parts[1].trim();
        // Determine if the value is a number or a string. Remove surrounding quotes if present.
        if key == "timestamp" {
            // For timestamp, value may not have quotes.
            let val_str = value.trim_matches('"');
            if let Ok(ts) = val_str.parse::<i64>() {
                timestamp_opt = Some(ts);
            } else {
                return None;
            }
        } else if key == "message" {
            let val = value.trim_matches('"').to_string();
            message_opt = Some(val);
        } else {
            let val = value.trim_matches('"').to_string();
            fields.insert(key.to_string(), val);
        }
    }
    if let (Some(timestamp), Some(message)) = (timestamp_opt, message_opt) {
        Some(LogMessage {
            timestamp,
            message,
            fields,
        })
    } else {
        None
    }
}

/// LogAggregator is responsible for processing raw JSON log messages, filtering them based on required fields
/// and a time window, batching them and then sending them over a channel.
pub struct LogAggregator {
    required_fields: Vec<String>,
    time_window: i64, // allowed time window in milliseconds
    batch_size: usize,
    max_delay: Duration,
    sender: Sender<Vec<LogMessage>>,
    buffer: Vec<LogMessage>,
    last_flush: Instant,
}

impl LogAggregator {
    /// Creates a new LogAggregator.
    /// required_fields: List of fields that must be present in a log message for it to be forwarded.
    /// time_window: Allowed deviation (in milliseconds) from the current time.
    /// batch_size: Number of log messages to hold before sending a batch.
    /// max_delay: Maximum delay (in milliseconds) before sending a batch regardless of its size.
    /// sender: Channel sender to forward the batch of log messages.
    pub fn new(
        required_fields: Vec<String>,
        time_window: i64,
        batch_size: usize,
        max_delay: u64,
        sender: Sender<Vec<LogMessage>>,
    ) -> Self {
        LogAggregator {
            required_fields,
            time_window,
            batch_size,
            max_delay: Duration::from_millis(max_delay),
            sender,
            buffer: Vec::new(),
            last_flush: Instant::now(),
        }
    }

    /// Processes a single raw JSON log message.
    /// If the message is valid, contains all required fields, and its timestamp is within the allowed time window,
    /// it is added to the batch buffer.  When the buffer reaches the batch size or the maximum delay has been exceeded,
    /// the batch is sent.
    pub fn process_message(&mut self, message: &str) {
        let current_time = current_time_millis();
        let parsed = parse_log_message(message);
        if let Some(log) = parsed {
            // Check if all required fields are present.
            let mut valid = true;
            for field in &self.required_fields {
                if !log.fields.contains_key(field) {
                    valid = false;
                    break;
                }
            }
            // Also check that timestamp is within the allowed window.
            if (log.timestamp < current_time - self.time_window)
                || (log.timestamp > current_time + self.time_window)
            {
                valid = false;
            }

            if valid {
                self.buffer.push(log);
            }
        } else {
            // Malformed JSON, log and discard.
            println!("Malformed log message: {}", message);
        }

        // Check for batch conditions.
        if self.buffer.len() >= self.batch_size
            || self.last_flush.elapsed() >= self.max_delay
        {
            self.flush();
        }
    }

    /// Flushes the current batch of log messages, sending them over the channel.
    pub fn flush(&mut self) {
        if !self.buffer.is_empty() {
            let batch = std::mem::take(&mut self.buffer);
            // If sending fails, we just drop the batch.
            let _ = self.sender.send(batch);
        }
        self.last_flush = Instant::now();
    }
}

/// LogAnalyzer receives log messages, stores them and provides query capabilities.
pub struct LogAnalyzer {
    storage: Vec<LogMessage>,
}

impl LogAnalyzer {
    /// Creates a new LogAnalyzer.
    pub fn new() -> Self {
        LogAnalyzer {
            storage: Vec::new(),
        }
    }

    /// Ingests a batch of log messages.
    pub fn ingest(&mut self, messages: Vec<LogMessage>) {
        self.storage.extend(messages);
    }

    /// Counts the number of log messages that have the given field equal to the given value within a time range (inclusive).
    pub fn count(&self, field: &str, value: &str, start_time: i64, end_time: i64) -> usize {
        self.storage.iter().filter(|log| {
            log.timestamp >= start_time &&
            log.timestamp <= end_time &&
            log.fields.get(field).map_or(false, |v| v == value)
        }).count()
    }
}

/// Returns the current time in milliseconds since the Unix epoch.
pub fn current_time_millis() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_millis() as i64
}