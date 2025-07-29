use std::collections::HashMap;

pub struct Node {
    pub id: usize,
    pub partition_id: usize,
}

pub fn min_moves(nodes: &[Node], _adj_matrix: &Vec<Vec<bool>>, k: usize) -> usize {
    let mut partition_count: HashMap<usize, usize> = HashMap::new();

    // Count the occurrences of each partition_id.
    for node in nodes {
        *partition_count.entry(node.partition_id).or_insert(0) += 1;
    }

    // For each partition, if the number of nodes exceeds k, add the surplus to moves.
    partition_count
        .values()
        .fold(0, |moves, &count| moves + if count > k { count - k } else { 0 })
}