use std::str::FromStr;

#[derive(Clone)]
struct Edge {
    u: usize,
    v: usize,
    cost: i64,
    potential: bool,
}

struct UnionFind {
    parent: Vec<usize>,
    rank: Vec<usize>,
}

impl UnionFind {
    fn new(n: usize) -> Self {
        UnionFind {
            parent: (0..n).collect(),
            rank: vec![0; n],
        }
    }

    fn find(&mut self, u: usize) -> usize {
        if self.parent[u] != u {
            self.parent[u] = self.find(self.parent[u]);
        }
        self.parent[u]
    }

    fn union(&mut self, u: usize, v: usize) -> bool {
        let mut u_root = self.find(u);
        let mut v_root = self.find(v);
        if u_root == v_root {
            return false;
        }
        if self.rank[u_root] < self.rank[v_root] {
            std::mem::swap(&mut u_root, &mut v_root);
        }
        self.parent[v_root] = u_root;
        if self.rank[u_root] == self.rank[v_root] {
            self.rank[u_root] += 1;
        }
        true
    }
}

// Compute MST with modified costs: for potential edges, weight = cost + lambda; for existing, weight = cost.
// Returns Some((total_modified_cost, count_of_potential_edges_used)) if MST spans all nodes, otherwise None.
fn mst_with_penalty(n: usize, edges: &Vec<Edge>, lambda: i64) -> Option<(i64, usize)> {
    let mut sorted_edges = edges.clone();
    sorted_edges.sort_by(|a, b| {
        let weight_a = if a.potential { a.cost + lambda } else { a.cost };
        let weight_b = if b.potential { b.cost + lambda } else { b.cost };
        weight_a.cmp(&weight_b)
    });
    let mut uf = UnionFind::new(n);
    let mut total_cost = 0;
    let mut potential_count = 0;
    let mut edges_used = 0;
    for edge in sorted_edges.iter() {
        if uf.union(edge.u, edge.v) {
            let weight = if edge.potential { edge.cost + lambda } else { edge.cost };
            total_cost += weight;
            if edge.potential {
                potential_count += 1;
            }
            edges_used += 1;
            if edges_used == n - 1 {
                break;
            }
        }
    }
    if edges_used == n - 1 {
        Some((total_cost, potential_count))
    } else {
        None
    }
}

fn parse_line<T: FromStr>(s: &str) -> Vec<T> {
    s.split_whitespace().filter_map(|word| word.parse::<T>().ok()).collect()
}

pub fn solve(input: &str) -> i64 {
    let mut lines = input.lines();
    // First line: N M K
    let first_line = lines.next();
    if first_line.is_none() {
        return -1;
    }
    let nums: Vec<usize> = parse_line(first_line.unwrap());
    if nums.len() < 3 {
        return -1;
    }
    let n = nums[0];
    let m = nums[1];
    let k = nums[2];

    let mut edges: Vec<Edge> = Vec::new();
    // Parse M existing roads.
    for _ in 0..m {
        if let Some(line) = lines.next() {
            let parts: Vec<i64> = parse_line(line);
            if parts.len() < 3 {
                return -1;
            }
            let u = (parts[0] - 1) as usize;
            let v = (parts[1] - 1) as usize;
            let cost = parts[2];
            edges.push(Edge { u, v, cost, potential: false });
        } else {
            return -1;
        }
    }
    // Next line: number of potential highways available, L.
    let potential_count_line = lines.next();
    if potential_count_line.is_none() {
        return -1;
    }
    let potential_count_vec: Vec<usize> = parse_line(potential_count_line.unwrap());
    if potential_count_vec.is_empty() {
        return -1;
    }
    let l = potential_count_vec[0];
    for _ in 0..l {
        if let Some(line) = lines.next() {
            let parts: Vec<i64> = parse_line(line);
            if parts.len() < 3 {
                return -1;
            }
            let u = (parts[0] - 1) as usize;
            let v = (parts[1] - 1) as usize;
            let cost = parts[2];
            edges.push(Edge { u, v, cost, potential: true });
        } else {
            return -1;
        }
    }
    // Check connectivity possibility: try MST with lambda=0.
    if let None = mst_with_penalty(n, &edges, 0) {
        return -1;
    }

    // Binary search over lambda to enforce potential highways usage constraint.
    let mut lo = 0;
    let mut hi = 1_000_000 + 1; // upper bound for lambda
    let mut best_lambda = hi;
    while lo < hi {
        let mid = (lo + hi) / 2;
        if let Some((_, used)) = mst_with_penalty(n, &edges, mid) {
            if used <= k {
                best_lambda = mid;
                hi = mid;
            } else {
                lo = mid + 1;
            }
        } else {
            // Should not happen because connectivity was confirmed.
            lo = mid + 1;
        }
    }
    // Compute final MST with best_lambda.
    if let Some((modified_cost, used)) = mst_with_penalty(n, &edges, best_lambda) {
        // Adjust back the cost: subtract lambda penalty for each potential edge used.
        let original_cost = modified_cost - best_lambda * (used as i64);
        original_cost
    } else {
        -1
    }
}