package social_path

import (
	"reflect"
	"testing"
)

// FindPath is assumed to be implemented in the social_path package.
// It takes a userNode function, a starting user ID, a target user ID, and a maximum path length.
// It returns a slice of strings representing the path from startUserID to targetUserID.
// If no valid path exists within the maxPathLength, it returns an empty slice.
func TestFindPath(t *testing.T) {
	type testCase struct {
		name          string
		startUserID   string
		targetUserID  string
		maxPathLength int
		network       map[string][]string
		expected      []string
	}

	// userNodeFunc returns a function that simulates querying a user node.
	// The function returns the local graph for the given user ID as a map.
	userNodeFunc := func(network map[string][]string) func(string) map[string][]string {
		return func(userID string) map[string][]string {
			if connections, ok := network[userID]; ok {
				return map[string][]string{userID: connections}
			}
			return map[string][]string{}
		}
	}

	tests := []testCase{
		{
			name:          "direct connection",
			startUserID:   "A",
			targetUserID:  "B",
			maxPathLength: 2,
			network: map[string][]string{
				"A": {"B"},
				"B": {"A"},
			},
			expected: []string{"A", "B"},
		},
		{
			name:          "indirect connection multiple hops",
			startUserID:   "A",
			targetUserID:  "D",
			maxPathLength: 3,
			network: map[string][]string{
				"A": {"B", "C"},
				"B": {"A", "D", "E"},
				"C": {"A", "F"},
				"D": {"B"},
				"E": {"B"},
				"F": {"C"},
			},
			expected: []string{"A", "B", "D"},
		},
		{
			name:          "target not reachable within maxPath length limit",
			startUserID:   "A",
			targetUserID:  "F",
			maxPathLength: 1,
			network: map[string][]string{
				"A": {"B", "C"},
				"B": {"A", "D"},
				"C": {"A", "F"},
				"D": {"B"},
				"F": {"C"},
			},
			expected: []string{},
		},
		{
			name:          "non-existent target",
			startUserID:   "A",
			targetUserID:  "Z",
			maxPathLength: 3,
			network: map[string][]string{
				"A": {"B"},
				"B": {"A", "C"},
				"C": {"B"},
			},
			expected: []string{},
		},
		{
			name:          "start equals target",
			startUserID:   "A",
			targetUserID:  "A",
			maxPathLength: 3,
			network: map[string][]string{
				"A": {"B"},
				"B": {"A", "C"},
				"C": {"B"},
			},
			expected: []string{},
		},
		{
			name:          "cycle in network",
			startUserID:   "A",
			targetUserID:  "D",
			maxPathLength: 4,
			network: map[string][]string{
				"A": {"B"},
				"B": {"C"},
				"C": {"A", "D"},
				"D": {"C"},
			},
			expected: []string{"A", "B", "C", "D"},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			path := FindPath(userNodeFunc(tc.network), tc.startUserID, tc.targetUserID, tc.maxPathLength)
			if !reflect.DeepEqual(path, tc.expected) {
				t.Errorf("Test %q failed: expected %v, got %v", tc.name, tc.expected, path)
			}
		})
	}
}

func BenchmarkFindPath(b *testing.B) {
	network := map[string][]string{
		"A": {"B", "C"},
		"B": {"A", "D", "E"},
		"C": {"A", "F"},
		"D": {"B", "G"},
		"E": {"B", "H"},
		"F": {"C", "I"},
		"G": {"D"},
		"H": {"E"},
		"I": {"F"},
	}
	userNodeFunc := func(userID string) map[string][]string {
		if connections, ok := network[userID]; ok {
			return map[string][]string{userID: connections}
		}
		return map[string][]string{}
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = FindPath(userNodeFunc, "A", "I", 5)
	}
}