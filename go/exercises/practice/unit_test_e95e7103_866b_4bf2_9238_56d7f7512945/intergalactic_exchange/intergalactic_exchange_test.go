package intergalactic_exchange

import (
	"reflect"
	"testing"
)

// Assume the existence of the following function in your implementation:
// func FindOptimalRoute(systems map[string]string, rates map[string]map[string]float64, startSystem, endSystem string, initialInvestment float64) []string

type testCase struct {
	description      string
	systems          map[string]string
	rates            map[string]map[string]float64
	startSystem      string
	endSystem        string
	investment       float64
	expectedRoute    []string
}

func TestFindOptimalRoute(t *testing.T) {
	testCases := []testCase{
		{
			description: "Start and end are the same",
			systems: map[string]string{
				"Alpha": "A",
				"Beta":  "B",
			},
			rates:          map[string]map[string]float64{},
			startSystem:    "Alpha",
			endSystem:      "Alpha",
			investment:     100.0,
			expectedRoute:  []string{"Alpha"},
		},
		{
			description: "Simple direct exchange",
			systems: map[string]string{
				"Alpha": "A",
				"Beta":  "B",
			},
			rates: map[string]map[string]float64{
				"A": {"B": 2.0},
			},
			startSystem:   "Alpha",
			endSystem:     "Beta",
			investment:    50.0,
			expectedRoute: []string{"Alpha", "Beta"},
		},
		{
			description: "Multiple hops are more profitable than direct route",
			systems: map[string]string{
				"Alpha": "A",
				"Beta":  "B",
				"Gamma": "C",
			},
			rates: map[string]map[string]float64{
				"A": {"B": 1.5, "C": 2.8},
				"B": {"C": 2.0},
			},
			startSystem:   "Alpha",
			endSystem:     "Gamma",
			investment:    100.0,
			// Via Alpha->Beta->Gamma, final=100*1.5*2.0=300 versus direct 100*2.8=280.
			expectedRoute: []string{"Alpha", "Beta", "Gamma"},
		},
		{
			description: "No possible route",
			systems: map[string]string{
				"Alpha": "A",
				"Beta":  "B",
			},
			// Rates do not connect A to B.
			rates:         map[string]map[string]float64{},
			startSystem:   "Alpha",
			endSystem:     "Beta",
			investment:    100.0,
			expectedRoute: []string{},
		},
		{
			description: "Tie-breaker: Fewer exchanges win",
			systems: map[string]string{
				"Alpha": "A",
				"Beta":  "B",
				"Delta": "D",
			},
			rates: map[string]map[string]float64{
				"A": {"B": 1.5, "D": 1.5},
				"B": {"D": 1.0},
			},
			startSystem:   "Alpha",
			endSystem:     "Delta",
			investment:    100.0,
			// Both routes yield factor 1.5, but direct route has fewer exchanges.
			expectedRoute: []string{"Alpha", "Delta"},
		},
		{
			description: "Tie-breaker: Lexicographical order",
			systems: map[string]string{
				"Alpha": "A",
				"Beta":  "B",
				"Gamma": "C",
				"Delta": "D",
			},
			rates: map[string]map[string]float64{
				"A": {"B": 2.0, "C": 2.0},
				"B": {"D": 2.0},
				"C": {"D": 2.0},
			},
			startSystem:   "Alpha",
			endSystem:     "Delta",
			investment:    50.0,
			// Two routes: Alpha->B->Delta and Alpha->C->Delta.
			// Both yield 50 * 2.0 * 2.0 = 200.0; choose lexicographically smaller route ["Alpha", "Beta", "Delta"].
			expectedRoute: []string{"Alpha", "Beta", "Delta"},
		},
		{
			description: "Cycle exists but non-profitable cycle is avoided",
			systems: map[string]string{
				"Alpha": "A",
				"Beta":  "B",
				"Gamma": "C",
			},
			rates: map[string]map[string]float64{
				"A": {"B": 1.1, "C": 1.0},
				"B": {"C": 0.9, "A": 1.0},
				"C": {"A": 1.0},
			},
			startSystem:   "Alpha",
			endSystem:     "Gamma",
			investment:    100.0,
			// Direct route Alpha->C gives 100.0; the route via Beta gives 100*1.1*0.9 = 99.0.
			// The optimal route is the direct one.
			expectedRoute: []string{"Alpha", "Gamma"},
		},
	}

	for _, tc := range testCases {
		actual := FindOptimalRoute(tc.systems, tc.rates, tc.startSystem, tc.endSystem, tc.investment)
		if !reflect.DeepEqual(actual, tc.expectedRoute) {
			t.Errorf("Test '%s' failed:\nExpected: %#v\nGot:      %#v", tc.description, tc.expectedRoute, actual)
		}
	}
}