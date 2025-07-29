package kclique

import (
    "sort"
)

// EnumKCliques finds all k-cliques in the given graph
func EnumKCliques(n, k int, adjList map[int][]int) [][]int {
    // Input validation
    if n < 1 || k < 1 || k > n {
        panic("Invalid input parameters")
    }

    // Convert adjacency lists to a more efficient representation
    // using a 2D boolean matrix for constant-time lookups
    adjMatrix := make([][]bool, n)
    for i := range adjMatrix {
        adjMatrix[i] = make([]bool, n)
    }
    for v, neighbors := range adjList {
        for _, u := range neighbors {
            adjMatrix[v][u] = true
            adjMatrix[u][v] = true
        }
    }

    result := make([][]int, 0)
    current := make([]int, 0, k)
    candidates := make([]int, n)
    for i := range candidates {
        candidates[i] = i
    }

    // Helper function to check if a vertex can be added to the current clique
    isConnectedToAll := func(vertex int, clique []int) bool {
        for _, v := range clique {
            if !adjMatrix[vertex][v] {
                return false
            }
        }
        return true
    }

    // Recursive function to find k-cliques
    var findCliques func(start int, remaining []int)
    findCliques = func(start int, remaining []int) {
        if len(current) == k {
            // Found a k-clique, make a copy and add it to results
            clique := make([]int, k)
            copy(clique, current)
            result = append(result, clique)
            return
        }

        // For each remaining vertex
        for i := start; i < len(remaining); i++ {
            v := remaining[i]
            
            // Check if this vertex can form a clique with current vertices
            if !isConnectedToAll(v, current) {
                continue
            }

            // Add vertex to current clique
            current = append(current, v)
            
            // Recursively find cliques with remaining vertices
            findCliques(i+1, remaining)
            
            // Backtrack
            current = current[:len(current)-1]
        }
    }

    // Start the recursive search
    findCliques(0, candidates)

    // Sort results lexicographically
    for _, clique := range result {
        sort.Ints(clique)
    }
    sort.Slice(result, func(i, j int) bool {
        for k := 0; k < len(result[i]) && k < len(result[j]); k++ {
            if result[i][k] != result[j][k] {
                return result[i][k] < result[j][k]
            }
        }
        return len(result[i]) < len(result[j])
    })

    return result
}