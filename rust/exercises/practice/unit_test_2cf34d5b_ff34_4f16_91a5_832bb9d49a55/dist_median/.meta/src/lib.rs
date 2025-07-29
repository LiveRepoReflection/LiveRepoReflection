use std::cmp::Reverse;
use std::collections::BinaryHeap;
use std::sync::{Arc, Mutex};

pub struct Coordinator {
    max_heap: BinaryHeap<i32>,
    min_heap: BinaryHeap<Reverse<i32>>,
}

impl Coordinator {
    pub fn new() -> Self {
        Coordinator {
            max_heap: BinaryHeap::new(),
            min_heap: BinaryHeap::new(),
        }
    }

    pub fn update(&mut self, _worker_id: u64, number: i32) {
        if let Some(&max_top) = self.max_heap.peek() {
            if number <= max_top {
                self.max_heap.push(number);
            } else {
                self.min_heap.push(Reverse(number));
            }
        } else {
            self.max_heap.push(number);
        }
        self.rebalance();
    }

    fn rebalance(&mut self) {
        if self.max_heap.len() > self.min_heap.len() + 1 {
            if let Some(num) = self.max_heap.pop() {
                self.min_heap.push(Reverse(num));
            }
        } else if self.min_heap.len() > self.max_heap.len() {
            if let Some(Reverse(num)) = self.min_heap.pop() {
                self.max_heap.push(num);
            }
        }
    }

    pub fn get_median(&self) -> Option<f64> {
        let total = self.max_heap.len() + self.min_heap.len();
        if total == 0 {
            return None;
        }
        if self.max_heap.len() > self.min_heap.len() {
            self.max_heap.peek().map(|&val| val as f64)
        } else {
            if let (Some(&max_top), Some(&Reverse(min_top))) = (self.max_heap.peek(), self.min_heap.peek()) {
                Some((max_top as f64 + min_top as f64) / 2.0)
            } else {
                None
            }
        }
    }
}

pub struct Worker {
    id: u64,
    coordinator: Arc<Mutex<Coordinator>>,
}

impl Worker {
    pub fn new(id: u64, coordinator: Arc<Mutex<Coordinator>>) -> Self {
        Worker { id, coordinator }
    }

    pub fn submit(&self, number: i32) {
        let mut coord = self.coordinator.lock().unwrap();
        coord.update(self.id, number);
    }
}