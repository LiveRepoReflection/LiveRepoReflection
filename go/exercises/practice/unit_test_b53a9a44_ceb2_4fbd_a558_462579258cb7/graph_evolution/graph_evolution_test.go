package graph_evolution

import (
	"math/rand"
	"testing"
)

func TestGraphEvolution(t *testing.T) {
	rand.Seed(42) // Fixed seed for deterministic tests

	tests := []struct {
		name           string
		n              int
		initialGraph   [][]bool
		evolutionRules []EvolutionRule
		timeSteps      int
		expectedGraph  [][]bool
	}{
		{
			name: "single user no changes",
			n:    1,
			initialGraph: [][]bool{
				{false},
			},
			evolutionRules: []EvolutionRule{},
			timeSteps:      10,
			expectedGraph: [][]bool{
				{false},
			},
		},
		{
			name: "two users with certain follow",
			n:    2,
			initialGraph: [][]bool{
				{false, false},
				{false, false},
			},
			evolutionRules: []EvolutionRule{
				{SourceUser: 0, TargetUser: 1, ActionType: "follow", Probability: 1.0},
			},
			timeSteps: 1,
			expectedGraph: [][]bool{
				{false, true},
				{false, false},
			},
		},
		{
			name: "three users with probabilistic rules",
			n:    3,
			initialGraph: [][]bool{
				{false, false, false},
				{false, false, false},
				{false, false, false},
			},
			evolutionRules: []EvolutionRule{
				{SourceUser: 0, TargetUser: 1, ActionType: "follow", Probability: 0.5},
				{SourceUser: 1, TargetUser: 2, ActionType: "follow", Probability: 0.5},
			},
			timeSteps: 10,
			// Expected graph is probabilistic, so we can only check some invariants
			expectedGraph: nil, // Will be checked specially
		},
		{
			name: "self follow attempt",
			n:    2,
			initialGraph: [][]bool{
				{false, false},
				{false, false},
			},
			evolutionRules: []EvolutionRule{
				{SourceUser: 0, TargetUser: 0, ActionType: "follow", Probability: 1.0},
			},
			timeSteps: 1,
			expectedGraph: [][]bool{
				{false, false},
				{false, false},
			},
		},
		{
			name: "multiple rules same users",
			n:    2,
			initialGraph: [][]bool{
				{false, true},
				{false, false},
			},
			evolutionRules: []EvolutionRule{
				{SourceUser: 0, TargetUser: 1, ActionType: "unfollow", Probability: 1.0},
				{SourceUser: 0, TargetUser: 1, ActionType: "follow", Probability: 1.0},
			},
			timeSteps: 1,
			expectedGraph: [][]bool{
				{false, true},
				{false, false},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := SimulateGraphEvolution(tt.n, tt.initialGraph, tt.evolutionRules, tt.timeSteps)

			if tt.expectedGraph != nil {
				if !equalGraphs(result, tt.expectedGraph) {
					t.Errorf("SimulateGraphEvolution() = %v, want %v", result, tt.expectedGraph)
				}
			} else {
				// For probabilistic tests, just verify the graph structure is valid
				if len(result) != tt.n || len(result[0]) != tt.n {
					t.Errorf("Result graph has incorrect dimensions")
				}
			}
		})
	}
}

func equalGraphs(a, b [][]bool) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if len(a[i]) != len(b[i]) {
			return false
		}
		for j := range a[i] {
			if a[i][j] != b[i][j] {
				return false
			}
		}
	}
	return true
}