package kclique

import (
    "reflect"
    "sort"
    "testing"
)

func TestEnumKCliques(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            result := EnumKCliques(tc.n, tc.k, tc.adjList)
            
            // Sort each clique and the entire result for comparison
            for i := range result {
                sort.Ints(result[i])
            }
            sort.Slice(result, func(i, j int) bool {
                for k := 0; k < len(result[i]) && k < len(result[j]); k++ {
                    if result[i][k] != result[j][k] {
                        return result[i][k] < result[j][k]
                    }
                }
                return len(result[i]) < len(result[j])
            })

            if !reflect.DeepEqual(result, tc.expected) {
                t.Errorf("EnumKCliques(%d, %d, %v) = %v, want %v",
                    tc.n, tc.k, tc.adjList, result, tc.expected)
            }
        })
    }
}

// Test invalid inputs
func TestInvalidInputs(t *testing.T) {
    invalidTests := []struct {
        description string
        n           int
        k           int
        adjList     map[int][]int
    }{
        {
            description: "k greater than n",
            n:          3,
            k:          4,
            adjList: map[int][]int{
                0: {1, 2},
                1: {0, 2},
                2: {0, 1},
            },
        },
        {
            description: "negative n",
            n:          -1,
            k:          2,
            adjList:    map[int][]int{},
        },
        {
            description: "negative k",
            n:          3,
            k:          -1,
            adjList: map[int][]int{
                0: {1},
                1: {0},
                2: {},
            },
        },
    }

    for _, tc := range invalidTests {
        t.Run(tc.description, func(t *testing.T) {
            defer func() {
                if r := recover(); r == nil {
                    t.Errorf("EnumKCliques(%d, %d, %v) should have panicked",
                        tc.n, tc.k, tc.adjList)
                }
            }()
            EnumKCliques(tc.n, tc.k, tc.adjList)
        })
    }
}

// Benchmark for performance testing
func BenchmarkEnumKCliques(b *testing.B) {
    // Create a complete graph with 10 vertices
    n := 10
    adjList := make(map[int][]int)
    for i := 0; i < n; i++ {
        neighbors := make([]int, 0, n-1)
        for j := 0; j < n; j++ {
            if i != j {
                neighbors = append(neighbors, j)
            }
        }
        adjList[i] = neighbors
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        EnumKCliques(n, 4, adjList)
    }
}