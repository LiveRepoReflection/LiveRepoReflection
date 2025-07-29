use std::collections::HashMap;
use dfs_consistency::check_consistency;

#[test]
fn test_basic_inconsistency() {
    let num_data_nodes = 2;
    let file_metadata = vec![("file1".to_string(), 2)];
    let mut node0 = HashMap::new();
    let mut node1 = HashMap::new();
    node0.insert(("file1".to_string(), 0), vec![1, 2, 3]);
    node0.insert(("file1".to_string(), 1), vec![4, 5, 6]);
    node1.insert(("file1".to_string(), 0), vec![1, 2, 3]);
    node1.insert(("file1".to_string(), 1), vec![4, 5, 7]); // Inconsistent chunk

    let data_node_contents = vec![node0, node1];
    let mut primary_nodes = HashMap::new();
    primary_nodes.insert(("file1".to_string(), 0), 0);
    primary_nodes.insert(("file1".to_string(), 1), 0);

    let mut result = check_consistency(num_data_nodes, file_metadata.clone(), data_node_contents, primary_nodes);
    result.sort();
    let expected = vec![
        ("file1".to_string(), 1, 1)
    ];
    assert_eq!(result, expected);
}

#[test]
fn test_all_consistent() {
    let num_data_nodes = 3;
    let file_metadata = vec![("file2".to_string(), 3)];
    let mut node0 = HashMap::new();
    let mut node1 = HashMap::new();
    let mut node2 = HashMap::new();
    node0.insert(("file2".to_string(), 0), vec![10]);
    node0.insert(("file2".to_string(), 1), vec![20]);
    node0.insert(("file2".to_string(), 2), vec![30]);
    node1.insert(("file2".to_string(), 0), vec![10]);
    node1.insert(("file2".to_string(), 1), vec![20]);
    node1.insert(("file2".to_string(), 2), vec![30]);
    node2.insert(("file2".to_string(), 0), vec![10]);
    node2.insert(("file2".to_string(), 1), vec![20]);
    node2.insert(("file2".to_string(), 2), vec![30]);

    let data_node_contents = vec![node0, node1, node2];
    let mut primary_nodes = HashMap::new();
    primary_nodes.insert(("file2".to_string(), 0), 0);
    primary_nodes.insert(("file2".to_string(), 1), 1);
    primary_nodes.insert(("file2".to_string(), 2), 2);

    let result = check_consistency(num_data_nodes, file_metadata.clone(), data_node_contents, primary_nodes);
    let expected: Vec<(String, usize, usize)> = vec![];
    assert_eq!(result, expected);
}

#[test]
fn test_multiple_inconsistencies() {
    let num_data_nodes = 3;
    let file_metadata = vec![
        ("file3".to_string(), 2),
        ("file4".to_string(), 2)
    ];
    let mut node0 = HashMap::new();
    let mut node1 = HashMap::new();
    let mut node2 = HashMap::new();

    // File3: Primary on node0 for both chunks.
    node0.insert(("file3".to_string(), 0), vec![1, 1]);
    node0.insert(("file3".to_string(), 1), vec![2, 2]);
    node1.insert(("file3".to_string(), 0), vec![1, 1]); // Consistent replica
    node1.insert(("file3".to_string(), 1), vec![2, 3]); // Inconsistent replica
    node2.insert(("file3".to_string(), 0), vec![1, 2]); // Inconsistent replica
    
    // File4: Primary on node1 for both chunks.
    node1.insert(("file4".to_string(), 0), vec![7, 7, 7]);
    node1.insert(("file4".to_string(), 1), vec![]);
    node0.insert(("file4".to_string(), 0), vec![7, 7, 8]); // Inconsistent replica
    node2.insert(("file4".to_string(), 1), vec![]); // Consistent replica

    let data_node_contents = vec![node0, node1, node2];
    let mut primary_nodes = HashMap::new();
    // File3 primary (node0)
    primary_nodes.insert(("file3".to_string(), 0), 0);
    primary_nodes.insert(("file3".to_string(), 1), 0);
    // File4 primary (node1)
    primary_nodes.insert(("file4".to_string(), 0), 1);
    primary_nodes.insert(("file4".to_string(), 1), 1);

    let mut result = check_consistency(num_data_nodes, file_metadata.clone(), data_node_contents, primary_nodes);
    result.sort();
    let mut expected = vec![
        ("file3".to_string(), 0, 2),
        ("file3".to_string(), 1, 1),
        ("file4".to_string(), 0, 0)
    ];
    expected.sort();
    assert_eq!(result, expected);
}

#[test]
fn test_empty_chunks_and_missing_chunks() {
    let num_data_nodes = 2;
    let file_metadata = vec![("file5".to_string(), 3)];
    let mut node0 = HashMap::new();
    let mut node1 = HashMap::new();

    // file5: chunk 0 is empty, chunk 1 contains data, chunk 2 is missing on node1.
    node0.insert(("file5".to_string(), 0), vec![]);
    node0.insert(("file5".to_string(), 1), vec![9]);
    node0.insert(("file5".to_string(), 2), vec![8, 8]);
    node1.insert(("file5".to_string(), 0), vec![]);
    node1.insert(("file5".to_string(), 1), vec![9, 0]); // Inconsistent due to different size/content

    let data_node_contents = vec![node0, node1];
    let mut primary_nodes = HashMap::new();
    primary_nodes.insert(("file5".to_string(), 0), 0);
    primary_nodes.insert(("file5".to_string(), 1), 0);
    primary_nodes.insert(("file5".to_string(), 2), 0);

    let mut result = check_consistency(num_data_nodes, file_metadata.clone(), data_node_contents, primary_nodes);
    result.sort();
    let expected = vec![
        ("file5".to_string(), 1, 1)
    ];
    assert_eq!(result, expected);
}