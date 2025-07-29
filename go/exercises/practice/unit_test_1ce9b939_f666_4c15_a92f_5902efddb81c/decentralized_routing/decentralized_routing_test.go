package decentralized_routing

import (
	"testing"
	"reflect"
)

func TestRouteMessage(t *testing.T) {
	for _, tt := range routeTests {
		t.Run(tt.description, func(t *testing.T) {
			actualPaths := RouteMessage(tt.originServer, tt.userID, tt.message, tt.networkState)
			
			if !reflect.DeepEqual(actualPaths, tt.expectedPaths) {
				t.Errorf("RouteMessage(%q, %q, %q, ...)\n got paths: %v\n want paths: %v",
					tt.originServer, tt.userID, tt.message, actualPaths, tt.expectedPaths)
			}
		})
	}
}

func BenchmarkRouteMessage(b *testing.B) {
	if testing.Short() {
		b.Skip("skipping benchmark in short mode.")
	}
	
	// Use the most complex test case for benchmarking
	testCase := routeTests[1]
	for i := 0; i < b.N; i++ {
		RouteMessage(testCase.originServer, testCase.userID, testCase.message, testCase.networkState)
	}
}