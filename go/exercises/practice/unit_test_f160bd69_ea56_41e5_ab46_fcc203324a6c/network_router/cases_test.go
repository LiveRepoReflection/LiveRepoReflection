package networkrouter

// Test cases for the network router implementation
var testCases = []struct {
	description string
	graph       NetworkGraph
	requests    []ContentRequest
	wantPaths   map[int][]int
	wantRejects []int
}{
	{
		description: "Simple path - single request",
		graph: NetworkGraph{
			Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
			Edges: []Edge{
				{Source: 1, Destination: 2, Latency: 10, Bandwidth: 100},
				{Source: 2, Destination: 3, Latency: 20, Bandwidth: 100},
			},
		},
		requests: []ContentRequest{
			{UserID: 1, ContentID: 1, SourceServer: 1, DestinationServer: 3, BandwidthRequired: 50},
		},
		wantPaths: map[int][]int{
			1: {1, 2, 3},
		},
		wantRejects: []int{},
	},
	{
		description: "Bandwidth exceeded - rejection required",
		graph: NetworkGraph{
			Nodes: []Node{{ID: 1}, {ID: 2}},
			Edges: []Edge{
				{Source: 1, Destination: 2, Latency: 10, Bandwidth: 50},
			},
		},
		requests: []ContentRequest{
			{UserID: 1, ContentID: 1, SourceServer: 1, DestinationServer: 2, BandwidthRequired: 100},
		},
		wantPaths:   map[int][]int{},
		wantRejects: []int{1},
	},
	{
		description: "Multiple paths - choose lowest latency",
		graph: NetworkGraph{
			Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}, {ID: 4}},
			Edges: []Edge{
				{Source: 1, Destination: 2, Latency: 10, Bandwidth: 100},
				{Source: 2, Destination: 4, Latency: 10, Bandwidth: 100},
				{Source: 1, Destination: 3, Latency: 5, Bandwidth: 100},
				{Source: 3, Destination: 4, Latency: 5, Bandwidth: 100},
			},
		},
		requests: []ContentRequest{
			{UserID: 1, ContentID: 1, SourceServer: 1, DestinationServer: 4, BandwidthRequired: 50},
		},
		wantPaths: map[int][]int{
			1: {1, 3, 4},
		},
		wantRejects: []int{},
	},
	{
		description: "Multiple concurrent requests with limited bandwidth",
		graph: NetworkGraph{
			Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
			Edges: []Edge{
				{Source: 1, Destination: 2, Latency: 10, Bandwidth: 100},
				{Source: 2, Destination: 3, Latency: 10, Bandwidth: 100},
			},
		},
		requests: []ContentRequest{
			{UserID: 1, ContentID: 1, SourceServer: 1, DestinationServer: 3, BandwidthRequired: 60},
			{UserID: 2, ContentID: 2, SourceServer: 1, DestinationServer: 3, BandwidthRequired: 50},
		},
		wantPaths: map[int][]int{
			1: {1, 2, 3},
		},
		wantRejects: []int{2},
	},
	{
		description: "No path available",
		graph: NetworkGraph{
			Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
			Edges: []Edge{
				{Source: 1, Destination: 2, Latency: 10, Bandwidth: 100},
			},
		},
		requests: []ContentRequest{
			{UserID: 1, ContentID: 1, SourceServer: 1, DestinationServer: 3, BandwidthRequired: 50},
		},
		wantPaths:   map[int][]int{},
		wantRejects: []int{1},
	},
}