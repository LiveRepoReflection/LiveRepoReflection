package intergalacticrouter

type testCase struct {
	description string
	graph       map[string]map[string][]int
	start       string
	end         string
	maxHops     int
	wantPath    []string
	wantRisk    int
}

var testCases = []testCase{
	{
		description: "Simple path with single option",
		graph: map[string]map[string][]int{
			"Earth": {
				"Mars": {5},
			},
			"Mars": {
				"Earth": {5},
			},
		},
		start:    "Earth",
		end:      "Mars",
		maxHops:  1,
		wantPath: []string{"Earth", "Mars"},
		wantRisk: 5,
	},
	{
		description: "Path with multiple wormhole options between same planets",
		graph: map[string]map[string][]int{
			"Earth": {
				"Mars": {5, 3, 8},
			},
			"Mars": {
				"Earth": {5, 3, 8},
			},
		},
		start:    "Earth",
		end:      "Mars",
		maxHops:  1,
		wantPath: []string{"Earth", "Mars"},
		wantRisk: 3,
	},
	{
		description: "Multiple possible paths",
		graph: map[string]map[string][]int{
			"Earth": {
				"Mars":           {5},
				"Alpha Centauri": {2},
			},
			"Mars": {
				"Earth":          {5},
				"Alpha Centauri": {7},
			},
			"Alpha Centauri": {
				"Earth": {2},
				"Mars":  {7},
			},
		},
		start:    "Earth",
		end:      "Mars",
		maxHops:  2,
		wantPath: []string{"Earth", "Mars"},
		wantRisk: 5,
	},
	{
		description: "Path exceeds maxHops",
		graph: map[string]map[string][]int{
			"Earth": {
				"Mars": {5},
			},
			"Mars": {
				"Earth": {5},
			},
		},
		start:    "Earth",
		end:      "Mars",
		maxHops:  0,
		wantPath: []string{},
		wantRisk: -1,
	},
	{
		description: "No path exists",
		graph: map[string]map[string][]int{
			"Earth": {
				"Mars": {5},
			},
			"Alpha Centauri": {
				"Beta Cygni": {3},
			},
		},
		start:    "Earth",
		end:      "Alpha Centauri",
		maxHops:  5,
		wantPath: []string{},
		wantRisk: -1,
	},
	{
		description: "Start planet doesn't exist",
		graph: map[string]map[string][]int{
			"Earth": {
				"Mars": {5},
			},
		},
		start:    "Jupiter",
		end:      "Mars",
		maxHops:  5,
		wantPath: []string{},
		wantRisk: -1,
	},
	{
		description: "Complex network",
		graph: map[string]map[string][]int{
			"Earth": {
				"Alpha Centauri": {5, 10},
				"Mars":           {2},
			},
			"Alpha Centauri": {
				"Earth":      {5, 10},
				"Beta Cygni": {7},
			},
			"Mars": {
				"Earth":      {2},
				"Beta Cygni": {1},
			},
			"Beta Cygni": {
				"Alpha Centauri":   {7},
				"Mars":            {1},
				"Epsilon Eridani": {3},
			},
			"Epsilon Eridani": {
				"Beta Cygni": {3},
			},
		},
		start:    "Earth",
		end:      "Epsilon Eridani",
		maxHops:  4,
		wantPath: []string{"Earth", "Mars", "Beta Cygni", "Epsilon Eridani"},
		wantRisk: 3,
	},
	{
		description: "Same start and end with maxHops 0",
		graph: map[string]map[string][]int{
			"Earth": {
				"Mars": {5},
			},
		},
		start:    "Earth",
		end:      "Earth",
		maxHops:  0,
		wantPath: []string{"Earth"},
		wantRisk: 0,
	},
}