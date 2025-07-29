use std::collections::{BinaryHeap, HashMap};

#[derive(Debug, PartialEq, Eq)]
struct State {
    planet: u32,
    arrival_time: u64,
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        other.arrival_time.partial_cmp(&self.arrival_time)
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        other.arrival_time.cmp(&self.arrival_time)
    }
}

pub fn min_intergalactic_travel_time(
    num_planets: u32,
    wormholes: Vec<(u32, u32, u32, Vec<(u64, u64)>)>,
    start_planet: u32,
    destination_planet: u32,
    departure_time: u64,
) -> Option<u64> {
    if start_planet == destination_planet {
        return Some(departure_time);
    }

    let mut graph: HashMap<u32, Vec<(u32, u32, Vec<(u64, u64)>)>> = HashMap::new();
    for (a, b, time, schedule) in wormholes {
        graph.entry(a).or_default().push((b, time, schedule.clone()));
        graph.entry(b).or_default().push((a, time, schedule));
    }

    let mut distances: HashMap<u32, u64> = HashMap::new();
    let mut heap = BinaryHeap::new();

    distances.insert(start_planet, departure_time);
    heap.push(State {
        planet: start_planet,
        arrival_time: departure_time,
    });

    while let Some(State { planet, arrival_time }) = heap.pop() {
        if planet == destination_planet {
            return Some(arrival_time);
        }

        if arrival_time > *distances.get(&planet).unwrap_or(&u64::MAX) {
            continue;
        }

        if let Some(connections) = graph.get(&planet) {
            for (neighbor, travel_time, schedule) in connections {
                let earliest_departure = arrival_time;
                let mut best_window = None;

                for &(start, end) in schedule {
                    if end < earliest_departure {
                        continue;
                    }

                    let departure = start.max(earliest_departure);
                    if departure + *travel_time as u64 > end {
                        continue;
                    }

                    let arrival = departure + *travel_time as u64;
                    if best_window.map_or(true, |(_, best_arrival)| arrival < best_arrival) {
                        best_window = Some((departure, arrival));
                    }
                }

                if let Some((_, new_arrival)) = best_window {
                    if new_arrival < *distances.get(neighbor).unwrap_or(&u64::MAX) {
                        distances.insert(*neighbor, new_arrival);
                        heap.push(State {
                            planet: *neighbor,
                            arrival_time: new_arrival,
                        });
                    }
                }
            }
        }
    }

    None
}