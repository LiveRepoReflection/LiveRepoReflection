package intergalacticrouter

import (
	"reflect"
	"testing"
)

func TestFindSafestRoute(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			gotPath, gotRisk := FindSafestRoute(tc.graph, tc.start, tc.end, tc.maxHops)
			
			if !reflect.DeepEqual(gotPath, tc.wantPath) {
				t.Errorf("FindSafestRoute() path = %v, want %v", gotPath, tc.wantPath)
			}
			
			if gotRisk != tc.wantRisk {
				t.Errorf("FindSafestRoute() risk = %v, want %v", gotRisk, tc.wantRisk)
			}
		})
	}
}

func BenchmarkFindSafestRoute(b *testing.B) {
	// Use the complex network test case for benchmarking
	tc := testCases[6]
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindSafestRoute(tc.graph, tc.start, tc.end, tc.maxHops)
	}
}