use std::collections::HashMap;

pub fn check_consistency(
    num_data_nodes: usize,
    file_metadata: Vec<(String, usize)>,
    data_node_contents: Vec<HashMap<(String, usize), Vec<u8>>>,
    primary_nodes: HashMap<(String, usize), usize>,
) -> Vec<(String, usize, usize)> {
    let mut inconsistencies = Vec::new();

    // Iterate over each data node's contents along with its index.
    for (node_index, node_contents) in data_node_contents.iter().enumerate() {
        // For every chunk stored on this node.
        for (key, replica_chunk) in node_contents.iter() {
            // key is (file_id, chunk_index)
            if let Some(&primary_index) = primary_nodes.get(key) {
                // Only check replicas on non-primary nodes.
                if primary_index != node_index {
                    // Retrieve the primary node's content for the key.
                    if let Some(primary_chunk) = data_node_contents[primary_index].get(key) {
                        // Compare the chunk contents.
                        if primary_chunk != replica_chunk {
                            let (file_id, chunk_index) = key;
                            inconsistencies.push((file_id.clone(), *chunk_index, node_index));
                        }
                    }
                }
            }
        }
    }
    inconsistencies
}