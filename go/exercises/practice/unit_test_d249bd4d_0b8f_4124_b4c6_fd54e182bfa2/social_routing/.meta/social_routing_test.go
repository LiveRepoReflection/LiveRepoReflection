package socialrouting

import (
	"reflect"
	"testing"
	"time"
)

func TestFindRoutePath(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Set a timeout for each test case to avoid infinite loops
			done := make(chan bool)
			var result []string
			
			go func() {
				result = FindRoutePath(tc.network, tc.startUser, tc.endUser, tc.maxHops, tc.blacklist)
				done <- true
			}()
			
			select {
			case <-done:
				// For paths with multiple valid solutions of same length, we need to verify that:
				// 1. The path starts with startUser and ends with endUser
				// 2. The path length is the same as expected
				// 3. Each step in the path is valid (connected in the network)
				// 4. No blacklisted users are in the path
				
				if len(tc.expected) == 0 {
					// Should return empty path
					if len(result) != 0 {
						t.Errorf("Expected empty path, got %v", result)
					}
				} else if len(result) == 0 {
					// Should have found a path
					if len(tc.expected) != 0 {
						t.Errorf("Expected to find a path, got empty path")
					}
				} else {
					// Check if path starts with startUser and ends with endUser
					if result[0] != tc.startUser {
						t.Errorf("Path doesn't start with startUser. Expected %s, got %s", tc.startUser, result[0])
					}
					if result[len(result)-1] != tc.endUser {
						t.Errorf("Path doesn't end with endUser. Expected %s, got %s", tc.endUser, result[len(result)-1])
					}
					
					// Check if path length is within maxHops
					if len(result)-1 > tc.maxHops {
						t.Errorf("Path exceeds maxHops. Path: %v, maxHops: %d", result, tc.maxHops)
					}
					
					// Check if path is connected
					for i := 0; i < len(result)-1; i++ {
						current := result[i]
						next := result[i+1]
						
						// Check if next is a friend of current
						found := false
						for _, friend := range tc.network[current] {
							if friend == next {
								found = true
								break
							}
						}
						
						if !found {
							t.Errorf("Invalid path: %s is not connected to %s", current, next)
						}
					}
					
					// Check if path contains any blacklisted users
					for _, user := range result {
						for _, blacklisted := range tc.blacklist {
							if user == blacklisted {
								t.Errorf("Path contains blacklisted user: %s", user)
							}
						}
					}
					
					// If the expected path is specified exactly, check that it matches
					// This is optional since there might be multiple valid paths of the same length
					if reflect.DeepEqual(tc.expected, result) {
						// Paths match exactly as expected, which is good
					} else if len(tc.expected) != len(result) {
						// If the test expects a specific path length, make sure we match it
						t.Errorf("Path length differs. Expected %d, got %d. Path: %v", len(tc.expected), len(result), result)
					}
				}
				
			case <-time.After(2 * time.Second):
				t.Errorf("Test timed out")
			}
		})
	}
}

// Benchmarks to test the efficiency of the solution
func BenchmarkFindRoutePath(b *testing.B) {
	// Use a complex test case for benchmarking
	tc := testCases[9] // The complex network case
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindRoutePath(tc.network, tc.startUser, tc.endUser, tc.maxHops, tc.blacklist)
	}
}

// Test that the function doesn't panic with empty inputs
func TestEmptyInputs(t *testing.T) {
	// Empty network
	result := FindRoutePath(map[string][]string{}, "alice", "bob", 5, []string{})
	if len(result) != 0 {
		t.Errorf("Expected empty path for empty network, got %v", result)
	}
	
	// Empty blacklist should work fine
	network := map[string][]string{
		"alice": {"bob"},
		"bob":   {"alice"},
	}
	result = FindRoutePath(network, "alice", "bob", 5, []string{})
	if !reflect.DeepEqual(result, []string{"alice", "bob"}) {
		t.Errorf("Expected [alice, bob] with empty blacklist, got %v", result)
	}
	
	// MaxHops of 0
	result = FindRoutePath(network, "alice", "bob", 0, []string{})
	if len(result) != 0 {
		t.Errorf("Expected empty path for maxHops=0, got %v", result)
	}
}

// Test that the function handles negative maxHops gracefully
func TestNegativeMaxHops(t *testing.T) {
	network := map[string][]string{
		"alice": {"bob"},
		"bob":   {"alice"},
	}
	result := FindRoutePath(network, "alice", "bob", -1, []string{})
	if len(result) != 0 {
		t.Errorf("Expected empty path for negative maxHops, got %v", result)
	}
}