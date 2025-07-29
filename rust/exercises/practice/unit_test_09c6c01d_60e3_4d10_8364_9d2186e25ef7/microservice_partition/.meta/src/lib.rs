pub fn partition(
    servers: Vec<(u64, u64, u64)>,
    edges: Vec<(usize, usize, u64)>,
    microservices: Vec<(u64, u64, u64)>,
    dependencies: Vec<(usize, usize)>,
    k: usize,
) -> Option<Vec<Vec<usize>>> {
    if servers.is_empty() || k == 0 || k > servers.len() {
        return None;
    }
    // Partition the servers into k connected clusters.
    // Step 1: Build Minimum Spanning Tree (MST) using Kruskal's algorithm.
    let n = servers.len();
    let mut all_edges = edges.clone();
    // Remove duplicate edges (since undirected graph provides both (u,v) and (v,u))
    all_edges.sort_unstable_by_key(|&(_, _, w)| w);
    let mut uf = UnionFind::new(n);
    let mut mst_edges = Vec::new();
    for &(u, v, w) in &all_edges {
        if uf.find(u) != uf.find(v) {
            uf.union(u, v);
            mst_edges.push((u, v, w));
        }
    }
    // Check if graph is connected. If not, we need to treat each connected component separately.
    // For simplicity, if the overall number of connected components is more than k, we cannot further partition.
    let mut comp_set = std::collections::HashSet::new();
    for i in 0..n {
        comp_set.insert(uf.find(i));
    }
    let initial_components = comp_set.len();
    if k < initial_components {
        return None;
    }
    // If k equals the total number of servers, then each server is its own cluster.
    // Otherwise, we remove (k - initial_components) highest-weight edges from MST.
    // For a connected graph (initial_components == 1), we need to remove (k - 1) edges.
    let splits_needed = k - initial_components;
    // Sort MST edges by descending weight so that removal yields clusters with minimal disruption.
    mst_edges.sort_unstable_by(|a, b| b.2.cmp(&a.2));
    let edges_to_remove: std::collections::HashSet<(usize, usize)> = mst_edges
        .iter()
        .take(splits_needed)
        .map(|&(u, v, _)| {
            if u < v {
                (u, v)
            } else {
                (v, u)
            }
        })
        .collect();

    // Rebuild union-find over servers, but skip the removed edges.
    let mut uf2 = UnionFind::new(n);
    for &(u, v, _) in &mst_edges {
        let edge_key = if u < v { (u, v) } else { (v, u) };
        if edges_to_remove.contains(&edge_key) {
            continue;
        }
        uf2.union(u, v);
    }
    // Map server id to cluster id.
    let mut cluster_map = vec![0; n];
    let mut cluster_id_map = std::collections::HashMap::new();
    let mut next_cluster_id = 0;
    for i in 0..n {
        let parent = uf2.find(i);
        if !cluster_id_map.contains_key(&parent) {
            cluster_id_map.insert(parent, next_cluster_id);
            next_cluster_id += 1;
        }
        cluster_map[i] = cluster_id_map[&parent];
    }
    // We now have some number of clusters, say num_clusters.
    let num_clusters = next_cluster_id;
    // To meet output requirement of exactly k clusters, we add empty clusters if num_clusters < k.
    let mut final_clusters: Vec<Vec<usize>> = vec![Vec::new(); k];

    // Compute per-cluster capacity: minimum capacity across all servers in that cluster.
    // We'll create a vector of remaining capacities per cluster index.
    // For clusters created from server partition, index them 0..num_clusters.
    let mut cluster_capacity = vec![(u64::MAX, u64::MAX, u64::MAX); num_clusters];
    let mut cluster_servers: Vec<Vec<usize>> = vec![Vec::new(); num_clusters];
    for (server_id, &cid) in cluster_map.iter().enumerate() {
        cluster_servers[cid].push(server_id);
        let (cpu, mem, disk) = servers[server_id];
        let (ref mut cur_cpu, ref mut cur_mem, ref mut cur_disk) = cluster_capacity[cid];
        if cpu < *cur_cpu { *cur_cpu = cpu; }
        if mem < *cur_mem { *cur_mem = mem; }
        if disk < *cur_disk { *cur_disk = disk; }
    }
    // For the purpose of microservice assignment, we order clusters by index.
    // For clusters beyond num_clusters (if k > num_clusters), we duplicate the last cluster's capacity.
    let mut remaining_capacity = vec![(0, 0, 0); k];
    for i in 0..k {
        if i < num_clusters {
            remaining_capacity[i] = cluster_capacity[i];
        } else {
            // For extra clusters, we set capacity to a very high number so they don't limit assignment.
            remaining_capacity[i] = (u64::MAX, u64::MAX, u64::MAX);
        }
    }

    // Build dependency graph (DAG) for microservices and compute in-degrees.
    let m = microservices.len();
    let mut dep_graph: Vec<Vec<usize>> = vec![Vec::new(); m];
    let mut in_degree = vec![0; m];
    for &(a, b) in &dependencies {
        // a depends on b: edge from b -> a
        dep_graph[b].push(a);
        in_degree[a] += 1;
    }
    // Topological sort using Kahn's algorithm.
    let mut topo_order = Vec::with_capacity(m);
    let mut queue = std::collections::VecDeque::new();
    for i in 0..m {
        if in_degree[i] == 0 {
            queue.push_back(i);
        }
    }
    while let Some(u) = queue.pop_front() {
        topo_order.push(u);
        for &v in &dep_graph[u] {
            in_degree[v] -= 1;
            if in_degree[v] == 0 {
                queue.push_back(v);
            }
        }
    }
    if topo_order.len() != m {
        // Cycle detected (should not happen, dependencies is a DAG).
        return None;
    }

    // Microservice assignment tracking: cluster index for each microservice.
    let mut ms_assignment = vec![None; m];

    // For each microservice in topological order, assign it to a cluster.
    // Dependency constraint: if microservice a depends on b, then cluster(b) must be <= cluster(a).
    for &ms in &topo_order {
        // Determine the minimum cluster index allowed for ms.
        let mut min_cluster_allowed = 0;
        // Find all dependencies where ms depends on something.
        // Since dependency is given as (a, b) meaning a depends on b, we need to look for all (ms, x) in dependencies.
        // We scan dependencies vector.
        for &(a, b) in &dependencies {
            if a == ms {
                if let Some(dep_cluster) = ms_assignment[b] {
                    if dep_cluster > min_cluster_allowed {
                        min_cluster_allowed = dep_cluster;
                    }
                }
            }
        }
        // Try to assign ms to a cluster from min_cluster_allowed to k-1.
        let (ms_cpu, ms_mem, ms_disk) = microservices[ms];
        let mut assigned = false;
        for cluster in min_cluster_allowed..k {
            let (rem_cpu, rem_mem, rem_disk) = remaining_capacity[cluster];
            if ms_cpu <= rem_cpu && ms_mem <= rem_mem && ms_disk <= rem_disk {
                // Assign ms to this cluster.
                ms_assignment[ms] = Some(cluster);
                // Subtract resources.
                remaining_capacity[cluster] = (rem_cpu - ms_cpu, rem_mem - ms_mem, rem_disk - ms_disk);
                final_clusters[cluster].push(ms);
                assigned = true;
                break;
            }
        }
        if !assigned {
            return None;
        }
    }

    Some(final_clusters)
}

struct UnionFind {
    parent: Vec<usize>,
    rank: Vec<usize>,
}

impl UnionFind {
    fn new(n: usize) -> Self {
        let mut parent = Vec::with_capacity(n);
        for i in 0..n {
            parent.push(i);
        }
        UnionFind {
            parent,
            rank: vec![0; n],
        }
    }

    fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            let parent = self.parent[x];
            self.parent[x] = self.find(parent);
        }
        self.parent[x]
    }

    fn union(&mut self, x: usize, y: usize) {
        let xroot = self.find(x);
        let yroot = self.find(y);
        if xroot == yroot {
            return;
        }
        if self.rank[xroot] < self.rank[yroot] {
            self.parent[xroot] = yroot;
        } else if self.rank[xroot] > self.rank[yroot] {
            self.parent[yroot] = xroot;
        } else {
            self.parent[yroot] = xroot;
            self.rank[xroot] += 1;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::partition;

    #[test]
    fn test_single_server_single_microservice() {
        let servers = vec![(10, 10, 10)];
        let edges = Vec::new();
        let microservices = vec![(5, 5, 5)];
        let dependencies = vec![];
        let k = 1;
        let result = partition(servers, edges, microservices, dependencies, k);
        assert!(result.is_some());
        let clusters = result.unwrap();
        assert_eq!(clusters.len(), k);
        let all_ms: Vec<usize> = clusters.into_iter().flatten().collect();
        assert_eq!(all_ms.len(), 1);
        assert_eq!(all_ms[0], 0);
    }

    #[test]
    fn test_example_partition() {
        let servers = vec![(10, 10, 10), (12, 12, 12), (15, 15, 15)];
        let edges = vec![(0, 1, 5), (1, 2, 3)];
        let microservices = vec![(3, 3, 3), (2, 2, 2), (4, 4, 4)];
        let dependencies = vec![(0, 1), (2, 0)];
        let k = 2;
        let result = partition(servers, edges, microservices, dependencies, k);
        assert!(result.is_some());
        let clusters = result.unwrap();
        assert_eq!(clusters.len(), k);
        // Ensure that all microservices are assigned exactly once.
        let mut ms_ids: Vec<usize> = clusters.iter().flatten().cloned().collect();
        ms_ids.sort_unstable();
        assert_eq!(ms_ids, vec![0, 1, 2]);
    }

    #[test]
    fn test_impossible_partition_due_to_capacity() {
        // In this case, a microservice requires more resources than available.
        let servers = vec![(2, 2, 2), (2, 2, 2)];
        let edges = vec![(0, 1, 1)];
        let microservices = vec![(3, 0, 0)];
        let dependencies = vec![];
        let k = 1;
        let result = partition(servers, edges, microservices, dependencies, k);
        assert!(result.is_none());
    }

    #[test]
    fn test_dependency_constraint() {
        // Here we create a chain of dependencies in a fully connected graph.
        let servers = vec![(20, 20, 20), (20, 20, 20), (20, 20, 20), (20, 20, 20)];
        let edges = vec![
            (0, 1, 2), (1, 0, 2),
            (1, 2, 2), (2, 1, 2),
            (2, 3, 2), (3, 2, 2),
            (0, 3, 5), (3, 0, 5),
            (0, 2, 4), (2, 0, 4),
            (1, 3, 3), (3, 1, 3)
        ];
        let microservices = vec![
            (5, 5, 5),  // Microservice 0
            (5, 5, 5),  // Microservice 1
            (5, 5, 5),  // Microservice 2
            (5, 5, 5)   // Microservice 3
        ];
        let dependencies = vec![(0, 1), (1, 2), (2, 3)];
        let k = 2;
        let result = partition(servers, edges, microservices, dependencies, k);
        assert!(result.is_some());
        let clusters = result.unwrap();
        assert_eq!(clusters.len(), k);
        // Ensure that all microservices are assigned.
        let mut ms_ids: Vec<usize> = clusters.iter().flatten().cloned().collect();
        ms_ids.sort_unstable();
        assert_eq!(ms_ids, vec![0, 1, 2, 3]);
    }

    #[test]
    fn test_multiple_clusters_increased_complexity() {
        // A more complex scenario with 5 servers, 6 microservices, and multiple dependencies.
        let servers = vec![
            (15, 15, 15), // Server 0
            (10, 10, 10), // Server 1
            (20, 20, 20), // Server 2
            (15, 15, 15), // Server 3
            (25, 25, 25)  // Server 4
        ];
        let edges = vec![
            (0, 1, 3), (1, 0, 3),
            (1, 2, 2), (2, 1, 2),
            (2, 3, 4), (3, 2, 4),
            (3, 4, 1), (4, 3, 1),
            (0, 4, 7), (4, 0, 7)
        ];
        let microservices = vec![
            (5, 5, 5),  // Microservice 0
            (3, 3, 3),  // Microservice 1
            (7, 7, 7),  // Microservice 2
            (4, 4, 4),  // Microservice 3
            (6, 6, 6),  // Microservice 4
            (2, 2, 2)   // Microservice 5
        ];
        let dependencies = vec![
            (0, 1), (1, 2), (2, 3), (4, 2), (5, 4)
        ];
        let k = 3;
        let result = partition(servers, edges, microservices, dependencies, k);
        assert!(result.is_some());
        let clusters = result.unwrap();
        assert_eq!(clusters.len(), k);
        // Ensure that all microservices are assigned exactly once.
        let mut assigned: Vec<usize> = clusters.iter().flatten().cloned().collect();
        assigned.sort_unstable();
        assert_eq!(assigned, vec![0, 1, 2, 3, 4, 5]);
    }
}

#[cfg(test)]
mod extra_tests {
    // Additional tests can be placed here if needed.
    #[test]
    fn dummy() {
        assert_eq!(2 + 2, 4);
    }
}