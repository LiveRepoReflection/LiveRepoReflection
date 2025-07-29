pub fn simulate(n: usize, f: usize, byzantine_nodes: Vec<usize>, rounds: usize, initial_values: Vec<u8>) -> Vec<u8> {
    // In this simplified simulation, the consensus is determined solely by the leader in the final round.
    // The leader for round i is determined by: leader = (i - 1) mod n, for rounds starting with 1.
    // If the final round leader is honest (not Byzantine), then its proposed value is adopted by all nodes.
    // Otherwise, if the leader is Byzantine, consensus fails for that round and nodes default to their initial value.
    let leader = (rounds - 1) % n;
    if byzantine_nodes.contains(&leader) {
        // Consensus fails; nodes do not update their values.
        initial_values
    } else {
        // Consensus success; all nodes adopt the leader's proposed value,
        // which is assumed to be the leader's initial value.
        let consensus_value = initial_values[leader];
        vec![consensus_value; n]
    }
}