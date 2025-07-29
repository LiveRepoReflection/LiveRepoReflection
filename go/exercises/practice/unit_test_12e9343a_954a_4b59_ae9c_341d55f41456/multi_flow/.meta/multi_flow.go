package multiflow

// MaxMultiFlow calculates the maximum flow for multiple commodities in a network
func MaxMultiFlow(n int, edges [][3]int, commodities [][3]int) []int {
    // Create result array for each commodity
    flows := make([]int, len(commodities))
    
    // Create residual graph capacity matrix
    residual := make([][]int, n)
    for i := range residual {
        residual[i] = make([]int, n)
    }
    
    // Initialize residual graph with edge capacities
    for _, edge := range edges {
        residual[edge[0]][edge[1]] = edge[2]
    }
    
    // Process each commodity independently
    for i, commodity := range commodities {
        source := commodity[0]
        sink := commodity[1]
        demand := commodity[2]
        
        // Create a temporary residual graph for this commodity
        tempResidual := make([][]int, n)
        for j := range tempResidual {
            tempResidual[j] = make([]int, n)
            copy(tempResidual[j], residual[j])
        }
        
        flows[i] = findMaxFlow(n, tempResidual, source, sink, demand)
        
        // Update the main residual graph with the flow used by this commodity
        for j := 0; j < n; j++ {
            for k := 0; k < n; k++ {
                residual[j][k] = tempResidual[j][k]
            }
        }
    }
    
    return flows
}

// findMaxFlow implements the Edmonds-Karp algorithm to find the maximum flow
func findMaxFlow(n int, residual [][]int, source, sink, demand int) int {
    totalFlow := 0
    
    for {
        // Find augmenting path using BFS
        parent := make([]int, n)
        for i := range parent {
            parent[i] = -1
        }
        
        // BFS queue
        queue := []int{source}
        parent[source] = source
        
        for len(queue) > 0 && parent[sink] == -1 {
            current := queue[0]
            queue = queue[1:]
            
            for next := 0; next < n; next++ {
                if parent[next] == -1 && residual[current][next] > 0 {
                    parent[next] = current
                    queue = append(queue, next)
                }
            }
        }
        
        // If no augmenting path is found, break
        if parent[sink] == -1 {
            break
        }
        
        // Find minimum residual capacity along the path
        pathFlow := demand - totalFlow
        current := sink
        for current != source {
            prev := parent[current]
            if residual[prev][current] < pathFlow {
                pathFlow = residual[prev][current]
            }
            current = prev
        }
        
        // Update residual capacities
        current = sink
        for current != source {
            prev := parent[current]
            residual[prev][current] -= pathFlow
            residual[current][prev] += pathFlow
            current = prev
        }
        
        totalFlow += pathFlow
        
        // If we've met the demand, break
        if totalFlow >= demand {
            return demand
        }
    }
    
    return totalFlow
}