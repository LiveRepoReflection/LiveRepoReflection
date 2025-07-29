package byzantine_agreement

import (
	"math/rand"
	"time"
)

type Message struct {
	Round   int
	Value   int
	Sender  int
}

type Node struct {
	ID           int
	Faulty       bool
	InitialValue int
	Received     map[int][]Message
	Decided      bool
	Decision     int
}

func ByzantineAgreement(n int, f int, initialValues []int) int {
	rand.Seed(time.Now().UnixNano())

	// Initialize nodes
	nodes := make([]*Node, n)
	for i := 0; i < n; i++ {
		nodes[i] = &Node{
			ID:           i,
			Faulty:       i < f, // First f nodes are faulty
			InitialValue: initialValues[i],
			Received:     make(map[int][]Message),
			Decided:     false,
		}
	}

	// Run rounds until all non-faulty nodes decide
	for round := 1; round <= f+1; round++ {
		// Phase 1: Send messages
		messages := make([]Message, 0)
		for _, node := range nodes {
			if !node.Decided {
				if node.Faulty {
					// Faulty nodes send random values to different nodes
					for j := 0; j < n; j++ {
						if j != node.ID {
							value := rand.Intn(2)
							messages = append(messages, Message{
								Round:  round,
								Value:  value,
								Sender: node.ID,
							})
						}
					}
				} else {
					// Honest nodes send their current value
					value := node.InitialValue
					if round > 1 {
						value = majorityValue(node.Received[round-1])
					}
					for j := 0; j < n; j++ {
						if j != node.ID {
							messages = append(messages, Message{
								Round:  round,
								Value:  value,
								Sender: node.ID,
							})
						}
					}
				}
			}
		}

		// Phase 2: Receive messages
		for _, msg := range messages {
			if msg.Round == round {
				receiver := msg.Sender % n // Simple routing for simulation
				if !nodes[receiver].Decided {
					nodes[receiver].Received[round] = append(nodes[receiver].Received[round], msg)
				}
			}
		}

		// Phase 3: Make decisions
		for _, node := range nodes {
			if !node.Decided && !node.Faulty {
				if round == f+1 {
					// Final decision
					node.Decision = majorityValue(node.Received[round])
					node.Decided = true
				} else {
					// Intermediate value
					node.InitialValue = majorityValue(node.Received[round])
				}
			}
		}
	}

	// Count decisions
	decisionCount := make(map[int]int)
	for _, node := range nodes {
		if !node.Faulty {
			decisionCount[node.Decision]++
		}
	}

	// Return majority decision
	if decisionCount[1] > decisionCount[0] {
		return 1
	}
	return 0
}

func majorityValue(messages []Message) int {
	count0 := 0
	count1 := 0
	for _, msg := range messages {
		if msg.Value == 0 {
			count0++
		} else {
			count1++
		}
	}
	if count1 > count0 {
		return 1
	}
	return 0
}