package dist_consensus

import (
	"math/rand"
	"sort"
)

// Node represents a node in the distributed consensus network
type Node struct {
	ID             int
	CurrentValue   int
	InitialValue   int
	HasFailed      bool
	PartitionGroup int // -1 means not in any partition
}

// Network simulates the communication network between nodes
type Network struct {
	Nodes      []*Node
	Partitions [][]int
	rnd        *rand.Rand
}

// NewNetwork creates a new network with the given nodes, failed nodes, and partitions
func NewNetwork(initialValues []int, numFailedNodes int, partitions [][]int, seed int64) *Network {
	n := len(initialValues)
	nodes := make([]*Node, n)
	for i := 0; i < n; i++ {
		nodes[i] = &Node{
			ID:             i,
			CurrentValue:   initialValues[i],
			InitialValue:   initialValues[i],
			HasFailed:      false,
			PartitionGroup: -1,
		}
	}

	network := &Network{
		Nodes:      nodes,
		Partitions: partitions,
		rnd:        rand.New(rand.NewSource(seed)),
	}

	// Set up partitions
	for groupID, partition := range partitions {
		for _, nodeID := range partition {
			if nodeID >= 0 && nodeID < n {
				nodes[nodeID].PartitionGroup = groupID
			}
		}
	}

	// Randomly select nodes to fail
	if numFailedNodes > 0 {
		indexes := make([]int, n)
		for i := 0; i < n; i++ {
			indexes[i] = i
		}
		// Shuffle the array using the seeded random number generator
		for i := n - 1; i > 0; i-- {
			j := network.rnd.Intn(i + 1)
			indexes[i], indexes[j] = indexes[j], indexes[i]
		}

		// Mark the first numFailedNodes as failed
		failCount := min(numFailedNodes, n)
		for i := 0; i < failCount; i++ {
			nodes[indexes[i]].HasFailed = true
		}
	}

	return network
}

// Simulate runs the distributed consensus algorithm for the specified number of rounds
func Simulate(initialValues []int, maxRounds int, numFailedNodes int, partitions [][]int, seed int64) []int {
	network := NewNetwork(initialValues, numFailedNodes, partitions, seed)
	n := len(initialValues)

	// Run the simulation for maxRounds
	for round := 0; round < maxRounds; round++ {
		// For each active node, collect proposals from other nodes
		proposals := make([][]int, n)
		for i := 0; i < n; i++ {
			if network.Nodes[i].HasFailed {
				continue
			}

			// Initialize with node's own proposal
			proposals[i] = []int{network.Nodes[i].CurrentValue}

			// Collect proposals from other nodes
			for j := 0; j < n; j++ {
				if i == j || network.Nodes[j].HasFailed {
					continue
				}

				// Check if nodes can communicate (same partition or no partition defined)
				canCommunicate := false
				if network.Nodes[i].PartitionGroup == -1 && network.Nodes[j].PartitionGroup == -1 {
					canCommunicate = true
				} else if network.Nodes[i].PartitionGroup != -1 && 
                        network.Nodes[i].PartitionGroup == network.Nodes[j].PartitionGroup {
					canCommunicate = true
				}

				if canCommunicate {
					proposals[i] = append(proposals[i], network.Nodes[j].CurrentValue)
				}
			}
		}

		// Update each active node's value based on received proposals
		for i := 0; i < n; i++ {
			if network.Nodes[i].HasFailed {
				continue
			}

			if len(proposals[i]) > 0 {
				network.Nodes[i].CurrentValue = updateValue(proposals[i])
			}
		}
	}

	// Gather final values from all nodes
	finalValues := make([]int, n)
	for i := 0; i < n; i++ {
		finalValues[i] = network.Nodes[i].CurrentValue
	}
	return finalValues
}

// updateValue updates a node's value based on the received proposals
func updateValue(proposals []int) int {
	// Count occurrences to check for majority
	counts := make(map[int]int)
	for _, v := range proposals {
		counts[v]++
	}

	// Check for strict majority
	for value, count := range counts {
		if count > len(proposals)/2 {
			return value
		}
	}

	// No majority, return median
	return median(proposals)
}

// median calculates the median of a slice of integers
// If the length is even, it returns the lower median
func median(values []int) int {
	if len(values) == 0 {
		return 0
	}

	// Create a copy to avoid modifying the original slice
	sorted := make([]int, len(values))
	copy(sorted, values)
	sort.Ints(sorted)

	middle := len(sorted) / 2

	// If even number of elements, take the lower median
	if len(sorted)%2 == 0 {
		return sorted[middle-1]
	}
	
	return sorted[middle]
}

// min returns the smaller of x or y
func min(x, y int) int {
	if x < y {
		return x
	}
	return y
}