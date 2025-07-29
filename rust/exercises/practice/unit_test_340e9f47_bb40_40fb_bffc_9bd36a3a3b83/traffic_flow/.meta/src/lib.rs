use std::collections::HashMap;

#[derive(Clone, Debug)]
pub struct RoadSegment {
    pub id: u32,
    pub source: u32,
    pub destination: u32,
    pub capacity: u32,
    pub arrival_rate: u32,
}

#[derive(Clone, Debug)]
pub struct Intersection {
    pub id: u32,
    pub routing_probabilities: HashMap<u32, f32>,
}

#[derive(Clone, Debug)]
pub struct RoadNetwork {
    pub intersections: Vec<Intersection>,
    pub road_segments: Vec<RoadSegment>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Phase {
    pub green_road_segments: Vec<u32>,
}

#[derive(Clone, Debug)]
pub struct SimulationResult {
    pub average_waiting_time: f64,
    pub phases: HashMap<u32, Vec<Phase>>,
}

/// Struct representing a vehicle waiting in a queue.
/// Stores the arrival time and the number of vehicles that arrived at that time.
#[derive(Clone, Debug)]
struct VehicleBatch {
    arrival_time: u32,
    count: u32,
}

/// Simulate the traffic flow over the given road network for a specified time.
/// This simulation uses a discrete time approach.
/// For each time step:
///   1. Vehicles arrive on each road segment based on arrival_rate and are added to the waiting queue at the destination intersection.
///   2. For each intersection, determine the currently active phase based on the configured phases, phase_duration and switching_time.
///   3. If the current phase is active (i.e. within the green duration), process vehicles from the corresponding waiting queue up to the capacity of that road segment.
///   4. Every `reopt_interval` time steps, re-optimize the phases for each intersection based on the current waiting queue lengths (in descending order).
/// The waiting time for each vehicle is computed as (current_time - arrival_time) when it is processed.
/// At the end of the simulation, the average waiting time is computed and the final phase configuration is returned.
pub fn simulate(
    network: &RoadNetwork,
    simulation_time: u32,
    reopt_interval: u32,
    phase_duration: u32,
    switching_time: u32,
) -> SimulationResult {
    // Map intersection id to its phase configuration.
    let mut intersection_phases: HashMap<u32, Vec<Phase>> = HashMap::new();
    // Initialize phases for each intersection.
    for intersection in &network.intersections {
        let mut incoming: Vec<u32> = network
            .road_segments
            .iter()
            .filter(|rs| rs.destination == intersection.id)
            .map(|rs| rs.id)
            .collect();
        incoming.sort(); // sort by road segment id
        let phases: Vec<Phase> = incoming
            .into_iter()
            .map(|road_id| Phase {
                green_road_segments: vec![road_id],
            })
            .collect();
        intersection_phases.insert(intersection.id, phases);
    }

    // For each intersection and for each incoming road segment, maintain a vector queue of VehicleBatch.
    let mut waiting_queues: HashMap<u32, HashMap<u32, Vec<VehicleBatch>>> = HashMap::new();
    for intersection in &network.intersections {
        let mut queue: HashMap<u32, Vec<VehicleBatch>> = HashMap::new();
        for rs in network.road_segments.iter().filter(|r| r.destination == intersection.id) {
            queue.insert(rs.id, Vec::new());
        }
        waiting_queues.insert(intersection.id, queue);
    }

    let mut total_wait_time: u64 = 0;
    let mut processed_count: u64 = 0;

    // Simulation loop, each iteration is one time step.
    for current_time in 0..simulation_time {
        // Step 1: Vehicles arrive on each road segment.
        for road in &network.road_segments {
            if road.arrival_rate > 0 {
                // Add arrivals to the waiting queue at the road's destination intersection.
                if let Some(intersection_queue) = waiting_queues.get_mut(&road.destination) {
                    let entry = intersection_queue.entry(road.id).or_insert(Vec::new());
                    entry.push(VehicleBatch {
                        arrival_time: current_time,
                        count: road.arrival_rate,
                    });
                }
            }
        }

        // Step 2: Process each intersection.
        for intersection in &network.intersections {
            if let Some(phases) = intersection_phases.get(&intersection.id) {
                if phases.len() == 0 {
                    continue;
                }
                let cycle_time = phase_duration + switching_time;
                let cycle_length = phases.len() as u32 * cycle_time;
                let local_time = current_time % cycle_length;
                let phase_index = (local_time / cycle_time) as usize;
                let sub_phase_time = local_time % cycle_time;
                // Only process if within green time (not switching time)
                if sub_phase_time < phase_duration {
                    let active_phase = &phases[phase_index];
                    // Process each road segment that is green in this phase.
                    for &road_id in &active_phase.green_road_segments {
                        // Find road segment capacity.
                        let capacity = network
                            .road_segments
                            .iter()
                            .find(|rs| rs.id == road_id)
                            .map(|rs| rs.capacity)
                            .unwrap_or(0);
                        if capacity == 0 {
                            continue;
                        }
                        let mut remaining_capacity = capacity;
                        if let Some(intersection_queue) = waiting_queues.get_mut(&intersection.id) {
                            if let Some(queue) = intersection_queue.get_mut(&road_id) {
                                // Process the queue in FIFO order.
                                while remaining_capacity > 0 && !queue.is_empty() {
                                    let mut batch = queue.first_mut().unwrap();
                                    if batch.count <= remaining_capacity {
                                        let processed = batch.count;
                                        total_wait_time += (current_time - batch.arrival_time) as u64 * processed as u64;
                                        processed_count += processed as u64;
                                        remaining_capacity -= batch.count;
                                        // Remove the batch.
                                        queue.remove(0);
                                    } else {
                                        total_wait_time += (current_time - batch.arrival_time) as u64 * remaining_capacity as u64;
                                        processed_count += remaining_capacity as u64;
                                        batch.count -= remaining_capacity;
                                        remaining_capacity = 0;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Step 3: Every reopt_interval, re-optimize the phases.
        if (current_time + 1) % reopt_interval == 0 {
            for intersection in &network.intersections {
                if let Some(intersection_queue) = waiting_queues.get(&intersection.id) {
                    // Build a vector of (road_id, waiting_count)
                    let mut road_waits: Vec<(u32, u32)> = Vec::new();
                    for (&road_id, queue) in intersection_queue.iter() {
                        let total: u32 = queue.iter().map(|batch| batch.count).sum();
                        road_waits.push((road_id, total));
                    }
                    // Sort descending by waiting count, then by road_id.
                    road_waits.sort_by(|a, b| {
                        if b.1 == a.1 {
                            a.0.cmp(&b.0)
                        } else {
                            b.1.cmp(&a.1)
                        }
                    });
                    let new_phases: Vec<Phase> = road_waits
                        .into_iter()
                        .map(|(road_id, _)| Phase {
                            green_road_segments: vec![road_id],
                        })
                        .collect();
                    intersection_phases.insert(intersection.id, new_phases);
                }
            }
        }
    }

    let average_waiting_time = if processed_count > 0 {
        total_wait_time as f64 / processed_count as f64
    } else {
        0.0
    };

    SimulationResult {
        average_waiting_time,
        phases: intersection_phases,
    }
}