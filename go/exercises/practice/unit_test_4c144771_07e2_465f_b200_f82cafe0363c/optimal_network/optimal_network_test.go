package optimal_network

import "testing"

type testCase struct {
	description             string
	numLocations            int
	edges                   [][]int
	locationData            []LocationData
	baseStationCapacity     int
	numBaseStationsToDeploy int
	budget                  int
	expected                int
}

func TestOptimalNetworkDeployment(t *testing.T) {
	cases := []testCase{
		{
			description:  "Basic three node graph with chain links",
			numLocations: 3,
			edges: [][]int{
				{0, 1, 5},
				{1, 2, 5},
			},
			locationData: []LocationData{
				{DataDemand: 100, Population: 10},
				{DataDemand: 150, Population: 15},
				{DataDemand: 200, Population: 20},
			},
			baseStationCapacity:     250,
			numBaseStationsToDeploy: 2,
			budget:                  500,
			expected:                450,
		},
		{
			description:  "Four node graph with multiple connection options",
			numLocations: 4,
			edges: [][]int{
				{0, 1, 10},
				{1, 2, 10},
				{2, 3, 10},
				{0, 3, 30},
				{1, 3, 15},
			},
			locationData: []LocationData{
				{DataDemand: 300, Population: 20},
				{DataDemand: 250, Population: 30},
				{DataDemand: 400, Population: 40},
				{DataDemand: 350, Population: 25},
			},
			baseStationCapacity:     500,
			numBaseStationsToDeploy: 2,
			budget:                  1000,
			expected:                750,
		},
		{
			description:  "Single node graph",
			numLocations: 1,
			edges:        [][]int{},
			locationData: []LocationData{
				{DataDemand: 100, Population: 15},
			},
			baseStationCapacity:     150,
			numBaseStationsToDeploy: 1,
			budget:                  200,
			expected:                100,
		},
		{
			description:  "Three node graph with no connections",
			numLocations: 3,
			edges:        [][]int{},
			locationData: []LocationData{
				{DataDemand: 200, Population: 10},
				{DataDemand: 300, Population: 20},
				{DataDemand: 400, Population: 30},
			},
			baseStationCapacity:     500,
			numBaseStationsToDeploy: 2,
			budget:                  500,
			expected:                700,
		},
	}

	for _, tc := range cases {
		t.Run(tc.description, func(t *testing.T) {
			result := OptimalNetworkDeployment(tc.numLocations, tc.edges, tc.locationData, tc.baseStationCapacity, tc.numBaseStationsToDeploy, tc.budget)
			if result != tc.expected {
				t.Fatalf("Test %q failed: expected %d, got %d", tc.description, tc.expected, result)
			}
		})
	}
}