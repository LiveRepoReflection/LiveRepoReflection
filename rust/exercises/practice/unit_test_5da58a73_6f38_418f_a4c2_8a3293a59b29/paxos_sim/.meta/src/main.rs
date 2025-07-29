use paxos_sim::ConsensusSimulator;
use std::env;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 6 {
        eprintln!("Usage: {} <num_nodes> <accept_probability> <fault_percentage> <max_rounds> <seed> [initial_states...]", args[0]);
        process::exit(1);
    }
    
    // Parse command-line arguments
    let num_nodes = match args[1].parse::<usize>() {
        Ok(n) => n,
        Err(_) => {
            eprintln!("Error: num_nodes must be a non-negative integer");
            process::exit(1);
        }
    };
    
    let accept_probability = match args[2].parse::<f64>() {
        Ok(p) if p >= 0.0 && p <= 1.0 => p,
        _ => {
            eprintln!("Error: accept_probability must be between 0.0 and 1.0");
            process::exit(1);
        }
    };
    
    let fault_percentage = match args[3].parse::<f64>() {
        Ok(p) if p >= 0.0 && p <= 1.0 => p,
        _ => {
            eprintln!("Error: fault_percentage must be between 0.0 and 1.0");
            process::exit(1);
        }
    };
    
    let max_rounds = match args[4].parse::<usize>() {
        Ok(n) if n >= 1 || num_nodes == 0 => n,
        _ => {
            eprintln!("Error: max_rounds must be at least 1");
            process::exit(1);
        }
    };
    
    let seed = match args[5].parse::<u64>() {
        Ok(s) => s,
        Err(_) => {
            eprintln!("Error: seed must be a non-negative integer");
            process::exit(1);
        }
    };
    
    // Parse initial states if provided
    let initial_states: Vec<i64> = if args.len() > 6 {
        args[6..].iter().filter_map(|s| s.parse::<i64>().ok()).collect()
    } else {
        Vec::new()
    };
    
    // Create and run the simulator
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    println!("Running consensus simulation with:");
    println!("  Nodes: {}", num_nodes);
    println!("  Accept probability: {}", accept_probability);
    println!("  Fault percentage: {}", fault_percentage);
    println!("  Max rounds: {}", max_rounds);
    println!("  Seed: {}", seed);
    
    let consensus_reached = simulator.run_simulation();
    
    // Output the results
    println!("\nSimulation complete");
    println!("Consensus reached: {}", consensus_reached);
    
    if num_nodes > 0 {
        let (unique_states, most_common_state, count) = simulator.get_state_statistics();
        println!("Number of unique states: {}", unique_states);
        println!("Most common state: {} (count: {})", most_common_state, count);
        
        // Show distribution of states for small numbers of nodes
        if num_nodes <= 20 {
            println!("\nFinal states:");
            for (i, state) in simulator.get_node_states().iter().enumerate() {
                let is_byzantine = simulator.get_byzantine_nodes()[i];
                println!("  Node {}: {} {}", i, state, if is_byzantine { "(Byzantine)" } else { "" });
            }
        }
    }
}