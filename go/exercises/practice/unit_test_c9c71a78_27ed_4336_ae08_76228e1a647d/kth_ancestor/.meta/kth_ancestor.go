package kth_ancestor

// KthAncestor is a data structure to efficiently compute k-th ancestors in a tree using binary lifting.
type KthAncestor struct {
	dp   [][]int // dp[node][j] stores the 2^j-th ancestor of node
	maxJ int     // maximum power of two used
}

// Constructor initializes the KthAncestor structure.
// n is the number of nodes, and parents is a slice where parents[i] is the parent of node i.
func Constructor(n int, parents []int) KthAncestor {
	// Compute maximum power needed such that 2^maxJ >= n.
	maxJ := 0
	for (1 << uint(maxJ)) <= n {
		maxJ++
	}

	// Initialize dp table with dimensions n x maxJ.
	dp := make([][]int, n)
	for i := 0; i < n; i++ {
		dp[i] = make([]int, maxJ)
	}

	// The first ancestor (2^0-th) is the direct parent.
	for i := 0; i < n; i++ {
		dp[i][0] = parents[i]
	}

	// Precompute the 2^j-th ancestor for each node.
	for j := 1; j < maxJ; j++ {
		for i := 0; i < n; i++ {
			prev := dp[i][j-1]
			if prev == -1 {
				dp[i][j] = -1
			} else {
				dp[i][j] = dp[prev][j-1]
			}
		}
	}

	return KthAncestor{
		dp:   dp,
		maxJ: maxJ,
	}
}

// GetKthAncestor returns the k-th ancestor of the given node.
// If the k-th ancestor does not exist, it returns -1.
func (ka *KthAncestor) GetKthAncestor(node int, k int) int {
	for j := 0; j < ka.maxJ && node != -1; j++ {
		// Check if the j-th bit in k is set.
		if (k >> uint(j)) & 1 == 1 {
			node = ka.dp[node][j]
		}
	}
	return node
}