use std::collections::{HashMap, BinaryHeap};
use std::cmp::Reverse;

pub enum Update {
    Add { source: i32, destination: i32, weight: i32 },
    Remove { source: i32, destination: i32 },
    Update { source: i32, destination: i32, weight: i32 },
}

pub struct Graph {
    sources: Vec<i32>,
    edges: HashMap<i32, Vec<(i32, i32)>>, // source -> list of (destination, weight)
}

impl Graph {
    pub fn new(initial_edges: Vec<(i32, i32, i32)>, source_cities: Vec<i32>) -> Self {
        let mut edges: HashMap<i32, Vec<(i32, i32)>> = HashMap::new();
        for (s, d, w) in initial_edges.into_iter() {
            edges.entry(s).or_insert_with(Vec::new).push((d, w));
        }
        Graph {
            sources: source_cities,
            edges,
        }
    }

    pub fn update(&mut self, update: Update) {
        match update {
            Update::Add { source, destination, weight } => {
                let entry = self.edges.entry(source).or_insert_with(Vec::new);
                if !entry.iter().any(|&(d, _)| d == destination) {
                    entry.push((destination, weight));
                }
            }
            Update::Remove { source, destination } => {
                if let Some(neighbors) = self.edges.get_mut(&source) {
                    neighbors.retain(|&(d, _)| d != destination);
                }
            }
            Update::Update { source, destination, weight } => {
                if let Some(neighbors) = self.edges.get_mut(&source) {
                    for edge in neighbors.iter_mut() {
                        if edge.0 == destination {
                            edge.1 = weight;
                            break;
                        }
                    }
                }
            }
        }
    }

    pub fn query(&self, target: i32) -> i32 {
        let mut dist: HashMap<i32, i32> = HashMap::new();
        let mut heap = BinaryHeap::new();

        for &src in &self.sources {
            dist.insert(src, 0);
            heap.push((Reverse(0), src));
        }

        while let Some((Reverse(d), u)) = heap.pop() {
            if u == target {
                return d;
            }
            if let Some(neighbors) = self.edges.get(&u) {
                for &(v, w) in neighbors.iter() {
                    let nd = d + w;
                    if nd < *dist.get(&v).unwrap_or(&i32::MAX) {
                        dist.insert(v, nd);
                        heap.push((Reverse(nd), v));
                    }
                }
            }
        }
        -1
    }
}