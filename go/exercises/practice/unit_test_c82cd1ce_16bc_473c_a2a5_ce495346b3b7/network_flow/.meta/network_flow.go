package networkflow

// MaximumSatisfiedRequests returns the maximum number of requests that can be satisfied
func MaximumSatisfiedRequests(n int, capacities [][]int, nodeCapacities []int, requests [][]int) int {
    // Create residual graph with additional source and sink nodes
    nodes := n + 2
    source := n      // Second last node
    sink := n + 1   // Last node
    
    // Initialize residual graph
    residual := make([][]int, nodes)
    for i := range residual {
        residual[i] = make([]int, nodes)
    }
    
    // Store original node capacities for reset between attempts
    originalNodeCap := make([]int, n)
    copy(originalNodeCap, nodeCapacities)
    
    // Try satisfying different numbers of requests
    left, right := 0, len(requests)
    maxSatisfied := 0
    
    // Binary search on the number of requests to satisfy
    for left <= right {
        mid := (left + right) / 2
        
        // Check if we can satisfy 'mid' number of requests
        if canSatisfyRequests(mid, requests, capacities, originalNodeCap, residual, n, source, sink) {
            maxSatisfied = mid
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    
    return maxSatisfied
}

// canSatisfyRequests checks if it's possible to satisfy the given number of requests
func canSatisfyRequests(numRequests int, requests [][]int, capacities [][]int, nodeCapacities []int, residual [][]int, n, source, sink int) bool {
    // Reset residual graph
    for i := range residual {
        for j := range residual[i] {
            residual[i][j] = 0
        }
    }
    
    // Reset node capacities
    nodeCap := make([]int, len(nodeCapacities))
    copy(nodeCap, nodeCapacities)
    
    // Build residual graph for the first numRequests requests
    for i := 0; i < numRequests && i < len(requests); i++ {
        src, dst, flow := requests[i][0], requests[i][1], requests[i][2]
        residual[source][src] += flow
        residual[dst][sink] += flow
        
        // Add edges between nodes based on capacities
        for j := 0; j < n; j++ {
            for k := 0; k < n; k++ {
                if capacities[j][k] > 0 {
                    residual[j][k] = capacities[j][k]
                }
            }
        }
    }
    
    // Try to find maximum flow using Ford-Fulkerson with DFS
    maxFlow := 0
    for {
        visited := make([]bool, len(residual))
        pathFlow := dfs(source, sink, residual, visited, nodeCap, []int{int(^uint(0) >> 1)})
        if pathFlow == 0 {
            break
        }
        maxFlow += pathFlow
    }
    
    // Calculate total required flow
    requiredFlow := 0
    for i := 0; i < numRequests && i < len(requests); i++ {
        requiredFlow += requests[i][2]
    }
    
    return maxFlow >= requiredFlow
}

// dfs implements depth-first search for finding augmenting paths
func dfs(curr, sink int, residual [][]int, visited []bool, nodeCap []int, minFlow []int) int {
    if curr == sink {
        return minFlow[0]
    }
    
    visited[curr] = true
    
    for next := 0; next < len(residual); next++ {
        if !visited[next] && residual[curr][next] > 0 {
            // Consider node capacity constraints
            if curr < len(nodeCap) {
                minFlow[0] = min(minFlow[0], nodeCap[curr])
            }
            minFlow[0] = min(minFlow[0], residual[curr][next])
            
            flow := dfs(next, sink, residual, visited, nodeCap, minFlow)
            if flow > 0 {
                residual[curr][next] -= flow
                residual[next][curr] += flow
                if curr < len(nodeCap) {
                    nodeCap[curr] -= flow
                }
                return flow
            }
        }
    }
    
    return 0
}

func min(a, b int) int {
    if a < b {
        return a
    }
    return b
}