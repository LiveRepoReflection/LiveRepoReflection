use std::collections::HashMap;

#[derive(Clone, Debug)]
pub struct Event {
    pub event_type: String,
    pub attributes: HashMap<String, String>,
}

impl Event {
    pub fn new(event_type: &str, attributes: HashMap<String, String>) -> Self {
        Event {
            event_type: event_type.to_string(),
            attributes,
        }
    }
}

pub struct Processor {
    events: Vec<Event>,
    routing_rules: Vec<Box<dyn Fn(&Event) -> Option<String>>>,
    stateful_transformations: Vec<Box<dyn Fn(&mut HashMap<String, Vec<f64>>, &Event) -> Option<(String, f64)>>>,
}

impl Processor {
    pub fn new() -> Self {
        Processor {
            events: Vec::new(),
            routing_rules: Vec::new(),
            stateful_transformations: Vec::new(),
        }
    }

    pub fn ingest_event(&mut self, event: Event) {
        self.events.push(event);
    }

    pub fn add_routing_rule<F>(&mut self, rule: F)
    where
        F: Fn(&Event) -> Option<String> + 'static,
    {
        self.routing_rules.push(Box::new(rule));
    }

    pub fn process_events(&mut self) -> HashMap<String, Vec<Event>> {
        let mut routed: HashMap<String, Vec<Event>> = HashMap::new();
        // Drain all events and route them according to the first matching rule
        for event in self.events.drain(..) {
            let mut route = "default".to_string();
            for rule in self.routing_rules.iter() {
                if let Some(r) = rule(&event) {
                    route = r;
                    break;
                }
            }
            routed.entry(route).or_insert_with(Vec::new).push(event);
        }
        routed
    }

    pub fn enable_stateful_transformation<F>(&mut self, transformation: F)
    where
        F: Fn(&mut HashMap<String, Vec<f64>>, &Event) -> Option<(String, f64)> + 'static,
    {
        self.stateful_transformations.push(Box::new(transformation));
    }

    pub fn compute_stateful_transformation(&mut self) -> HashMap<String, f64> {
        let mut state: HashMap<String, Vec<f64>> = HashMap::new();
        let mut results: HashMap<String, f64> = HashMap::new();
        // Process each event in order and apply each stateful transformation
        for event in self.events.iter() {
            for transform in self.stateful_transformations.iter() {
                if let Some((key, value)) = transform(&mut state, event) {
                    results.insert(key, value);
                }
            }
        }
        // Clear events after processing transformations
        self.events.clear();
        results
    }

    pub fn simulate_failure_and_recover(&mut self) -> Vec<Event> {
        // Simulate node failure by cloning current events, then clearing them for recovery.
        let pending = self.events.clone();
        self.events.clear();
        pending
    }

    pub fn process_pending(&mut self, pending: Vec<Event>) -> HashMap<String, Vec<Event>> {
        let mut routed: HashMap<String, Vec<Event>> = HashMap::new();
        for event in pending {
            let mut route = "default".to_string();
            for rule in self.routing_rules.iter() {
                if let Some(r) = rule(&event) {
                    route = r;
                    break;
                }
            }
            routed.entry(route).or_insert_with(Vec::new).push(event);
        }
        routed
    }
}