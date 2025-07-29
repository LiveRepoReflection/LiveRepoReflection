use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;

#[derive(Debug)]
pub struct Graph {
    pub nodes: Vec<i32>,
    pub edges: Vec<(i32, i32, f64)>, // (from, to, flight_time)
    pub charging_stations: Vec<i32>,
}

#[derive(Debug)]
pub struct Drone {
    pub id: i32,
    pub start: i32,
    pub battery_capacity: f64,
    pub t_max: f64,
}

#[derive(Debug)]
pub struct DeliveryRequest {
    pub id: i32,
    pub origin: i32,
    pub destination: i32,
    pub deadline: f64,
}

#[derive(Debug)]
pub struct DronePlan {
    pub drone_id: i32,
    pub route: Vec<i32>,
    pub total_delivery_time: f64,
}

#[derive(Debug)]
pub struct Plan {
    pub drones_plans: Vec<DronePlan>,
}

#[derive(Debug)]
pub enum PlanningError {
    UnreachableDelivery(i32), // delivery request id that cannot be reached
    NotEnoughDrones,
}

#[derive(Clone)]
struct State {
    cost: f64,
    node: i32,
    battery: f64,
    path: Vec<i32>,
}

impl Eq for State {}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse ordering because BinaryHeap is a max-heap.
        other.cost.partial_cmp(&self.cost).unwrap_or(Ordering::Equal)
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// Get neighbors for a given node.
fn neighbors(graph: &Graph, node: i32) -> Vec<(i32, f64)> {
    let mut result = Vec::new();
    for &(from, to, time) in &graph.edges {
        if from == node {
            result.push((to, time));
        }
    }
    result
}

// Dijkstra algorithm adapted to include battery constraints and charging stops.
fn dijkstra_with_charge(graph: &Graph, start: i32, target: i32, capacity: f64, t_charge: f64) -> Option<(Vec<i32>, f64)> {
    let mut heap = BinaryHeap::new();
    let init_state = State {
        cost: 0.0,
        node: start,
        battery: capacity,
        path: vec![start],
    };
    heap.push(init_state);
    // Use a visited map with discretized battery level to track the best cost for each state.
    let mut best: HashMap<(i32, i32), f64> = HashMap::new();

    while let Some(state) = heap.pop() {
        if state.node == target {
            return Some((state.path, state.cost));
        }
        // Discretize battery amount to avoid floating point precision issues.
        let battery_key = (state.node, (state.battery * 1000.0) as i32);
        if let Some(&prev_cost) = best.get(&battery_key) {
            if state.cost >= prev_cost {
                continue;
            }
        }
        best.insert(battery_key, state.cost);

        // If the current node is a charging station and battery is not full, consider recharging.
        if graph.charging_stations.contains(&state.node) && (state.battery - capacity).abs() > 1e-6 {
            let new_state = State {
                cost: state.cost + t_charge,
                node: state.node,
                battery: capacity,
                path: state.path.clone(),
            };
            heap.push(new_state);
        }

        // Explore neighbors.
        for (next, w) in neighbors(graph, state.node) {
            if state.battery + 1e-6 >= w {
                let mut new_path = state.path.clone();
                new_path.push(next);
                let new_state = State {
                    cost: state.cost + w,
                    node: next,
                    battery: state.battery - w,
                    path: new_path,
                };
                heap.push(new_state);
            }
        }
    }
    None
}

// Helper to combine two paths without duplicating the junction node.
fn combine_paths(path1: Vec<i32>, path2: Vec<i32>) -> Vec<i32> {
    if path1.is_empty() {
        return path2;
    }
    let mut combined = path1;
    if !path2.is_empty() {
        let mut iter = path2.into_iter();
        let first = iter.next().unwrap();
        if *combined.last().unwrap() != first {
            combined.push(first);
        }
        for node in iter {
            combined.push(node);
        }
    }
    combined
}

// plan_routes assigns each delivery to a drone (each drone performs a single delivery).
// The planned route is a combination of three legs:
// 1. From the drone's starting warehouse to the delivery origin.
// 2. From the delivery origin to the delivery destination.
// 3. From the delivery destination back to the drone's starting warehouse.
// Each leg is planned using Dijkstra with battery constraints and optional charging stops.
pub fn plan_routes(
    graph: &Graph,
    drones: &[Drone],
    deliveries: &[DeliveryRequest],
    t_charge: f64,
) -> Result<Plan, PlanningError> {
    let mut drone_plans: Vec<DronePlan> = Vec::new();
    let mut used_drones = vec![false; drones.len()];
    let mut used_deliveries = vec![false; deliveries.len()];

    // Attempt to assign each delivery to a drone.
    for (di, delivery) in deliveries.iter().enumerate() {
        let mut assigned = false;
        for (i, drone) in drones.iter().enumerate() {
            if used_drones[i] {
                continue;
            }
            // Leg 1: Drone warehouse to delivery origin.
            let (path1, cost1) = if drone.start == delivery.origin {
                (vec![drone.start], 0.0)
            } else {
                match dijkstra_with_charge(graph, drone.start, delivery.origin, drone.battery_capacity, t_charge) {
                    Some(result) => result,
                    None => continue,
                }
            };

            // Leg 2: Delivery origin to delivery destination.
            let (path2, cost2) = if delivery.origin == delivery.destination {
                (vec![delivery.origin], 0.0)
            } else {
                match dijkstra_with_charge(graph, delivery.origin, delivery.destination, drone.battery_capacity, t_charge) {
                    Some(result) => result,
                    None => continue,
                }
            };

            // Leg 3: Delivery destination back to drone warehouse.
            let (path3, cost3) = if delivery.destination == drone.start {
                (vec![delivery.destination], 0.0)
            } else {
                match dijkstra_with_charge(graph, delivery.destination, drone.start, drone.battery_capacity, t_charge) {
                    Some(result) => result,
                    None => continue,
                }
            };

            // Check if delivery deadline can be met (for leg1 + leg2).
            if cost1 + cost2 > delivery.deadline + 1e-6 {
                continue;
            }
            let total_cost = cost1 + cost2 + cost3;
            if total_cost > drone.t_max + 1e-6 {
                continue;
            }

            // Combine paths for the complete route.
            let route12 = combine_paths(path1, path2);
            let full_route = combine_paths(route12, path3);
            drone_plans.push(DronePlan {
                drone_id: drone.id,
                route: full_route,
                total_delivery_time: total_cost,
            });
            used_drones[i] = true;
            used_deliveries[di] = true;
            assigned = true;
            break;
        }
        if !assigned {
            return Err(PlanningError::UnreachableDelivery(delivery.id));
        }
    }
    if drone_plans.len() < deliveries.len() {
        return Err(PlanningError::NotEnoughDrones);
    }
    Ok(Plan { drones_plans: drone_plans })
}