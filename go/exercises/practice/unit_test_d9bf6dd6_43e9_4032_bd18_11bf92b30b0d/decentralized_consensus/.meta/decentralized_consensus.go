package decentralized_consensus

import (
	"math/rand"
	"sort"
)

// Node represents a node in the decentralized consensus network
type Node struct {
	id              int
	currentValue    int64
	receivedValues  []int64
	sentToThisRound map[int]bool
}

// SimulateConsensus simulates the consensus protocol and determines if all nodes reach consensus
func SimulateConsensus(n, k, r int, initialValues []int64, messageLossProbability float64) bool {
	// Create a network of nodes
	nodes := make([]*Node, n)
	for i := 0; i < n; i++ {
		nodes[i] = &Node{
			id:              i,
			currentValue:    initialValues[i],
			receivedValues:  []int64{initialValues[i]}, // Start with own value
			sentToThisRound: make(map[int]bool),
		}
	}

	// Run for R rounds
	for round := 0; round < r; round++ {
		// Reset sent-to tracking for each round
		for i := 0; i < n; i++ {
			nodes[i].sentToThisRound = make(map[int]bool)
		}

		// Each node sends its value to K random other nodes
		messages := generateMessages(nodes, k, messageLossProbability)

		// Process messages
		for _, msg := range messages {
			receiverNode := nodes[msg.toID]
			receiverNode.receivedValues = append(receiverNode.receivedValues, msg.value)
		}

		// Update node values based on received messages
		for i := 0; i < n; i++ {
			if len(nodes[i].receivedValues) > 0 {
				nodes[i].currentValue = calculateMedian(nodes[i].receivedValues)
				// Clear received values for next round but keep own current value
				nodes[i].receivedValues = []int64{nodes[i].currentValue}
			}
		}

		// Check if consensus has been reached
		if checkConsensus(nodes) {
			return true
		}
	}

	return false
}

// Message represents a message sent from one node to another
type Message struct {
	fromID int
	toID   int
	value  int64
}

// generateMessages generates messages for the current round based on the protocol rules
func generateMessages(nodes []*Node, k int, messageLossProbability float64) []Message {
	var messages []Message
	n := len(nodes)

	for fromID, node := range nodes {
		// Skip if k is 0 or n is 1 (no other nodes to send to)
		if k == 0 || n <= 1 {
			continue
		}

		// Choose k random recipients without replacement
		availableNodes := make([]int, 0, n-1)
		for i := 0; i < n; i++ {
			if i != fromID {
				availableNodes = append(availableNodes, i)
			}
		}

		// Shuffle the available nodes
		rand.Shuffle(len(availableNodes), func(i, j int) {
			availableNodes[i], availableNodes[j] = availableNodes[j], availableNodes[i]
		})

		// Take the first k or fewer if there aren't k available
		numRecipients := k
		if numRecipients > len(availableNodes) {
			numRecipients = len(availableNodes)
		}

		for i := 0; i < numRecipients; i++ {
			toID := availableNodes[i]

			// Check if the message is lost due to network issues
			if rand.Float64() >= messageLossProbability {
				messages = append(messages, Message{
					fromID: fromID,
					toID:   toID,
					value:  node.currentValue,
				})
				nodes[fromID].sentToThisRound[toID] = true
			}
		}
	}

	return messages
}

// calculateMedian calculates the median of a slice of values
// If the number of values is even, it returns the smaller of the two middle values
func calculateMedian(values []int64) int64 {
	// Create a copy to avoid modifying the original slice
	valuesCopy := make([]int64, len(values))
	copy(valuesCopy, values)
	
	// Sort the copy
	sort.Slice(valuesCopy, func(i, j int) bool {
		return valuesCopy[i] < valuesCopy[j]
	})

	// Find the median
	length := len(valuesCopy)
	if length == 0 {
		return 0 // This should never happen in our protocol
	}
	
	if length%2 == 1 {
		// Odd number of elements
		return valuesCopy[length/2]
	} else {
		// Even number of elements: take the smaller of the two middle values
		return valuesCopy[(length/2)-1]
	}
}

// checkConsensus checks if all nodes have the same current value
func checkConsensus(nodes []*Node) bool {
	if len(nodes) <= 1 {
		return true
	}

	consensusValue := nodes[0].currentValue
	for i := 1; i < len(nodes); i++ {
		if nodes[i].currentValue != consensusValue {
			return false
		}
	}
	return true
}