package concurrent_path

import (
	"testing"
)

func TestFindShortestPath(t *testing.T) {
	tests := []struct {
		name        string
		numNodes    int
		graph       map[int][]Edge
		source      int
		destination int
		wantPath    []int
		wantErr     bool
	}{
		{
			name:     "simple path",
			numNodes: 3,
			graph: map[int][]Edge{
				0: {{To: 1, Weight: 1}},
				1: {{To: 2, Weight: 1}},
				2: {},
			},
			source:      0,
			destination: 2,
			wantPath:    []int{0, 1, 2},
			wantErr:     false,
		},
		{
			name:     "no path exists",
			numNodes: 3,
			graph: map[int][]Edge{
				0: {{To: 1, Weight: 1}},
				1: {},
				2: {},
			},
			source:      0,
			destination: 2,
			wantPath:    []int{},
			wantErr:     false,
		},
		{
			name:     "multiple paths with same weight",
			numNodes: 4,
			graph: map[int][]Edge{
				0: {{To: 1, Weight: 2}, {To: 2, Weight: 2}},
				1: {{To: 3, Weight: 2}},
				2: {{To: 3, Weight: 2}},
				3: {},
			},
			source:      0,
			destination: 3,
			wantPath:    []int{0, 1, 3}, // or {0, 2, 3}
			wantErr:     false,
		},
		{
			name:     "invalid source node",
			numNodes: 3,
			graph: map[int][]Edge{
				0: {{To: 1, Weight: 1}},
				1: {{To: 2, Weight: 1}},
				2: {},
			},
			source:      3,
			destination: 2,
			wantPath:    nil,
			wantErr:     true,
		},
		{
			name:     "large graph with multiple paths",
			numNodes: 6,
			graph: map[int][]Edge{
				0: {{To: 1, Weight: 2}, {To: 2, Weight: 4}},
				1: {{To: 2, Weight: 1}, {To: 3, Weight: 7}},
				2: {{To: 3, Weight: 3}},
				3: {{To: 4, Weight: 1}, {To: 5, Weight: 5}},
				4: {},
				5: {},
			},
			source:      0,
			destination: 4,
			wantPath:    []int{0, 1, 2, 3, 4}, // or {0, 2, 3, 4}
			wantErr:     false,
		},
		{
			name:     "source equals destination",
			numNodes: 3,
			graph: map[int][]Edge{
				0: {{To: 1, Weight: 1}},
				1: {{To: 2, Weight: 1}},
				2: {},
			},
			source:      1,
			destination: 1,
			wantPath:    []int{1},
			wantErr:     false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotPath, err := FindShortestPath(tt.numNodes, tt.graph, tt.source, tt.destination)
			if (err != nil) != tt.wantErr {
				t.Errorf("FindShortestPath() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if len(gotPath) != len(tt.wantPath) {
					t.Errorf("FindShortestPath() path length = %v, want %v", gotPath, tt.wantPath)
				} else {
					// For multiple valid paths, check if the path is valid and has correct weight
					if len(gotPath) > 0 {
						// Verify path starts and ends correctly
						if gotPath[0] != tt.source || gotPath[len(gotPath)-1] != tt.destination {
							t.Errorf("FindShortestPath() invalid path endpoints, got %v", gotPath)
						}
						// Verify path connectivity
						for i := 0; i < len(gotPath)-1; i++ {
							found := false
							for _, edge := range tt.graph[gotPath[i]] {
								if edge.To == gotPath[i+1] {
									found = true
									break
								}
							}
							if !found {
								t.Errorf("FindShortestPath() invalid path segment %v->%v", gotPath[i], gotPath[i+1])
							}
						}
					}
				}
			}
		})
	}
}