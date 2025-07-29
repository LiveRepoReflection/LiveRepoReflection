package network

// TestCase represents a test case for the network congestion control algorithm
type TestCase struct {
	Description string
	NumNodes    int
	Graph       map[int][]Edge
	Source      int
	Destination int
	Updates     []CapacityUpdate
	Expected    []float64
}

var testCases = []TestCase{
	{
		Description: "Simple linear network with three nodes",
		NumNodes:    3,
		Graph: map[int][]Edge{
			0: {
				{Destination: 1, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
			1: {
				{Destination: 2, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
		},
		Source:      0,
		Destination: 2,
		Updates: []CapacityUpdate{
			{Source: 0, Destination: 1, NewCapacity: 30},
			{Source: 1, Destination: 2, NewCapacity: 20},
			{Source: 0, Destination: 1, NewCapacity: 15},
		},
		Expected: []float64{30, 20, 15},
	},
	{
		Description: "Network with multiple paths",
		NumNodes:    4,
		Graph: map[int][]Edge{
			0: {
				{Destination: 1, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
				{Destination: 2, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
			1: {
				{Destination: 3, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
			2: {
				{Destination: 3, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
		},
		Source:      0,
		Destination: 3,
		Updates: []CapacityUpdate{
			{Source: 0, Destination: 1, NewCapacity: 40},
			{Source: 0, Destination: 2, NewCapacity: 30},
			{Source: 1, Destination: 3, NewCapacity: 25},
			{Source: 2, Destination: 3, NewCapacity: 35},
		},
		Expected: []float64{90, 70, 55, 60},
	},
	{
		Description: "Complex network with bottlenecks",
		NumNodes:    6,
		Graph: map[int][]Edge{
			0: {
				{Destination: 1, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 80},
				{Destination: 2, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 70},
			},
			1: {
				{Destination: 3, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 60},
				{Destination: 4, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
			2: {
				{Destination: 3, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 40},
				{Destination: 4, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 30},
			},
			3: {
				{Destination: 5, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
			4: {
				{Destination: 5, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 40},
			},
		},
		Source:      0,
		Destination: 5,
		Updates: []CapacityUpdate{
			{Source: 0, Destination: 1, NewCapacity: 60},
			{Source: 1, Destination: 3, NewCapacity: 40},
			{Source: 3, Destination: 5, NewCapacity: 30},
			{Source: 4, Destination: 5, NewCapacity: 20},
			{Source: 2, Destination: 4, NewCapacity: 15},
		},
		Expected: []float64{140, 120, 90, 70, 65},
	},
	{
		Description: "Network with changing capacities forcing path changes",
		NumNodes:    5,
		Graph: map[int][]Edge{
			0: {
				{Destination: 1, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 60},
				{Destination: 2, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 20},
			},
			1: {
				{Destination: 3, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
			2: {
				{Destination: 3, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 30},
				{Destination: 4, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 40},
			},
			3: {
				{Destination: 4, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 45},
			},
		},
		Source:      0,
		Destination: 4,
		Updates: []CapacityUpdate{
			{Source: 0, Destination: 1, NewCapacity: 15},
			{Source: 0, Destination: 2, NewCapacity: 70},
			{Source: 1, Destination: 3, NewCapacity: 25},
			{Source: 2, Destination: 4, NewCapacity: 60},
			{Source: 3, Destination: 4, NewCapacity: 20},
		},
		Expected: []float64{80, 90, 45, 95, 55},
	},
	{
		Description: "Larger network with multiple bottlenecks",
		NumNodes:    8,
		Graph: map[int][]Edge{
			0: {
				{Destination: 1, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
				{Destination: 2, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
			1: {
				{Destination: 3, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 40},
				{Destination: 4, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 30},
			},
			2: {
				{Destination: 4, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 45},
				{Destination: 5, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 35},
			},
			3: {
				{Destination: 6, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 25},
			},
			4: {
				{Destination: 6, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 20},
				{Destination: 7, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 30},
			},
			5: {
				{Destination: 7, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 40},
			},
			6: {
				{Destination: 7, MinCapacity: 10, MaxCapacity: 100, CurrentCapacity: 50},
			},
		},
		Source:      0,
		Destination: 7,
		Updates: []CapacityUpdate{
			{Source: 0, Destination: 1, NewCapacity: 30},
			{Source: 0, Destination: 2, NewCapacity: 70},
			{Source: 3, Destination: 6, NewCapacity: 15},
			{Source: 4, Destination: 7, NewCapacity: 50},
			{Source: 5, Destination: 7, NewCapacity: 20},
			{Source: 6, Destination: 7, NewCapacity: 25},
		},
		Expected: []float64{95, 115, 105, 125, 110, 95},
	},
}