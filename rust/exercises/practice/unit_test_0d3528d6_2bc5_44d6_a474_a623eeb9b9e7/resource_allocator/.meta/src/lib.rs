use std::collections::{HashMap, HashSet, VecDeque};

#[derive(Debug, Clone)]
pub struct Machine {
    pub id: u32,
    pub cpu: u32,
    pub memory: u32,
    pub network: u32,
}

#[derive(Debug, Clone)]
pub struct Task {
    pub id: u32,
    pub cpu: u32,
    pub memory: u32,
    pub network: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Allocation {
    pub task_id: u32,
    pub machine_id: u32,
}

struct MachineState {
    machine: Machine,
    remaining_cpu: u32,
    remaining_memory: u32,
    remaining_network: u32,
}

impl MachineState {
    fn new(machine: Machine) -> Self {
        MachineState {
            remaining_cpu: machine.cpu,
            remaining_memory: machine.memory,
            remaining_network: machine.network,
            machine,
        }
    }

    fn can_accommodate(&self, task: &Task) -> bool {
        self.remaining_cpu >= task.cpu &&
        self.remaining_memory >= task.memory &&
        self.remaining_network >= task.network
    }

    fn allocate(&mut self, task: &Task) {
        self.remaining_cpu -= task.cpu;
        self.remaining_memory -= task.memory;
        self.remaining_network -= task.network;
    }
}

fn detect_cycles(
    task_id: u32,
    dependencies: &HashMap<u32, Vec<u32>>,
    visited: &mut HashSet<u32>,
    path: &mut HashSet<u32>,
) -> bool {
    if !visited.insert(task_id) {
        return path.contains(&task_id);
    }
    
    path.insert(task_id);
    
    if let Some(deps) = dependencies.get(&task_id) {
        for &dep in deps {
            if path.contains(&dep) || detect_cycles(dep, dependencies, visited, path) {
                return true;
            }
        }
    }
    
    path.remove(&task_id);
    false
}

fn has_cycles(dependencies: &HashMap<u32, Vec<u32>>) -> bool {
    let mut visited = HashSet::new();
    let mut path = HashSet::new();
    
    for &task_id in dependencies.keys() {
        if detect_cycles(task_id, dependencies, &mut visited, &mut path) {
            return true;
        }
    }
    false
}

fn calculate_in_degrees(tasks: &[Task], dependencies: &HashMap<u32, Vec<u32>>) -> HashMap<u32, usize> {
    let mut in_degrees = HashMap::new();
    
    // Initialize all tasks with in-degree 0
    for task in tasks {
        in_degrees.insert(task.id, 0);
    }
    
    // Count dependencies
    for deps in dependencies.values() {
        for &dep_id in deps {
            *in_degrees.entry(dep_id).or_insert(0) += 1;
        }
    }
    
    in_degrees
}

fn get_reverse_dependencies(tasks: &[Task], dependencies: &HashMap<u32, Vec<u32>>) -> HashMap<u32, Vec<u32>> {
    let mut reverse_deps = HashMap::new();
    
    // Initialize empty vectors for all tasks
    for task in tasks {
        reverse_deps.insert(task.id, Vec::new());
    }
    
    // Build reverse dependencies
    for (&task_id, deps) in dependencies {
        for &dep_id in deps {
            reverse_deps.entry(dep_id).or_default().push(task_id);
        }
    }
    
    reverse_deps
}

pub fn allocate_resources(
    machines: &[Machine],
    tasks: &[Task],
    dependencies: &HashMap<u32, Vec<u32>>
) -> Vec<Allocation> {
    // Check for cycles in dependencies
    if has_cycles(dependencies) {
        return Vec::new();
    }

    let mut machine_states: Vec<MachineState> = machines.iter()
        .cloned()
        .map(MachineState::new)
        .collect();

    let mut allocations = Vec::new();
    let mut in_degrees = calculate_in_degrees(tasks, dependencies);
    let reverse_deps = get_reverse_dependencies(tasks, dependencies);
    let mut available_tasks: VecDeque<&Task> = tasks.iter()
        .filter(|task| in_degrees.get(&task.id).unwrap_or(&0) == &0)
        .collect();

    while let Some(task) = available_tasks.pop_front() {
        let mut allocated = false;

        // Try to find the best fit machine for this task
        for machine_state in &mut machine_states {
            if machine_state.can_accommodate(task) {
                machine_state.allocate(task);
                allocations.push(Allocation {
                    task_id: task.id,
                    machine_id: machine_state.machine.id,
                });
                allocated = true;

                // Update dependencies
                if let Some(dependent_tasks) = reverse_deps.get(&task.id) {
                    for &dep_task_id in dependent_tasks {
                        if let Some(in_degree) = in_degrees.get_mut(&dep_task_id) {
                            *in_degree -= 1;
                            if *in_degree == 0 {
                                if let Some(dep_task) = tasks.iter().find(|t| t.id == dep_task_id) {
                                    available_tasks.push_back(dep_task);
                                }
                            }
                        }
                    }
                }
                break;
            }
        }

        if !allocated {
            // If we couldn't allocate a task with no dependencies, we can't proceed
            return Vec::new();
        }
    }

    allocations
}