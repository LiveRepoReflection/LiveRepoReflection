pub fn distributed_kmeans(
    data: Vec<Vec<f64>>,
    num_nodes: usize,
    k: usize,
    iterations: usize,
    initial_centroids: Vec<Vec<f64>>,
) -> Vec<Vec<f64>> {
    if data.is_empty() || k == 0 {
        return vec![];
    }

    // Assume dimensions are consistent and taken from the first data point.
    let dim = data[0].len();

    // Validate that each centroid has the correct dimensionality.
    if initial_centroids.len() != k || initial_centroids.iter().any(|c| c.len() != dim) {
        // Inconsistent dimensions or invalid number of centroids.
        return vec![];
    }

    // Ensure that num_nodes is at least 1.
    let nodes = if num_nodes < 1 { 1 } else { num_nodes };

    // Partition the data into roughly equal chunks for each node.
    let partitions = partition_data(&data, nodes);

    // Initialize centroids to the initial ones given.
    let mut centroids = initial_centroids;

    // Run fixed number of iterations.
    for _ in 0..iterations {
        // Global accumulators for each centroid: sum of coordinates and count.
        let mut global_sums = vec![vec![0.0; dim]; k];
        let mut global_counts = vec![0usize; k];

        // Simulate distributed computation.
        for partition in &partitions {
            // For each node, initialize local accumulators.
            let mut local_sums = vec![vec![0.0; dim]; k];
            let mut local_counts = vec![0usize; k];

            // For each data point in the partition, assign to nearest centroid.
            for point in partition {
                let nearest = nearest_centroid(point, &centroids);
                // Add the point to the corresponding cluster.
                for d in 0..dim {
                    local_sums[nearest][d] += point[d];
                }
                local_counts[nearest] += 1;
            }

            // Aggregate local accumulators into global accumulators.
            for j in 0..k {
                for d in 0..dim {
                    global_sums[j][d] += local_sums[j][d];
                }
                global_counts[j] += local_counts[j];
            }
        }

        // Update centroids globally, respecting nodes that did not contribute.
        for j in 0..k {
            if global_counts[j] > 0 {
                for d in 0..dim {
                    centroids[j][d] = global_sums[j][d] / (global_counts[j] as f64);
                }
            }
            // If global_counts[j] == 0, retain the current centroid.
        }
    }

    centroids
}

// Helper: Partition data into `nodes` groups as evenly as possible.
fn partition_data(data: &Vec<Vec<f64>>, nodes: usize) -> Vec<Vec<Vec<f64>>> {
    let n = data.len();
    let mut partitions: Vec<Vec<Vec<f64>>> = Vec::with_capacity(nodes);
    let base_size = n / nodes;
    let remainder = n % nodes;
    let mut start = 0;
    for i in 0..nodes {
        let extra = if i < remainder { 1 } else { 0 };
        let end = start + base_size + extra;
        // Use slice to create a partition, then clone the data points.
        let part = data[start..end].to_vec();
        partitions.push(part);
        start = end;
    }
    partitions
}

// Helper: Compute the Euclidean distance squared between two points.
fn distance_sq(point: &Vec<f64>, centroid: &Vec<f64>) -> f64 {
    point
        .iter()
        .zip(centroid.iter())
        .map(|(a, b)| {
            let diff = a - b;
            diff * diff
        })
        .sum()
}

// Helper: Find the index of the nearest centroid for a given point.
fn nearest_centroid(point: &Vec<f64>, centroids: &Vec<Vec<f64>>) -> usize {
    let mut best_index = 0;
    let mut best_distance = distance_sq(point, &centroids[0]);
    for (i, centroid) in centroids.iter().enumerate().skip(1) {
        let dist = distance_sq(point, centroid);
        if dist < best_distance {
            best_distance = dist;
            best_index = i;
        }
    }
    best_index
}