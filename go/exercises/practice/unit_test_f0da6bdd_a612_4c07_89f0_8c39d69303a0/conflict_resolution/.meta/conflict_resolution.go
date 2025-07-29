package conflictresolution

// ResolveConflicts analyzes transaction logs and resolves conflicts
func ResolveConflicts(transactions []Transaction, numNodes int) map[int]map[string]string {
    // Initialize result map for all nodes
    result := make(map[int]map[string]string)
    for i := 0; i < numNodes; i++ {
        result[i] = make(map[string]string)
    }

    // Create a map to track conflicts per node and key
    conflicts := make(map[int]map[string][]transactionOperation)
    
    // Sort operations by transaction ID to ensure deterministic conflict resolution
    sortedOps := buildSortedOperations(transactions)

    // Process all operations
    for _, op := range sortedOps {
        nodeConflicts, exists := conflicts[op.operation.NodeID]
        if !exists {
            nodeConflicts = make(map[string][]transactionOperation)
            conflicts[op.operation.NodeID] = nodeConflicts
        }

        // Skip read operations as they don't cause conflicts
        if op.operation.OpType == "READ" {
            continue
        }

        // Check for conflicts
        if existingOps, hasKey := nodeConflicts[op.operation.Key]; hasKey {
            // Check if there's a write conflict
            hasConflict := false
            for _, existing := range existingOps {
                if existing.operation.OpType == "WRITE" {
                    hasConflict = true
                    break
                }
            }

            if hasConflict {
                // If current transaction has higher ID, skip it (conflict resolution)
                shouldSkip := false
                for _, existing := range existingOps {
                    if existing.transactionID < op.transactionID {
                        shouldSkip = true
                        break
                    }
                }
                if shouldSkip {
                    continue
                }
                // If current transaction has lower ID, remove conflicting operations
                nodeConflicts[op.operation.Key] = []transactionOperation{op}
            } else {
                // No write conflict, append operation
                nodeConflicts[op.operation.Key] = append(existingOps, op)
            }
        } else {
            // No conflicts yet for this key
            nodeConflicts[op.operation.Key] = []transactionOperation{op}
        }

        // Update the result map with the new value
        result[op.operation.NodeID][op.operation.Key] = op.operation.Value
    }

    return result
}

// transactionOperation pairs an operation with its transaction ID
type transactionOperation struct {
    transactionID int
    operation     Operation
}

// buildSortedOperations creates a sorted slice of operations with their transaction IDs
func buildSortedOperations(transactions []Transaction) []transactionOperation {
    var operations []transactionOperation
    
    // Collect all operations with their transaction IDs
    for _, tx := range transactions {
        for _, op := range tx.Operations {
            operations = append(operations, transactionOperation{
                transactionID: tx.ID,
                operation:     op,
            })
        }
    }

    // Sort operations by transaction ID (bubble sort for simplicity)
    for i := 0; i < len(operations)-1; i++ {
        for j := 0; j < len(operations)-i-1; j++ {
            if operations[j].transactionID > operations[j+1].transactionID {
                operations[j], operations[j+1] = operations[j+1], operations[j]
            }
        }
    }

    return operations
}