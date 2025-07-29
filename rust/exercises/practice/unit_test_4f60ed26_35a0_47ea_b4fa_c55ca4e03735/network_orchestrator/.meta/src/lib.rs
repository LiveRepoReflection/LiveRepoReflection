use std::collections::{HashMap, BinaryHeap};
use std::cmp::Ordering;

pub type NodeId = u32;
pub type TaskId = u32;

const CPU_WEIGHT: f64 = 0.4;
const MEM_WEIGHT: f64 = 0.6;
const MAX_LATENCY: i32 = i32::MAX;

#[derive(Debug, Clone)]
pub struct Node {
    pub id: NodeId,
    pub capabilities: Vec<String>,
    pub cpu_cores: u32,
    pub memory_mb: u32,
    pub available_cpu: u32,
    pub available_memory: u32,
}

#[derive(Debug, Clone)]
pub struct Task {
    pub id: TaskId,
    pub required_capability: String,
    pub cpu_cores: u32,
    pub memory_mb: u32,
}

#[derive(Debug, Copy, Clone, Eq, PartialEq)]
struct Assignment {
    task_id: TaskId,
    node_id: NodeId,
    cost: i32,
}

impl Ord for Assignment {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost)
    }
}

impl PartialOrd for Assignment {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn calculate_cost(
    task: &Task,
    node: &Node,
    latency: i32,
) -> i32 {
    let cpu_ratio = task.cpu_cores as f64 / node.cpu_cores as f64;
    let mem_ratio = task.memory_mb as f64 / node.memory_mb as f64;
    let resource_cost = (CPU_WEIGHT * cpu_ratio + MEM_WEIGHT * mem_ratio) * 100.0;
    
    resource_cost as i32 + latency
}

fn find_shortest_path(
    network: &HashMap<(NodeId, NodeId), i32>,
    start: NodeId,
    end: NodeId,
    nodes: &HashMap<NodeId, Node>,
) -> i32 {
    if start == end {
        return 0;
    }

    let mut distances: HashMap<NodeId, i32> = nodes
        .keys()
        .map(|&node_id| (node_id, MAX_LATENCY))
        .collect();
    
    distances.insert(start, 0);
    let mut heap = BinaryHeap::new();
    heap.push((0, start));

    while let Some((cost, current)) = heap.pop() {
        let cost = -cost;
        
        if current == end {
            return cost;
        }

        if cost > distances[&current] {
            continue;
        }

        for (&(from, to), &weight) in network.iter() {
            if from == current {
                let next = to;
                let next_cost = cost + weight;

                if next_cost < distances[&next] {
                    distances.insert(next, next_cost);
                    heap.push((-next_cost, next));
                }
            }
        }
    }

    MAX_LATENCY
}

pub fn assign_tasks(
    nodes: HashMap<NodeId, Node>,
    tasks: HashMap<TaskId, Task>,
    network: HashMap<(NodeId, NodeId), i32>,
    requesting_node: NodeId,
) -> Result<HashMap<TaskId, NodeId>, String> {
    if tasks.is_empty() || nodes.is_empty() {
        return Ok(HashMap::new());
    }

    if !nodes.contains_key(&requesting_node) {
        return Err("Requesting node does not exist".to_string());
    }

    let mut assignments = HashMap::new();
    let mut available_nodes = nodes.clone();
    let mut potential_assignments = BinaryHeap::new();

    // Calculate all possible assignments
    for (task_id, task) in tasks.iter() {
        for (node_id, node) in available_nodes.iter() {
            // Check if node has required capability
            if !node.capabilities.contains(&task.required_capability) {
                continue;
            }

            // Check if node has sufficient resources
            if node.available_cpu < task.cpu_cores || node.available_memory < task.memory_mb {
                continue;
            }

            // Calculate latency between requesting node and target node
            let latency = find_shortest_path(&network, requesting_node, *node_id, &nodes);
            if latency == MAX_LATENCY {
                continue;
            }

            let cost = calculate_cost(task, node, latency);
            potential_assignments.push(Assignment {
                task_id: *task_id,
                node_id: *node_id,
                cost,
            });
        }
    }

    // Process assignments in order of increasing cost
    let mut assigned_tasks = HashMap::new();

    while let Some(assignment) = potential_assignments.pop() {
        if assigned_tasks.contains_key(&assignment.task_id) {
            continue;
        }

        let node = available_nodes.get_mut(&assignment.node_id).unwrap();
        let task = tasks.get(&assignment.task_id).unwrap();

        if node.available_cpu >= task.cpu_cores && node.available_memory >= task.memory_mb {
            // Update available resources
            node.available_cpu -= task.cpu_cores;
            node.available_memory -= task.memory_mb;
            
            assignments.insert(assignment.task_id, assignment.node_id);
            assigned_tasks.insert(assignment.task_id, true);
        }
    }

    Ok(assignments)
}