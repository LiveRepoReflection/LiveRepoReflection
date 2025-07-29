package ride_share

import (
	"testing"
	"time"
)

func TestOptimalRideSharing(t *testing.T) {
	// Test case 1: Simple graph with one vehicle and one ride
	graph1 := map[int][]Edge{
		1: {{2, 10}},
		2: {{3, 15}},
		3: {},
	}

	rides1 := []RideRequest{
		{Start: 1, Destination: 3, PickupTime: 100, DropoffLimit: 150, Passengers: 1},
	}

	vehicles1 := []Vehicle{
		{Location: 1, Capacity: 2},
	}

	assignments, fulfilled := OptimalRideSharing(graph1, rides1, vehicles1, 2)
	if fulfilled != 1 {
		t.Errorf("Test case 1 failed: expected 1 fulfilled ride, got %d", fulfilled)
	}
	if len(assignments) != 1 {
		t.Errorf("Test case 1 failed: expected 1 assignment, got %d", len(assignments))
	}

	// Test case 2: No possible rides due to capacity
	graph2 := map[int][]Edge{
		1: {{2, 10}},
		2: {},
	}

	rides2 := []RideRequest{
		{Start: 1, Destination: 2, PickupTime: 100, DropoffLimit: 150, Passengers: 3},
	}

	vehicles2 := []Vehicle{
		{Location: 1, Capacity: 2},
	}

	assignments, fulfilled = OptimalRideSharing(graph2, rides2, vehicles2, 2)
	if fulfilled != 0 {
		t.Errorf("Test case 2 failed: expected 0 fulfilled rides, got %d", fulfilled)
	}

	// Test case 3: Multiple vehicles and rides
	graph3 := map[int][]Edge{
		1: {{2, 10}, {3, 20}},
		2: {{4, 15}},
		3: {{4, 5}},
		4: {},
	}

	rides3 := []RideRequest{
		{Start: 1, Destination: 4, PickupTime: 100, DropoffLimit: 150, Passengers: 1},
		{Start: 2, Destination: 4, PickupTime: 110, DropoffLimit: 140, Passengers: 2},
		{Start: 3, Destination: 4, PickupTime: 120, DropoffLimit: 150, Passengers: 1},
	}

	vehicles3 := []Vehicle{
		{Location: 1, Capacity: 2},
		{Location: 2, Capacity: 2},
	}

	assignments, fulfilled = OptimalRideSharing(graph3, rides3, vehicles3, 2)
	if fulfilled < 2 {
		t.Errorf("Test case 3 failed: expected at least 2 fulfilled rides, got %d", fulfilled)
	}

	// Test case 4: Time constraints
	now := time.Now().Unix()
	graph4 := map[int][]Edge{
		1: {{2, 60}}, // 1 minute travel time
		2: {},
	}

	rides4 := []RideRequest{
		{Start: 1, Destination: 2, PickupTime: now, DropoffLimit: now + 30, Passengers: 1}, // Impossible (needs 60s)
		{Start: 1, Destination: 2, PickupTime: now, DropoffLimit: now + 120, Passengers: 1}, // Possible
	}

	vehicles4 := []Vehicle{
		{Location: 1, Capacity: 2},
	}

	assignments, fulfilled = OptimalRideSharing(graph4, rides4, vehicles4, 2)
	if fulfilled != 1 {
		t.Errorf("Test case 4 failed: expected 1 fulfilled ride, got %d", fulfilled)
	}

	// Test case 5: Large graph with multiple paths
	graph5 := map[int][]Edge{
		1: {{2, 5}, {3, 10}},
		2: {{4, 10}, {5, 20}},
		3: {{5, 15}},
		4: {{6, 5}},
		5: {{6, 10}},
		6: {},
	}

	rides5 := []RideRequest{
		{Start: 1, Destination: 6, PickupTime: 1000, DropoffLimit: 1040, Passengers: 1},
		{Start: 2, Destination: 6, PickupTime: 1010, DropoffLimit: 1035, Passengers: 1},
		{Start: 3, Destination: 6, PickupTime: 1020, DropoffLimit: 1060, Passengers: 2},
	}

	vehicles5 := []Vehicle{
		{Location: 1, Capacity: 2},
		{Location: 2, Capacity: 2},
		{Location: 3, Capacity: 2},
	}

	assignments, fulfilled = OptimalRideSharing(graph5, rides5, vehicles5, 2)
	if fulfilled != 3 {
		t.Errorf("Test case 5 failed: expected 3 fulfilled rides, got %d", fulfilled)
	}
}

func BenchmarkOptimalRideSharing(b *testing.B) {
	graph := map[int][]Edge{
		1: {{2, 5}, {3, 10}},
		2: {{4, 10}, {5, 20}},
		3: {{5, 15}},
		4: {{6, 5}},
		5: {{6, 10}},
		6: {},
	}

	rides := []RideRequest{
		{Start: 1, Destination: 6, PickupTime: 1000, DropoffLimit: 1040, Passengers: 1},
		{Start: 2, Destination: 6, PickupTime: 1010, DropoffLimit: 1035, Passengers: 1},
		{Start: 3, Destination: 6, PickupTime: 1020, DropoffLimit: 1060, Passengers: 2},
	}

	vehicles := []Vehicle{
		{Location: 1, Capacity: 2},
		{Location: 2, Capacity: 2},
		{Location: 3, Capacity: 2},
	}

	for i := 0; i < b.N; i++ {
		OptimalRideSharing(graph, rides, vehicles, 2)
	}
}