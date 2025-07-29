use std::cmp::Ordering;
use std::sync::{Mutex, OnceLock};

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum EventType {
    Deposit,
    Withdrawal,
    TransferIn,
    TransferOut,
}

#[derive(Debug, PartialEq, Eq, Clone)]
pub struct Event {
    pub timestamp: u64,
    pub institution_id: String,
    pub account_id: String,
    pub event_type: EventType,
    pub amount: i64,
    pub transfer_id: Option<String>,
}

// Global event store with thread-safe access.
static EVENT_STORE: OnceLock<Mutex<Vec<Event>>> = OnceLock::new();

fn get_event_store() -> &'static Mutex<Vec<Event>> {
    EVENT_STORE.get_or_init(|| Mutex::new(Vec::new()))
}

/// Clears the event store. For testing purposes.
pub fn clear_store() {
    let mut store = get_event_store().lock().unwrap();
    store.clear();
}

/// Ingests a new event into the event store. Performs basic validation on the event.
pub fn ingest_event(event: Event) -> Result<(), String> {
    // Validate event integrity.
    match event.event_type {
        EventType::TransferIn | EventType::TransferOut => {
            if event.transfer_id.is_none() {
                return Err("Transfer events must have a transfer_id".to_string());
            }
        }
        EventType::Deposit | EventType::Withdrawal => {
            if event.transfer_id.is_some() {
                return Err("Non-transfer events should not have a transfer_id".to_string());
            }
        }
    }
    let mut store = get_event_store().lock().map_err(|e| e.to_string())?;
    store.push(event);
    Ok(())
}

/// Queries events from the event store based on optional filters and pagination parameters.
/// Returns events sorted by ascending timestamp.
pub fn query_events(
    institution: Option<&str>,
    account: Option<&str>,
    start_time: Option<u64>,
    end_time: Option<u64>,
    page: usize,
    page_size: usize,
) -> Result<Vec<Event>, String> {
    let store = get_event_store().lock().map_err(|e| e.to_string())?;
    let mut filtered: Vec<Event> = store
        .iter()
        .filter(|e| {
            if let Some(inst) = institution {
                if e.institution_id != inst {
                    return false;
                }
            }
            if let Some(acc) = account {
                if e.account_id != acc {
                    return false;
                }
            }
            if let Some(st) = start_time {
                if e.timestamp < st {
                    return false;
                }
            }
            if let Some(et) = end_time {
                if e.timestamp > et {
                    return false;
                }
            }
            true
        })
        .cloned()
        .collect();

    // Sort the filtered events by ascending timestamp.
    filtered.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));

    // Apply pagination.
    let start_index = page * page_size;
    if start_index >= filtered.len() {
        return Ok(vec![]);
    }
    let end_index = std::cmp::min(start_index + page_size, filtered.len());
    Ok(filtered[start_index..end_index].to_vec())
}