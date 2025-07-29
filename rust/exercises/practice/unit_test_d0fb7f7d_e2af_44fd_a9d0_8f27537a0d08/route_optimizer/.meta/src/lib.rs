use std::collections::{BinaryHeap, HashMap};
use std::cmp::Reverse;

pub fn find_min_travel_time(
    start_node: usize,
    end_node: usize,
    departure_time: u64,
    graph: &Vec<Vec<(usize, u64, f64)>>,
    congestion_updates: &Vec<(usize, usize, u64, f64)>,
    restricted_access: &Vec<(usize, Vec<(u64, u64)>)>,
) -> Option<u64> {
    let n = graph.len();

    // Build congestion update mapping: key: (u, v) -> sorted Vec of update timestamps.
    let mut update_map: HashMap<(usize, usize), Vec<u64>> = HashMap::new();
    for &(u, v, timestamp, _new_factor) in congestion_updates.iter() {
        update_map.entry((u, v)).or_insert_with(Vec::new).push(timestamp);
    }
    for (_key, timestamps) in update_map.iter_mut() {
        timestamps.sort();
    }

    // Build restricted access mapping: for each node, get sorted intervals.
    let mut restrictions: Vec<Vec<(u64, u64)>> = vec![Vec::new(); n];
    for &(node, ref intervals) in restricted_access.iter() {
        let mut ints = intervals.clone();
        ints.sort_by_key(|x| x.0);
        restrictions[node] = ints;
    }

    // Dijkstra with time as weight.
    let mut dist: Vec<u64> = vec![u64::MAX; n];
    dist[start_node] = departure_time;
    let mut heap = BinaryHeap::new();
    heap.push(Reverse((departure_time, start_node)));

    while let Some(Reverse((time, u))) = heap.pop() {
        if u == end_node {
            return Some(time);
        }
        if time > dist[u] {
            continue;
        }
        // For each neighbor v from u.
        for &(v, base_time, _init_factor) in &graph[u] {
            let mut effective_travel = base_time;
            // Check congestion updates for edge (u, v).
            if let Some(updates) = update_map.get(&(u, v)) {
                // Find the earliest update timestamp that is >= departure time and <= departure time + base_time.
                // We only consider updates that occur after we start traversing the edge.
                let t_start = time;
                // Binary search for first update >= t_start.
                if let Ok(idx) = updates.binary_search(&t_start) {
                    // Found an update exactly at departure time.
                    let candidate = updates[idx];
                    if candidate <= t_start + base_time {
                        effective_travel = base_time + (candidate - t_start);
                    }
                } else if let Err(idx) = updates.binary_search(&t_start) {
                    if idx < updates.len() {
                        let candidate = updates[idx];
                        if candidate <= t_start + base_time {
                            effective_travel = base_time + (candidate - t_start);
                        }
                    }
                }
            }
            let mut arrival = time.saturating_add(effective_travel);
            // Adjust arrival if destination node v has restricted access.
            if !restrictions[v].is_empty() {
                for &(start_r, end_r) in restrictions[v].iter() {
                    // If arrival time falls in the restricted interval [start_r, end_r),
                    // then wait until end_r.
                    if arrival >= start_r && arrival < end_r {
                        arrival = end_r;
                    }
                    // Since intervals are sorted and non-overlapping,
                    // if arrival is before current interval, no need to check further.
                    if arrival < start_r {
                        break;
                    }
                }
            }
            if arrival < dist[v] {
                dist[v] = arrival;
                heap.push(Reverse((arrival, v)));
            }
        }
    }
    None
}