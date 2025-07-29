use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

pub type IntersectionId = u32;
pub type Timestamp = u64;
pub type CongestionLevel = u8;

pub const MAX_SPEED: f64 = 30.0;

#[derive(Clone, Copy, Debug)]
pub struct RoadSegment {
    pub from: IntersectionId,
    pub to: IntersectionId,
    pub length: f64,
    pub congestion: CongestionLevel,
}

pub trait CityGraph {
    fn get_outgoing_edges(&self, intersection_id: IntersectionId) -> &[RoadSegment];
}

#[derive(Debug, PartialEq)]
pub struct Route {
    pub path: Vec<IntersectionId>,
    pub total_travel_time: f64,
    pub total_cost: f64,
}

struct State {
    cost: f64,
    position: IntersectionId,
}

impl Eq for State {}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost && self.position == other.position
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // Notice that BinaryHeap is a max-heap, so we invert the comparison.
        other.cost.partial_cmp(&self.cost).unwrap_or(Ordering::Equal)
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Calculates the travel time for a given road segment.
/// If congestion is 100%, returns None as the edge is impassable.
fn travel_time(segment: &RoadSegment) -> Option<f64> {
    if segment.congestion >= 100 {
        return None;
    }
    let speed_factor = 1.0 - (segment.congestion as f64) / 100.0;
    let effective_speed = MAX_SPEED * speed_factor;
    if effective_speed <= 0.0 {
        None
    } else {
        Some(segment.length / effective_speed)
    }
}

/// Finds the optimal route in the city graph from start_intersection to end_intersection.
/// The cost function is total_travel_time + lateness_penalty_weight * max(0, arrival_time - request_deadline)
/// where arrival_time = current_time + total_travel_time.
///
/// This function employs Dijkstra's algorithm to find the route with minimal total travel time.
pub fn find_optimal_route(
    graph: &dyn CityGraph,
    start_intersection: IntersectionId,
    end_intersection: IntersectionId,
    request_deadline: Timestamp,
    current_time: Timestamp,
    lateness_penalty_weight: f64,
) -> Option<Route> {
    // Special case: if start and end are the same.
    if start_intersection == end_intersection {
        return Some(Route {
            path: vec![start_intersection],
            total_travel_time: 0.0,
            total_cost: 0.0,
        });
    }

    // Maps each IntersectionId to (current best travel time, previous intersection).
    let mut distances: HashMap<IntersectionId, f64> = HashMap::new();
    let mut previous: HashMap<IntersectionId, IntersectionId> = HashMap::new();

    let mut heap = BinaryHeap::new();

    distances.insert(start_intersection, 0.0);
    heap.push(State {
        cost: 0.0,
        position: start_intersection,
    });

    while let Some(State { cost, position }) = heap.pop() {
        if position == end_intersection {
            // Found the destination; break early.
            break;
        }
        if cost > *distances.get(&position).unwrap_or(&f64::INFINITY) {
            continue;
        }
        let edges = graph.get_outgoing_edges(position);
        for segment in edges {
            if let Some(segment_time) = travel_time(segment) {
                let next = segment.to;
                let next_cost = cost + segment_time;
                if next_cost < *distances.get(&next).unwrap_or(&f64::INFINITY) {
                    distances.insert(next, next_cost);
                    previous.insert(next, position);
                    heap.push(State {
                        cost: next_cost,
                        position: next,
                    });
                }
            }
        }
    }

    // If destination was not reached
    let &best_travel_time = distances.get(&end_intersection)?;
    // Reconstruct path
    let mut path = Vec::new();
    let mut current = end_intersection;
    path.push(current);
    while let Some(&prev) = previous.get(&current) {
        current = prev;
        path.push(current);
    }
    path.reverse();

    let arrival_time = current_time as f64 + best_travel_time;
    let deadline_f64 = request_deadline as f64;
    let lateness = if arrival_time > deadline_f64 {
        arrival_time - deadline_f64
    } else {
        0.0
    };
    let total_cost = best_travel_time + lateness_penalty_weight * lateness;

    Some(Route {
        path,
        total_travel_time: best_travel_time,
        total_cost,
    })
}