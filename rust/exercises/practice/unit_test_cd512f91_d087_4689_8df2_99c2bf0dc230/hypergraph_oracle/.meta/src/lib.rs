/// A data structure for efficiently answering connectivity queries on a hypergraph
/// using a Union-Find (Disjoint Set) implementation with path compression and union by rank.
///
/// This implementation has the following complexities:
/// - Construction: O(n)
/// - add_hyperedge: Amortized O(α(n)) per vertex in the hyperedge, where α is the inverse Ackermann function
/// - are_connected: O(α(n)) where α is the inverse Ackermann function (nearly constant time in practice)
pub struct HypergraphConnectivityOracle {
    // Number of vertices in the hypergraph
    n: usize,
    // Parent array for the disjoint-set data structure
    parent: Vec<usize>,
    // Rank array for union by rank optimization
    rank: Vec<usize>,
}

impl HypergraphConnectivityOracle {
    /// Creates a new HypergraphConnectivityOracle with n vertices and no hyperedges.
    ///
    /// Each vertex is initially in its own connected component.
    ///
    /// Time complexity: O(n)
    pub fn new(n: usize) -> Self {
        // Initialize each vertex to be its own parent (n disjoint sets)
        let mut parent = Vec::with_capacity(n + 1);
        let mut rank = Vec::with_capacity(n + 1);
        
        // We use 1-indexed vertices, so we add a dummy element at index 0
        parent.push(0);
        rank.push(0);
        
        for i in 1..=n {
            parent.push(i);
            rank.push(0);
        }
        
        HypergraphConnectivityOracle {
            n,
            parent,
            rank,
        }
    }
    
    /// Finds the representative (root) of the set containing vertex x.
    ///
    /// Uses path compression to optimize future queries.
    ///
    /// Time complexity: Amortized O(α(n)), where α is the inverse Ackermann function
    /// (effectively constant time for all practical purposes)
    fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            // Path compression: Make every visited node point directly to the root
            self.parent[x] = self.find(self.parent[x]);
        }
        self.parent[x]
    }
    
    /// Performs a non-mutating find operation for cases where we don't want to change
    /// the data structure (used in are_connected).
    fn find_non_mut(&self, mut x: usize) -> usize {
        while self.parent[x] != x {
            x = self.parent[x];
        }
        x
    }
    
    /// Merges the sets containing vertices x and y.
    ///
    /// Uses union by rank to keep the tree balanced.
    ///
    /// Time complexity: O(α(n)) amortized
    fn union(&mut self, x: usize, y: usize) {
        let root_x = self.find(x);
        let root_y = self.find(y);
        
        if root_x == root_y {
            return; // Already in the same set
        }
        
        // Union by rank: attach smaller rank tree under root of higher rank tree
        if self.rank[root_x] < self.rank[root_y] {
            self.parent[root_x] = root_y;
        } else if self.rank[root_x] > self.rank[root_y] {
            self.parent[root_y] = root_x;
        } else {
            // If ranks are the same, make one the root and increment its rank
            self.parent[root_y] = root_x;
            self.rank[root_x] += 1;
        }
    }
    
    /// Adds a new hyperedge to the hypergraph.
    ///
    /// A hyperedge connects all vertices it contains, making them part of the same
    /// connected component.
    ///
    /// Time complexity: O(|vertices| * α(n)) amortized, where |vertices| is the size of the hyperedge
    pub fn add_hyperedge(&mut self, vertices: Vec<usize>) {
        if vertices.is_empty() {
            return; // Empty hyperedge doesn't connect anything
        }
        
        // To add a hyperedge, we simply need to union all vertices it contains
        // We use the first vertex as a representative to union with all others
        let first = vertices[0];
        
        for &v in vertices.iter().skip(1) {
            self.union(first, v);
        }
    }
    
    /// Checks if vertices u and v are connected in the hypergraph.
    ///
    /// Two vertices are connected if they belong to the same connected component.
    ///
    /// Time complexity: O(α(n)) amortized, effectively constant time
    pub fn are_connected(&self, u: usize, v: usize) -> bool {
        // Vertices are connected if they are in the same set
        // We use find_non_mut to avoid modifying the data structure during a query
        self.find_non_mut(u) == self.find_non_mut(v)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_example() {
        let mut oracle = HypergraphConnectivityOracle::new(5);
        
        oracle.add_hyperedge(vec![1, 2, 3]);
        oracle.add_hyperedge(vec![3, 4]);
        
        assert!(oracle.are_connected(1, 4));
        assert!(!oracle.are_connected(1, 5));
        
        oracle.add_hyperedge(vec![5]);
        assert!(!oracle.are_connected(1, 5));
        
        oracle.add_hyperedge(vec![2, 5]);
        assert!(oracle.are_connected(1, 5));
    }

    #[test]
    fn test_disjoint_components() {
        let mut oracle = HypergraphConnectivityOracle::new(10);
        
        oracle.add_hyperedge(vec![1, 2, 3]);
        oracle.add_hyperedge(vec![5, 6, 7]);
        
        assert!(oracle.are_connected(1, 3));
        assert!(oracle.are_connected(5, 7));
        assert!(!oracle.are_connected(1, 5));
        assert!(!oracle.are_connected(3, 6));
        assert!(!oracle.are_connected(2, 7));
        
        // Connect the two components
        oracle.add_hyperedge(vec![3, 5]);
        
        assert!(oracle.are_connected(1, 7));
        assert!(oracle.are_connected(2, 6));
    }

    #[test]
    fn test_reflexivity() {
        let oracle = HypergraphConnectivityOracle::new(5);
        
        // A vertex is always connected to itself
        for i in 1..=5 {
            assert!(oracle.are_connected(i, i));
        }
    }

    #[test]
    fn test_edge_cases() {
        let mut oracle = HypergraphConnectivityOracle::new(3);
        
        // Empty hyperedge should have no effect
        oracle.add_hyperedge(vec![]);
        assert!(!oracle.are_connected(1, 2));
        
        // Hyperedge with a single vertex
        oracle.add_hyperedge(vec![1]);
        assert!(!oracle.are_connected(1, 2));
        
        // Normal hyperedge
        oracle.add_hyperedge(vec![1, 2, 3]);
        assert!(oracle.are_connected(1, 3));
    }
}