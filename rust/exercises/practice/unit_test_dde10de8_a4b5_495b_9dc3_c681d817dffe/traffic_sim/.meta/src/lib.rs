use std::collections::HashMap;
use std::f64;

pub type VehicleId = u32;

#[derive(Debug, Clone)]
pub struct Vehicle {
    pub id: VehicleId,
    pub route: Vec<u32>,
    pub max_speed: f64,
    pub entry_time: f64,
}

#[derive(Debug, Clone)]
pub struct Road {
    pub to: u32,
    pub capacity: usize,
    pub speed_limit: f64,
    pub length: f64,
}

#[derive(Debug, Clone)]
pub struct CityGraph {
    pub adjacency: HashMap<u32, Vec<Road>>,
}

impl CityGraph {
    pub fn new() -> Self {
        CityGraph {
            adjacency: HashMap::new(),
        }
    }

    pub fn add_road(&mut self, from: u32, to: u32, capacity: usize, speed_limit: f64, length: f64) {
        let road = Road {
            to,
            capacity,
            speed_limit,
            length,
        };
        self.adjacency.entry(from).or_insert_with(Vec::new).push(road);
        // Ensure destination node exists in the graph.
        self.adjacency.entry(to).or_insert_with(Vec::new);
    }

    pub fn get_road(&self, from: u32, to: u32) -> Option<&Road> {
        if let Some(roads) = self.adjacency.get(&from) {
            for road in roads {
                if road.to == to {
                    return Some(road);
                }
            }
        }
        None
    }
}

enum State {
    Waiting,
    InTransit { from: u32, to: u32, remaining: f64 },
}

struct SimVehicle {
    vehicle: Vehicle,
    current_index: usize, // index in route vector; current intersection is at route[current_index]
    state: State,
}

pub fn simulate(
    city_graph: &CityGraph,
    vehicles: Vec<Vehicle>,
    max_steps: u32,
) -> HashMap<VehicleId, f64> {
    let mut results: HashMap<VehicleId, f64> = HashMap::new();

    // Occupancy for roads: key = (from, to), value = number of vehicles currently on the road.
    let mut occupancy: HashMap<(u32, u32), usize> = HashMap::new();

    // Vehicles that have not yet entered the simulation.
    let mut pending: Vec<Vehicle> = vehicles;
    pending.sort_by(|a, b| a.entry_time.partial_cmp(&b.entry_time).unwrap());

    // Active vehicles in simulation.
    let mut active: Vec<SimVehicle> = Vec::new();

    let mut current_time: f64 = 0.0;
    for step in 0..=max_steps {
        current_time = step as f64;

        // Add pending vehicles whose entry_time is <= current_time.
        while !pending.is_empty() && pending[0].entry_time <= current_time {
            let vehicle = pending.remove(0);
            if vehicle.route.is_empty() {
                // Invalid route.
                results.insert(vehicle.id, f64::INFINITY);
                continue;
            }
            let sim_vehicle = SimVehicle {
                vehicle,
                current_index: 0,
                state: State::Waiting,
            };
            active.push(sim_vehicle);
        }

        // Update vehicles that are in transit.
        let mut finished_indices: Vec<usize> = Vec::new();
        for (i, sim_vehicle) in active.iter_mut().enumerate() {
            if let State::InTransit { ref mut remaining, .. } = sim_vehicle.state {
                *remaining -= 1.0;
                if *remaining <= 0.0 {
                    finished_indices.push(i);
                }
            }
        }

        // Process vehicles that finished transit.
        finished_indices.sort_by(|a, b| b.cmp(a));
        for i in finished_indices {
            let (from, to) = match active[i].state {
                State::InTransit { from, to, .. } => (from, to),
                _ => (0, 0),
            };
            // Free the road occupancy.
            let occ = occupancy.entry((from, to)).or_insert(1);
            if *occ > 0 {
                *occ -= 1;
            }
            // Advance vehicle position.
            active[i].current_index += 1;
            if active[i].current_index >= active[i].vehicle.route.len() {
                results.insert(active[i].vehicle.id, current_time);
            } else {
                active[i].state = State::Waiting;
            }
        }

        // Process vehicles that are waiting at an intersection.
        for sim_vehicle in active.iter_mut() {
            if sim_vehicle.current_index >= sim_vehicle.vehicle.route.len() {
                continue;
            }
            if let State::Waiting = sim_vehicle.state {
                // Check if vehicle is at its destination.
                if sim_vehicle.current_index == sim_vehicle.vehicle.route.len() - 1 {
                    results.insert(sim_vehicle.vehicle.id, current_time);
                    continue;
                }
                let from = sim_vehicle.vehicle.route[sim_vehicle.current_index];
                let to = sim_vehicle.vehicle.route[sim_vehicle.current_index + 1];
                // Validate the road exists.
                let road_option = city_graph.get_road(from, to);
                if road_option.is_none() {
                    results.insert(sim_vehicle.vehicle.id, f64::INFINITY);
                    sim_vehicle.current_index = sim_vehicle.vehicle.route.len();
                    continue;
                }
                let road = road_option.unwrap();
                let current_occ = occupancy.get(&(from, to)).cloned().unwrap_or(0);
                if current_occ < road.capacity {
                    // The vehicle can enter the road.
                    let effective_speed = if sim_vehicle.vehicle.max_speed < road.speed_limit {
                        sim_vehicle.vehicle.max_speed
                    } else {
                        road.speed_limit
                    };
                    let travel_time = road.length / effective_speed;
                    occupancy.insert((from, to), current_occ + 1);
                    sim_vehicle.state = State::InTransit {
                        from,
                        to,
                        remaining: travel_time,
                    };
                }
            }
        }

        // Remove vehicles that have finished their routes.
        active.retain(|sv| sv.current_index < sv.vehicle.route.len() && !results.contains_key(&sv.vehicle.id));
        if pending.is_empty() && active.is_empty() {
            break;
        }
    }

    // Vehicles still in simulation did not finish within max_steps.
    for sim_vehicle in active.into_iter() {
        results.insert(sim_vehicle.vehicle.id, f64::INFINITY);
    }
    for vehicle in pending.into_iter() {
        results.insert(vehicle.id, f64::INFINITY);
    }

    results
}