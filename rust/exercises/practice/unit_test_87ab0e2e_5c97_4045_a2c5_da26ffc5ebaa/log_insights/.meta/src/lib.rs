use std::collections::HashMap;

pub fn query_logs(
    _num_nodes: usize,
    _edges: Vec<(usize, usize)>,
    logs: Vec<(usize, Vec<(u64, String, String)>)>,
    queries: Vec<(u64, u64, String)>
) -> Vec<usize> {
    let mut severity_map: HashMap<String, Vec<u64>> = HashMap::new();
    
    for (_node_id, log_entries) in logs.into_iter() {
        for (timestamp, severity, _message) in log_entries.into_iter() {
            severity_map.entry(severity).or_insert_with(Vec::new).push(timestamp);
        }
    }
    
    // Sort timestamps for each severity for binary search.
    for timestamps in severity_map.values_mut() {
        timestamps.sort_unstable();
    }
    
    let mut results = Vec::with_capacity(queries.len());
    for (start, end, severity) in queries.into_iter() {
        if let Some(timestamps) = severity_map.get(&severity) {
            let left = timestamps.partition_point(|&ts| ts < start);
            let right = timestamps.partition_point(|&ts| ts <= end);
            results.push(right - left);
        } else {
            results.push(0);
        }
    }
    
    results
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_queries() {
        let num_nodes = 3;
        let edges = vec![(1, 0), (2, 0)];
        let logs = vec![
            (1, vec![
                (1000, "Error".to_string(), "Something went wrong".to_string()),
                (2000, "Warning".to_string(), "Low memory".to_string()),
            ]),
            (2, vec![
                (1500, "Info".to_string(), "Service started".to_string()),
                (2500, "Debug".to_string(), "Variable x = 5".to_string()),
            ]),
        ];
        let queries = vec![
            (1200, 2200, "Warning".to_string()),
            (1000, 3000, "Info".to_string()),
            (0, 1100, "Error".to_string()),
        ];
        let expected = vec![1, 1, 1];
        let result = query_logs(num_nodes, edges, logs, queries);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_multiple_entries_same_severity() {
        let num_nodes = 4;
        let edges = vec![(1, 0), (2, 0), (3, 0)];
        let logs = vec![
            (1, vec![
                (500, "Error".to_string(), "Disk failure".to_string()),
                (1500, "Error".to_string(), "Disk failure again".to_string()),
            ]),
            (2, vec![
                (1000, "Error".to_string(), "Memory leak".to_string()),
                (2000, "Error".to_string(), "Critical error".to_string()),
            ]),
            (3, vec![
                (2500, "Error".to_string(), "Service halted".to_string()),
            ]),
        ];
        let queries = vec![
            (0, 1000, "Error".to_string()),
            (1500, 2500, "Error".to_string()),
            (0, 3000, "Error".to_string()),
        ];
        let expected = vec![2, 3, 5];
        let result = query_logs(num_nodes, edges, logs, queries);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_various_severities() {
        let num_nodes = 5;
        let edges = vec![(1, 0), (2, 0), (3, 0), (4, 0)];
        let logs = vec![
            (1, vec![
                (100, "Info".to_string(), "Startup complete".to_string()),
            ]),
            (2, vec![
                (200, "Warning".to_string(), "High temperature".to_string()),
                (300, "Warning".to_string(), "Temperature normal".to_string()),
            ]),
            (3, vec![
                (150, "Debug".to_string(), "Checking configs".to_string()),
                (350, "Debug".to_string(), "Configs valid".to_string()),
            ]),
            (4, vec![
                (400, "Error".to_string(), "Service crash".to_string()),
            ]),
        ];
        let queries = vec![
            (0, 250, "Info".to_string()),
            (0, 350, "Warning".to_string()),
            (100, 400, "Debug".to_string()),
            (300, 500, "Error".to_string()),
            (0, 500, "Critical".to_string()),
        ];
        let expected = vec![1, 2, 2, 1, 0];
        let result = query_logs(num_nodes, edges, logs, queries);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_empty_queries() {
        let num_nodes = 2;
        let edges = vec![(1, 0)];
        let logs = vec![
            (1, vec![
                (1000, "Info".to_string(), "Started".to_string()),
            ]),
        ];
        let queries: Vec<(u64, u64, String)> = vec![];
        let expected: Vec<usize> = vec![];
        let result = query_logs(num_nodes, edges, logs, queries);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_query_no_matching_logs() {
        let num_nodes = 3;
        let edges = vec![(1, 0), (2, 0)];
        let logs = vec![
            (1, vec![
                (1000, "Error".to_string(), "Issue detected".to_string()),
            ]),
            (2, vec![
                (2000, "Warning".to_string(), "Minor issue".to_string()),
            ]),
        ];
        let queries = vec![
            (1500, 1600, "Error".to_string()),
            (0, 900, "Warning".to_string()),
        ];
        let expected = vec![0, 0];
        let result = query_logs(num_nodes, edges, logs, queries);
        assert_eq!(result, expected);
    }
}