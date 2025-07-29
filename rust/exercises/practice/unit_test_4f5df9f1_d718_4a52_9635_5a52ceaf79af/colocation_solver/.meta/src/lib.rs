use std::collections::{HashMap, HashSet, VecDeque};

/// Represents the resource capacity of a server
pub struct ServerCapacity {
    pub cpu: u32,
    pub memory: u64,
    pub network: u32,
}

type CustomerId = u32;
type VmId = u32;
type ServerId = u32;
type VmIdentifier = (CustomerId, VmId);
type VmResources = (u32, u64, u32); // (cpu, memory, network)

/// Main function to solve the colocation optimization problem
pub fn solve_colocation(
    server_capacity: &ServerCapacity,
    vm_requests: &[(CustomerId, VmId, u32, u64, u32)],
    colocation_restrictions: &[(CustomerId, u32)],
    existing_placements: &HashMap<ServerId, Vec<VmIdentifier>>,
) -> Option<HashMap<ServerId, Vec<VmIdentifier>>> {
    // Step 1: Build a restriction graph for customers who cannot be collocated
    let restriction_graph = build_restriction_graph(colocation_restrictions);
    
    // Step 2: Convert VM requests to a more usable format and track which VMs need placement
    let vm_resources: HashMap<VmIdentifier, VmResources> = vm_requests
        .iter()
        .map(|&(cust_id, vm_id, cpu, mem, net)| ((cust_id, vm_id), (cpu, mem, net)))
        .collect();

    // Step 3: Process existing placements and validate them
    let mut current_placements = process_existing_placements(
        existing_placements,
        &vm_resources,
        server_capacity,
        &restriction_graph,
    )?;

    // Find the highest used server ID to continue from there
    let mut next_server_id = existing_placements.keys().fold(0, |acc, &id| acc.max(id)) + 1;
    
    // Step 4: Create a set of VMs that need to be placed (not in existing placements)
    let placed_vms: HashSet<VmIdentifier> = current_placements
        .values()
        .flat_map(|vms| vms.iter().cloned())
        .collect();
    
    let unplaced_vms: Vec<VmIdentifier> = vm_requests
        .iter()
        .map(|&(cust_id, vm_id, _, _, _)| (cust_id, vm_id))
        .filter(|vm_id| !placed_vms.contains(vm_id))
        .collect();
    
    // No VMs to place? We're done
    if unplaced_vms.is_empty() {
        return Some(current_placements);
    }
    
    // Step 5: Sort VMs by resource requirements (descending) for better bin packing
    let mut sorted_vms = unplaced_vms;
    sorted_vms.sort_by(|a, b| {
        let res_a = vm_resources.get(a).unwrap();
        let res_b = vm_resources.get(b).unwrap();
        // Sort by CPU, then memory, then network (all descending)
        res_b.0.cmp(&res_a.0)
            .then(res_b.1.cmp(&res_a.1))
            .then(res_b.2.cmp(&res_a.2))
    });
    
    // Step 6: Try to place VMs with a best-fit bin packing algorithm
    if !place_vms(
        &sorted_vms,
        &vm_resources,
        server_capacity,
        &restriction_graph,
        &mut current_placements,
        &mut next_server_id,
    ) {
        return None;
    }
    
    // Step 7: Ensure server IDs are contiguous starting from 1
    let result = renumber_servers(current_placements);
    
    Some(result)
}

// Build a graph of colocation restrictions
fn build_restriction_graph(restrictions: &[(CustomerId, CustomerId)]) -> HashMap<CustomerId, HashSet<CustomerId>> {
    let mut graph: HashMap<CustomerId, HashSet<CustomerId>> = HashMap::new();
    
    for &(customer1, customer2) in restrictions {
        // Add restriction in both directions
        graph.entry(customer1).or_default().insert(customer2);
        graph.entry(customer2).or_default().insert(customer1);
    }
    
    graph
}

// Process and validate existing placements
fn process_existing_placements(
    existing: &HashMap<ServerId, Vec<VmIdentifier>>,
    vm_resources: &HashMap<VmIdentifier, VmResources>,
    capacity: &ServerCapacity,
    restrictions: &HashMap<CustomerId, HashSet<CustomerId>>,
) -> Option<HashMap<ServerId, Vec<VmIdentifier>>> {
    let mut result = HashMap::new();
    
    for (&server_id, vms) in existing {
        // Check if all VMs in existing placements have resource requirements
        for &vm in vms {
            if !vm_resources.contains_key(&vm) {
                return None; // VM in existing placement not in requests
            }
        }
        
        // Validate resource constraints
        let (total_cpu, total_mem, total_net) = calculate_server_usage(vms, vm_resources);
        if total_cpu > capacity.cpu || total_mem > capacity.memory || total_net > capacity.network {
            return None; // Server overloaded
        }
        
        // Validate colocation restrictions
        if !validate_colocation(vms, restrictions) {
            return None; // Colocation restriction violated
        }
        
        result.insert(server_id, vms.clone());
    }
    
    Some(result)
}

// Calculate total resource usage on a server
fn calculate_server_usage(
    vms: &[VmIdentifier],
    vm_resources: &HashMap<VmIdentifier, VmResources>,
) -> (u32, u64, u32) {
    vms.iter().fold((0, 0, 0), |(cpu, mem, net), &vm| {
        let (vm_cpu, vm_mem, vm_net) = vm_resources.get(&vm).unwrap();
        (cpu + vm_cpu, mem + vm_mem, net + vm_net)
    })
}

// Validate that no colocation restrictions are violated
fn validate_colocation(
    vms: &[VmIdentifier],
    restrictions: &HashMap<CustomerId, HashSet<CustomerId>>,
) -> bool {
    let customers: HashSet<CustomerId> = vms.iter().map(|&(cust_id, _)| cust_id).collect();
    
    for &(cust_id, _) in vms {
        if let Some(restricted) = restrictions.get(&cust_id) {
            for &other_cust in restricted {
                if customers.contains(&other_cust) {
                    return false; // Restriction violated
                }
            }
        }
    }
    
    true
}

// Try to place all unplaced VMs
fn place_vms(
    vms: &[VmIdentifier],
    vm_resources: &HashMap<VmIdentifier, VmResources>,
    capacity: &ServerCapacity,
    restrictions: &HashMap<CustomerId, HashSet<CustomerId>>,
    placements: &mut HashMap<ServerId, Vec<VmIdentifier>>,
    next_server_id: &mut ServerId,
) -> bool {
    // Implement a best-fit bin packing algorithm
    for &vm in vms {
        let (vm_cpu, vm_mem, vm_net) = *vm_resources.get(&vm).unwrap();
        let (cust_id, _) = vm;
        
        // Try to place this VM on an existing server with best fit
        let mut best_server: Option<ServerId> = None;
        let mut best_remaining_space = (u32::MAX, u64::MAX, u32::MAX);
        
        for (&server_id, server_vms) in placements.iter() {
            // Check colocation restrictions
            if !can_colocate(cust_id, server_vms, restrictions) {
                continue;
            }
            
            // Calculate remaining capacity
            let (used_cpu, used_mem, used_net) = calculate_server_usage(server_vms, vm_resources);
            
            // Check if VM fits
            if capacity.cpu >= used_cpu + vm_cpu && 
               capacity.memory >= used_mem + vm_mem && 
               capacity.network >= used_net + vm_net {
                
                // Calculate remaining space after placing
                let remaining = (
                    capacity.cpu - (used_cpu + vm_cpu),
                    capacity.memory - (used_mem + vm_mem),
                    capacity.network - (used_net + vm_net),
                );
                
                // Use a heuristic to find the best fit
                // We consider the server with the least remaining space (but still fits) to be the best fit
                if best_remaining_space.0 > remaining.0 ||
                   (best_remaining_space.0 == remaining.0 && best_remaining_space.1 > remaining.1) ||
                   (best_remaining_space.0 == remaining.0 && best_remaining_space.1 == remaining.1 && best_remaining_space.2 > remaining.2) {
                    best_remaining_space = remaining;
                    best_server = Some(server_id);
                }
            }
        }
        
        // Place VM on best server or create a new one
        if let Some(server_id) = best_server {
            placements.get_mut(&server_id).unwrap().push(vm);
        } else {
            // No existing server can host this VM, create a new one
            if vm_cpu > capacity.cpu || vm_mem > capacity.memory || vm_net > capacity.network {
                return false; // VM too large for any server
            }
            
            placements.insert(*next_server_id, vec![vm]);
            *next_server_id += 1;
        }
    }
    
    true
}

// Check if a customer can be collocated with existing VMs on a server
fn can_colocate(
    customer_id: CustomerId,
    server_vms: &[VmIdentifier],
    restrictions: &HashMap<CustomerId, HashSet<CustomerId>>,
) -> bool {
    // Get customers already on this server
    let server_customers: HashSet<CustomerId> = server_vms.iter().map(|&(cust_id, _)| cust_id).collect();
    
    // Check if any restrictions would be violated
    if let Some(restricted) = restrictions.get(&customer_id) {
        for &restricted_customer in restricted {
            if server_customers.contains(&restricted_customer) {
                return false; // Cannot collocate
            }
        }
    }
    
    true
}

// Ensure server IDs are contiguous starting from 1
fn renumber_servers(
    placements: HashMap<ServerId, Vec<VmIdentifier>>,
) -> HashMap<ServerId, Vec<VmIdentifier>> {
    if placements.is_empty() {
        return placements;
    }
    
    let mut result = HashMap::new();
    let mut server_ids: Vec<ServerId> = placements.keys().cloned().collect();
    server_ids.sort();
    
    // Perform a BFS to handle any gaps in server IDs
    let mut queue = VecDeque::new();
    queue.push_back(1); // Start with server ID 1
    let mut seen = HashSet::new();
    seen.insert(1);
    
    let mut next_id = 1;
    
    while let Some(original_id) = queue.pop_front() {
        // Map the original ID to the next available contiguous ID
        if let Some(vms) = placements.get(&original_id) {
            result.insert(next_id, vms.clone());
            next_id += 1;
        }
        
        // Add neighboring server IDs to the queue
        for &id in &server_ids {
            if !seen.contains(&id) {
                queue.push_back(id);
                seen.insert(id);
            }
        }
    }
    
    // Handle any servers not visited in BFS (if there are gaps)
    for (&id, vms) in placements.iter() {
        if !result.values().any(|server_vms| server_vms == vms) {
            result.insert(next_id, vms.clone());
            next_id += 1;
        }
    }
    
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_simple_case() {
        let server_capacity = ServerCapacity {
            cpu: 8,
            memory: 16 * 1024 * 1024 * 1024, // 16GB
            network: 1000,
        };
        
        let vm_requests = vec![
            (1, 101, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 1, VM 101
            (1, 102, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 1, VM 102
            (2, 201, 4, 8 * 1024 * 1024 * 1024, 400), // Customer 2, VM 201
        ];
        
        let colocation_restrictions: Vec<(u32, u32)> = vec![(1, 2)]; // Customer 1 and 2 cannot be collocated
        let existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();
        
        let result = solve_colocation(
            &server_capacity,
            &vm_requests,
            &colocation_restrictions,
            &existing_placements,
        );
        
        assert!(result.is_some());
        let placement = result.unwrap();
        assert_eq!(placement.len(), 2); // Should use 2 servers
    }
}