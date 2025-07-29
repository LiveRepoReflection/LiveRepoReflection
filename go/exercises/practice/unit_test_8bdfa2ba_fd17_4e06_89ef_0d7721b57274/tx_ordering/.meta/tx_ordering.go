package tx_ordering

import (
	"sort"
)

// Transaction represents a financial transaction in the DeFi network.
type Transaction struct {
	ID        string   // Unique transaction ID (UUID).
	Submitter string   // Public key of the transaction submitter.
	Data      []byte   // Arbitrary transaction data.
	Timestamp int64    // Nanosecond-precision timestamp of when the transaction was first seen by *any* node.
	Priority  uint64   // Explicit priority for transaction ordering. Lower values mean higher priority.
	Conflicts []string // A list of transaction IDs that conflict with this transaction.
}

// OrderTransactions takes a slice of transactions and returns a new slice with
// transactions ordered according to the specified rules.
func OrderTransactions(transactions []Transaction) []Transaction {
	// Handle empty input
	if len(transactions) == 0 {
		return []Transaction{}
	}

	// Create a copy to avoid modifying the original slice
	result := make([]Transaction, len(transactions))
	copy(result, transactions)

	// First sort step: Sort by timestamp, then priority, then ID
	sort.SliceStable(result, func(i, j int) bool {
		// First criterion: Timestamp (older first)
		if result[i].Timestamp != result[j].Timestamp {
			return result[i].Timestamp < result[j].Timestamp
		}

		// Second criterion: Priority (lower value first)
		if result[i].Priority != result[j].Priority {
			return result[i].Priority < result[j].Priority
		}

		// Third criterion: ID (lexicographically smaller first)
		return result[i].ID < result[j].ID
	})

	// Second step: Process transactions with same timestamp and priority to handle conflicts
	// This is needed because conflicts can create complex relationships that simple sorting can't handle
	return resolveConflicts(result)
}

// resolveConflicts ensures all conflict relationships are respected while maintaining
// the overall ordering based on timestamp and priority.
func resolveConflicts(txs []Transaction) []Transaction {
	if len(txs) <= 1 {
		return txs
	}

	// Group transactions by timestamp and priority
	groups := groupTransactionsByTimestampAndPriority(txs)

	// Process each group to resolve conflicts
	result := make([]Transaction, 0, len(txs))
	for _, group := range groups {
		// If the group has only one transaction or no conflicts, just add it to the result
		if len(group) <= 1 {
			result = append(result, group...)
			continue
		}

		// Build a conflict graph for this group
		conflictGraph := buildConflictGraph(group)

		// Sort the group respecting conflicts
		sortedGroup := topologicalSort(group, conflictGraph)
		
		// Append the sorted group to the result
		result = append(result, sortedGroup...)
	}

	return result
}

// groupTransactionsByTimestampAndPriority groups transactions by timestamp and priority
func groupTransactionsByTimestampAndPriority(txs []Transaction) [][]Transaction {
	if len(txs) == 0 {
		return [][]Transaction{}
	}

	var groups [][]Transaction
	currentGroup := []Transaction{txs[0]}
	currentTimestamp := txs[0].Timestamp
	currentPriority := txs[0].Priority

	for i := 1; i < len(txs); i++ {
		if txs[i].Timestamp == currentTimestamp && txs[i].Priority == currentPriority {
			// Add to current group
			currentGroup = append(currentGroup, txs[i])
		} else {
			// Start a new group
			groups = append(groups, currentGroup)
			currentGroup = []Transaction{txs[i]}
			currentTimestamp = txs[i].Timestamp
			currentPriority = txs[i].Priority
		}
	}
	
	// Add the last group
	if len(currentGroup) > 0 {
		groups = append(groups, currentGroup)
	}

	return groups
}

// buildConflictGraph creates a directed graph representing conflicts between transactions
func buildConflictGraph(txs []Transaction) map[string][]string {
	// Map transaction IDs to their index in the txs slice for quick lookup
	idToIndex := make(map[string]int)
	for i, tx := range txs {
		idToIndex[tx.ID] = i
	}

	// Build the conflict graph as an adjacency list
	graph := make(map[string][]string)
	for _, tx := range txs {
		// Initialize the node in the graph if it doesn't exist
		if _, exists := graph[tx.ID]; !exists {
			graph[tx.ID] = []string{}
		}

		// Add edges for conflicts
		for _, conflictID := range tx.Conflicts {
			// Check if the conflict is in our current group
			if conflictIdx, exists := idToIndex[conflictID]; exists {
				// Add an edge from tx.ID to conflictID in the directed graph
				// This means tx.ID should come after conflictID
				conflictTx := txs[conflictIdx]
				
				// If both transactions conflict with each other, use lexicographic ordering
				if containsString(conflictTx.Conflicts, tx.ID) {
					if tx.ID < conflictID {
						graph[conflictID] = append(graph[conflictID], tx.ID)
					} else {
						graph[tx.ID] = append(graph[tx.ID], conflictID)
					}
				} else {
					// One-way conflict: tx conflicts with conflictTx
					graph[tx.ID] = append(graph[tx.ID], conflictID)
				}
			}
		}
	}

	return graph
}

// containsString checks if a string slice contains a specific string
func containsString(slice []string, str string) bool {
	for _, item := range slice {
		if item == str {
			return true
		}
	}
	return false
}

// topologicalSort performs a topological sort on the conflict graph
// It uses depth-first search and handles potential cycles by falling back to lexicographical ordering
func topologicalSort(txs []Transaction, graph map[string][]string) []Transaction {
	// If we have no conflicts, just sort lexicographically and return
	if len(graph) == 0 {
		sort.Slice(txs, func(i, j int) bool {
			return txs[i].ID < txs[j].ID
		})
		return txs
	}

	// Create a map for quick transaction lookup
	txMap := make(map[string]Transaction)
	for _, tx := range txs {
		txMap[tx.ID] = tx
	}

	// Track visited nodes and completed nodes
	visited := make(map[string]bool)
	temp := make(map[string]bool)  // For cycle detection
	ordered := make([]string, 0)   // The topologically sorted order of transaction IDs

	// Depth-first search function
	var dfs func(node string) bool
	dfs = func(node string) bool {
		if temp[node] {
			// Cycle detected, handle this case specially
			return false
		}
		if visited[node] {
			return true
		}
		
		// Mark as temporarily visited
		temp[node] = true
		
		// Visit all neighbors
		for _, neighbor := range graph[node] {
			if !dfs(neighbor) {
				// Cycle detected, resolve by comparing IDs
				if node < neighbor {
					// Add node first, then neighbor to the ordered list later
					return true
				} else {
					// Skip this edge and continue with other neighbors
					continue
				}
			}
		}
		
		// Mark as permanently visited
		visited[node] = true
		temp[node] = false
		
		// Add to ordered list
		ordered = append(ordered, node)
		return true
	}

	// Run DFS on all nodes
	for id := range txMap {
		if !visited[id] {
			dfs(id)
		}
	}

	// Reverse ordered to get correct topological ordering
	for i, j := 0, len(ordered)-1; i < j; i, j = i+1, j-1 {
		ordered[i], ordered[j] = ordered[j], ordered[i]
	}

	// Convert the ordered IDs back to transactions
	result := make([]Transaction, 0, len(ordered))
	for _, id := range ordered {
		result = append(result, txMap[id])
	}

	// Add any transactions that weren't in the graph (no conflicts)
	for _, tx := range txs {
		if !visited[tx.ID] {
			result = append(result, tx)
		}
	}

	// Ensure deterministic ordering by finally sorting any remaining transactions lexicographically
	// This helps with transactions that might have been missed in the graph
	sort.Slice(result, func(i, j int) bool {
		return result[i].ID < result[j].ID
	})

	return result
}