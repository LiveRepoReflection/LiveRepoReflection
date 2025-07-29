package kth_ancestor

import (
	"testing"
)

func TestKthAncestorExample(t *testing.T) {
	// Tree structure:
	//       0
	//     /   \
	//    1     2
	//   / \   / \
	//  3   4 5   6
	n := 7
	parents := []int{-1, 0, 0, 1, 1, 2, 2}
	kt := Constructor(n, parents)
	
	tests := []struct {
		node     int
		k        int
		expected int
	}{
		{node: 3, k: 1, expected: 1},  // 1 is direct parent of 3
		{node: 5, k: 2, expected: 0},  // 0 is 2nd ancestor of 5 (5->2->0)
		{node: 6, k: 3, expected: -1}, // ancestor exceeds root
		{node: 0, k: 1, expected: -1}, // root node has no ancestor
	}
	for _, tc := range tests {
		if res := kt.GetKthAncestor(tc.node, tc.k); res != tc.expected {
			t.Errorf("GetKthAncestor(%d, %d) = %d; expected %d", tc.node, tc.k, res, tc.expected)
		}
	}
}

func TestKthAncestorChain(t *testing.T) {
	// Tree structure is a chain: 0 -> 1 -> 2 -> 3 -> 4
	n := 5
	parents := []int{-1, 0, 1, 2, 3}
	kt := Constructor(n, parents)
	
	tests := []struct {
		node     int
		k        int
		expected int
	}{
		{node: 4, k: 1, expected: 3},
		{node: 4, k: 2, expected: 2},
		{node: 4, k: 4, expected: 0},
		{node: 4, k: 5, expected: -1},
		{node: 2, k: 0, expected: 2}, // if k==0, returns the node itself (if implementation supports)
	}
	for _, tc := range tests {
		if res := kt.GetKthAncestor(tc.node, tc.k); res != tc.expected {
			t.Errorf("Chain Test: GetKthAncestor(%d, %d) = %d; expected %d", tc.node, tc.k, res, tc.expected)
		}
	}
}

func TestKthAncestorSingleNode(t *testing.T) {
	// Tree with single node only.
	n := 1
	parents := []int{-1}
	kt := Constructor(n, parents)
	
	if res := kt.GetKthAncestor(0, 1); res != -1 {
		t.Errorf("Single Node Test: GetKthAncestor(0, 1) = %d; expected -1", res)
	}
}

func TestKthAncestorBranching(t *testing.T) {
	// Create a balanced tree with additional branches.
	// Tree structure:
	//          0
	//       /     \
	//      1       2
	//     / \     / \
	//    3   4   5   6
	//   / \
	//  7   8
	n := 9
	parents := []int{-1, 0, 0, 1, 1, 2, 2, 3, 3}
	kt := Constructor(n, parents)
	
	tests := []struct {
		node     int
		k        int
		expected int
	}{
		{node: 4, k: 1, expected: 1},
		{node: 4, k: 2, expected: 0},
		{node: 7, k: 1, expected: 3},
		{node: 7, k: 2, expected: 1},
		{node: 7, k: 3, expected: 0},
		{node: 7, k: 4, expected: -1},
		{node: 6, k: 1, expected: 2},
		{node: 6, k: 2, expected: 0},
	}
	for _, tc := range tests {
		if res := kt.GetKthAncestor(tc.node, tc.k); res != tc.expected {
			t.Errorf("Branching Test: GetKthAncestor(%d, %d) = %d; expected %d", tc.node, tc.k, res, tc.expected)
		}
	}
}