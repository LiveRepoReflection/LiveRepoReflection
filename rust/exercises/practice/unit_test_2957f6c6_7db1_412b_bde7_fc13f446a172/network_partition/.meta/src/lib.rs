pub fn min_resilience_loss(n: usize, k: usize, edges: Vec<(usize, usize, usize)>) -> i32 {
    // Calculate the total resilience sum of all edges.
    let total_sum: usize = edges.iter().map(|&(_, _, w)| w).sum();

    // Initialize DSU to build the maximum spanning forest.
    let mut dsu = DSU::new(n);

    // Sort edges in descending order by weight.
    let mut sorted_edges = edges.clone();
    sorted_edges.sort_by(|a, b| b.2.cmp(&a.2));

    let mut forest_edges = Vec::new();
    for (u, v, w) in sorted_edges {
        if dsu.find(u) != dsu.find(v) {
            dsu.union(u, v);
            forest_edges.push(w);
        }
    }

    // Number of connected components in the maximum spanning forest.
    let comp_count = dsu.components();
    // If the desired number of partitions is less than the number of existing connected components,
    // it is impossible because removal cannot merge disconnected components.
    if k < comp_count {
        return -1;
    }

    // To achieve exactly k components, we need to further remove (k - comp_count) edges
    // from the maximum spanning forest.
    let removals_needed = k - comp_count;

    // Sort the edges in the forest in ascending order.
    forest_edges.sort();

    // Sum of weights of the edges to remove (choose the smallest ones to minimize loss).
    let mut removed_sum = 0;
    for i in 0..removals_needed {
        // In a maximum spanning forest, the number of edges is exactly n - comp_count,
        // and removals_needed is always <= n - comp_count.
        removed_sum += forest_edges[i];
    }

    let forest_sum: usize = forest_edges.iter().sum();
    // The total kept sum is the forest's total minus the sum of the removed edges.
    let kept_sum = forest_sum - removed_sum;
    
    // The minimal resilience loss is the total resilience value of all edges minus
    // the kept resilience in the final forest partition.
    (total_sum - kept_sum) as i32
}

struct DSU {
    parent: Vec<usize>,
    rank: Vec<usize>,
    count: usize,
}

impl DSU {
    fn new(n: usize) -> Self {
        let parent = (0..n).collect();
        let rank = vec![0; n];
        DSU { parent, rank, count: n }
    }

    fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            self.parent[x] = self.find(self.parent[x]);
        }
        self.parent[x]
    }

    fn union(&mut self, x: usize, y: usize) {
        let mut x_root = self.find(x);
        let mut y_root = self.find(y);
        if x_root == y_root {
            return;
        }
        if self.rank[x_root] < self.rank[y_root] {
            self.parent[x_root] = y_root;
        } else if self.rank[x_root] > self.rank[y_root] {
            self.parent[y_root] = x_root;
        } else {
            self.parent[y_root] = x_root;
            self.rank[x_root] += 1;
        }
        self.count -= 1;
    }

    fn components(&self) -> usize {
        self.count
    }
}