use std::collections::BTreeMap;
use std::sync::{Arc, RwLock};

#[derive(Debug)]
pub struct DistributedMedianSystem {
    nodes: RwLock<BTreeMap<u64, NodeData>>,
    global_stats: RwLock<GlobalStats>,
}

#[derive(Debug)]
struct NodeData {
    count: usize,
    min: i64,
    max: i64,
}

#[derive(Debug, Default)]
struct GlobalStats {
    total_count: usize,
    less_than: BTreeMap<i64, usize>,
}

impl DistributedMedianSystem {
    pub fn new() -> Self {
        DistributedMedianSystem {
            nodes: RwLock::new(BTreeMap::new()),
            global_stats: RwLock::new(GlobalStats::default()),
        }
    }

    pub fn register_node(&self, node_id: u64) -> bool {
        let mut nodes = self.nodes.write().unwrap();
        if nodes.contains_key(&node_id) {
            return false;
        }
        nodes.insert(
            node_id,
            NodeData {
                count: 0,
                min: i64::MAX,
                max: i64::MIN,
            },
        );
        true
    }

    pub fn add_data(&self, node_id: u64, data: &[i64]) {
        if data.is_empty() {
            return;
        }

        let mut nodes = self.nodes.write().unwrap();
        let node_data = match nodes.get_mut(&node_id) {
            Some(data) => data,
            None => return,
        };

        let first = data[0];
        let last = data[data.len() - 1];
        node_data.count += data.len();
        node_data.min = node_data.min.min(first);
        node_data.max = node_data.max.max(last);

        let mut global_stats = self.global_stats.write().unwrap();
        global_stats.total_count += data.len();

        for &num in data {
            *global_stats.less_than.entry(num).or_insert(0) += 1;
        }
    }

    pub fn get_median(&self) -> Option<f64> {
        let global_stats = self.global_stats.read().unwrap();
        if global_stats.total_count == 0 {
            return None;
        }

        let mut sorted_counts: Vec<_> = global_stats.less_than.iter().collect();
        sorted_counts.sort_by_key(|(&num, _)| num);

        let mut cumulative = 0;
        let mut prev_num = None;
        let mut median_low = None;
        let mut median_high = None;

        let target_low = (global_stats.total_count - 1) / 2;
        let target_high = global_stats.total_count / 2;

        for (&num, &count) in &sorted_counts {
            cumulative += count;
            if median_low.is_none() && cumulative > target_low {
                median_low = Some(num);
            }
            if median_high.is_none() && cumulative > target_high {
                median_high = Some(num);
                break;
            }
            prev_num = Some(num);
        }

        match (median_low, median_high) {
            (Some(low), Some(high)) => {
                if global_stats.total_count % 2 == 0 {
                    Some((low as f64 + high as f64) / 2.0)
                } else {
                    Some(high as f64)
                }
            }
            (Some(low), None) => Some(low as f64),
            (None, Some(high)) => Some(high as f64),
            (None, None) => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_system() {
        let system = DistributedMedianSystem::new();
        assert_eq!(system.get_median(), None);
    }

    #[test]
    fn test_single_node_single_batch() {
        let system = DistributedMedianSystem::new();
        assert!(system.register_node(1));
        system.add_data(1, &[1, 2, 3]);
        assert_eq!(system.get_median(), Some(2.0));
    }

    #[test]
    fn test_multiple_nodes_multiple_batches() {
        let system = DistributedMedianSystem::new();
        assert!(system.register_node(1));
        assert!(system.register_node(2));
        system.add_data(1, &[1, 3, 5]);
        system.add_data(2, &[2, 4]);
        system.add_data(1, &[7, 9]);
        system.add_data(2, &[6, 8]);
        assert_eq!(system.get_median(), Some(5.0));
    }
}