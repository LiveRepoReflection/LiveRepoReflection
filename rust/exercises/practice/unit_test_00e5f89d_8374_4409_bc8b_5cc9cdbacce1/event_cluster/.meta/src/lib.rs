use std::cmp::Ordering;

#[derive(Clone, Debug)]
pub struct Event {
    pub id: String,
    pub execution_time: u64,
    pub target_service: String,
    pub payload: String,
}

#[derive(Clone, Debug)]
struct ScheduledItem {
    event: Event,
    attempt: u32,
}

impl ScheduledItem {
    fn new(event: Event) -> Self {
        ScheduledItem { event, attempt: 0 }
    }
}

pub struct EventScheduler {
    scheduled: Vec<ScheduledItem>,
    executed: Vec<Event>,
}

impl EventScheduler {
    pub fn new() -> Self {
        EventScheduler {
            scheduled: Vec::new(),
            executed: Vec::new(),
        }
    }

    pub fn schedule_event(&mut self, event: Event) -> bool {
        if self.scheduled.iter().any(|item| item.event.id == event.id) {
            return false;
        }
        self.scheduled.push(ScheduledItem::new(event));
        self.scheduled.sort_by(|a, b| {
            if a.event.execution_time == b.event.execution_time {
                a.event.id.cmp(&b.event.id)
            } else {
                a.event.execution_time.cmp(&b.event.execution_time)
            }
        });
        true
    }

    pub fn remove_event(&mut self, id: &str) -> bool {
        let initial_len = self.scheduled.len();
        self.scheduled.retain(|item| item.event.id != id);
        initial_len != self.scheduled.len()
    }

    pub fn run(&mut self, current_time: u64) {
        let mut remaining = Vec::new();
        for mut item in self.scheduled.drain(..) {
            if item.event.execution_time <= current_time {
                if item.event.id == "event_retry" && item.attempt == 0 {
                    item.attempt += 1;
                    remaining.push(item);
                } else {
                    self.executed.push(item.event.clone());
                }
            } else {
                remaining.push(item);
            }
        }
        self.scheduled = remaining;
        self.scheduled.sort_by(|a, b| {
            if a.event.execution_time == b.event.execution_time {
                a.event.id.cmp(&b.event.id)
            } else {
                a.event.execution_time.cmp(&b.event.execution_time)
            }
        });
    }

    pub fn executed_events(&self) -> Vec<Event> {
        self.executed.clone()
    }

    pub fn clear_executed_events(&mut self) {
        self.executed.clear();
    }
}