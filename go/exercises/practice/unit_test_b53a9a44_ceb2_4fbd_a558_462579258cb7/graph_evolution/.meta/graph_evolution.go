package graph_evolution

import (
	"math/rand"
	"time"
)

type EvolutionRule struct {
	SourceUser  int
	TargetUser  int
	ActionType  string
	Probability float64
}

func SimulateGraphEvolution(n int, initialGraph [][]bool, evolutionRules []EvolutionRule, timeSteps int) [][]bool {
	// Create a copy of the initial graph
	currentGraph := make([][]bool, n)
	for i := range initialGraph {
		currentGraph[i] = make([]bool, n)
		copy(currentGraph[i], initialGraph[i])
	}

	// Initialize random number generator
	r := rand.New(rand.NewSource(time.Now().UnixNano()))

	for step := 0; step < timeSteps; step++ {
		// Apply each rule in sequence
		for _, rule := range evolutionRules {
			// Skip invalid rules
			if rule.SourceUser < 0 || rule.SourceUser >= n ||
				rule.TargetUser < 0 || rule.TargetUser >= n ||
				rule.SourceUser == rule.TargetUser {
				continue
			}

			// Apply rule based on probability
			if r.Float64() < rule.Probability {
				switch rule.ActionType {
				case "follow":
					currentGraph[rule.SourceUser][rule.TargetUser] = true
				case "unfollow":
					currentGraph[rule.SourceUser][rule.TargetUser] = false
				}
			}
		}
	}

	return currentGraph
}