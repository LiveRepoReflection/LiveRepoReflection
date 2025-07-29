use std::collections::{BinaryHeap, HashMap};
use std::f64::consts::PI;

const EARTH_RADIUS_KM: f64 = 6371.0;
const CONGESTION_FACTOR: f64 = 10.0;

#[derive(Debug, Clone)]
struct Server {
    id: usize,
    lat: f64,
    lon: f64,
    congestion: u8,
}

#[derive(Debug, Clone)]
struct Edge {
    to: usize,
    latency: f64,
}

#[derive(Debug, PartialEq)]
struct NodeDistance {
    node: usize,
    distance: f64,
}

impl Eq for NodeDistance {}

impl PartialOrd for NodeDistance {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        other.distance.partial_cmp(&self.distance)
    }
}

impl Ord for NodeDistance {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.partial_cmp(other).unwrap()
    }
}

fn degrees_to_radians(degrees: f64) -> f64 {
    degrees * PI / 180.0
}

fn haversine_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    let lat1 = degrees_to_radians(lat1);
    let lon1 = degrees_to_radians(lon1);
    let lat2 = degrees_to_radians(lat2);
    let lon2 = degrees_to_radians(lon2);

    let dlat = lat2 - lat1;
    let dlon = lon2 - lon1;

    let a = (dlat / 2.0).sin().powi(2) + lat1.cos() * lat2.cos() * (dlon / 2.0).sin().powi(2);
    let c = 2.0 * a.sqrt().asin();

    EARTH_RADIUS_KM * c
}

fn build_graph(servers: &[(usize, f64, f64, u8)]) -> HashMap<usize, Vec<Edge>> {
    let mut graph = HashMap::new();
    let server_count = servers.len();

    for i in 0..server_count {
        let (id1, lat1, lon1, congestion1) = servers[i];
        let mut edges = Vec::new();

        for j in 0..server_count {
            if i == j {
                continue;
            }

            let (id2, lat2, lon2, congestion2) = servers[j];
            let distance = haversine_distance(lat1, lon1, lat2, lon2);
            let congestion_penalty = CONGESTION_FACTOR * congestion1 as f64 * congestion2 as f64;
            let total_latency = distance + congestion_penalty;

            edges.push(Edge {
                to: id2,
                latency: total_latency,
            });
        }

        graph.insert(id1, edges);
    }

    graph
}

fn dijkstra(
    graph: &HashMap<usize, Vec<Edge>>,
    start: usize,
    end: usize,
) -> Option<(Vec<usize>, f64)> {
    let mut distances: HashMap<usize, f64> = HashMap::new();
    let mut previous: HashMap<usize, usize> = HashMap::new();
    let mut heap = BinaryHeap::new();

    distances.insert(start, 0.0);
    heap.push(NodeDistance {
        node: start,
        distance: 0.0,
    });

    while let Some(NodeDistance { node, distance }) = heap.pop() {
        if node == end {
            let mut path = Vec::new();
            let mut current = node;

            while current != start {
                path.push(current);
                current = previous[&current];
            }
            path.push(start);
            path.reverse();

            return Some((path, distance));
        }

        if distance > *distances.get(&node).unwrap_or(&f64::INFINITY) {
            continue;
        }

        if let Some(edges) = graph.get(&node) {
            for edge in edges {
                let new_distance = distance + edge.latency;

                if new_distance < *distances.get(&edge.to).unwrap_or(&f64::INFINITY) {
                    distances.insert(edge.to, new_distance);
                    previous.insert(edge.to, node);
                    heap.push(NodeDistance {
                        node: edge.to,
                        distance: new_distance,
                    });
                }
            }
        }
    }

    None
}

pub fn optimize_network_latency(
    servers: &[(usize, f64, f64, u8)],
    requests: &[(usize, usize, u32)],
) -> u64 {
    let mut server_map: HashMap<usize, (f64, f64, u8)> = servers
        .iter()
        .map(|&(id, lat, lon, congestion)| (id, (lat, lon, congestion)))
        .collect();

    let mut total_latency = 0.0;

    for &(src, dst, size) in requests {
        let graph = build_graph(
            &server_map
                .iter()
                .map(|(&id, &(lat, lon, congestion))| (id, lat, lon, congestion))
                .collect::<Vec<_>>(),
        );

        if let Some((path, latency)) = dijkstra(&graph, src, dst) {
            let size_factor = (size as f64 / 1000.0).ceil();
            total_latency += latency * size_factor;

            // Update congestion for all servers in the path
            for &node in &path {
                if let Some(server) = server_map.get_mut(&node) {
                    if server.2 < 10 {
                        server.2 += 1;
                    }
                }
            }
        }
    }

    total_latency.ceil() as u64
}