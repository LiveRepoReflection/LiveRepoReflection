package social_reach

import (
	"sync"
	"testing"
	"time"
)

func TestDirectFollow(t *testing.T) {
	g := NewSocialGraph()
	err := g.AddFollow(1, 2)
	if err != nil {
		t.Fatalf("unexpected error on AddFollow(1, 2): %v", err)
	}
	if !g.IsReachable(1, 2) {
		t.Errorf("expected 1 to reach 2, but IsReachable(1, 2) returned false")
	}
}

func TestChainReachability(t *testing.T) {
	g := NewSocialGraph()
	// Create a chain: 1 -> 2 -> 3 -> 4
	edges := []struct {
		follower int64
		followee int64
	}{
		{1, 2},
		{2, 3},
		{3, 4},
	}
	for _, edge := range edges {
		if err := g.AddFollow(edge.follower, edge.followee); err != nil {
			t.Fatalf("unexpected error on AddFollow(%d, %d): %v", edge.follower, edge.followee, err)
		}
	}
	if !g.IsReachable(1, 4) {
		t.Errorf("expected 1 to reach 4 through the chain, but IsReachable(1, 4) returned false")
	}
	if g.IsReachable(4, 1) {
		t.Errorf("expected 4 not to reach 1, but IsReachable(4, 1) returned true")
	}
}

func TestCyclicGraph(t *testing.T) {
	g := NewSocialGraph()
	// Create a cycle: 1 -> 2 -> 3 -> 1
	edges := []struct {
		follower int64
		followee int64
	}{
		{1, 2},
		{2, 3},
		{3, 1},
	}
	for _, edge := range edges {
		if err := g.AddFollow(edge.follower, edge.followee); err != nil {
			t.Fatalf("unexpected error on AddFollow(%d, %d): %v", edge.follower, edge.followee, err)
		}
	}
	if !g.IsReachable(1, 3) {
		t.Errorf("expected 1 to reach 3 in cyclic graph, but IsReachable(1, 3) returned false")
	}
	if !g.IsReachable(3, 2) {
		t.Errorf("expected 3 to reach 2 in cyclic graph, but IsReachable(3, 2) returned false")
	}
}

func TestDisconnectedGraph(t *testing.T) {
	g := NewSocialGraph()
	// Create two disconnected components: 1 -> 2 and 3 -> 4
	if err := g.AddFollow(1, 2); err != nil {
		t.Fatalf("unexpected error on AddFollow(1, 2): %v", err)
	}
	if err := g.AddFollow(3, 4); err != nil {
		t.Fatalf("unexpected error on AddFollow(3, 4): %v", err)
	}
	if g.IsReachable(1, 4) {
		t.Errorf("expected 1 not to reach 4 in a disconnected graph, but IsReachable(1, 4) returned true")
	}
	if g.IsReachable(4, 1) {
		t.Errorf("expected 4 not to reach 1 in a disconnected graph, but IsReachable(4, 1) returned true")
	}
}

func TestSelfReachability(t *testing.T) {
	g := NewSocialGraph()
	// A user should be reachable from itself
	if !g.IsReachable(5, 5) {
		t.Errorf("expected user 5 to be reachable from itself, but IsReachable(5, 5) returned false")
	}
}

func TestMultiplePaths(t *testing.T) {
	g := NewSocialGraph()
	// Create a graph with multiple paths:
	// 1 -> 2, 1 -> 3, 2 -> 4, and 3 -> 4.
	// Query: 1 should reach 4 via either path.
	edges := []struct {
		follower int64
		followee int64
	}{
		{1, 2},
		{1, 3},
		{2, 4},
		{3, 4},
	}
	for _, edge := range edges {
		if err := g.AddFollow(edge.follower, edge.followee); err != nil {
			t.Fatalf("unexpected error on AddFollow(%d, %d): %v", edge.follower, edge.followee, err)
		}
	}
	if !g.IsReachable(1, 4) {
		t.Errorf("expected 1 to reach 4 via multiple paths, but IsReachable(1, 4) returned false")
	}
}

func TestConcurrentUpdatesAndQueries(t *testing.T) {
	g := NewSocialGraph()
	var wg sync.WaitGroup

	// Start a goroutine to add a chain of follows concurrently.
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := int64(1); i < 1000; i++ {
			if err := g.AddFollow(i, i+1); err != nil {
				t.Errorf("unexpected error on AddFollow(%d, %d): %v", i, i+1, err)
			}
			// Sleep a tiny duration to simulate sporadic updates.
			time.Sleep(time.Microsecond)
		}
	}()

	// Start multiple goroutines to query reachability concurrently.
	queryFunc := func(start, end int64) {
		defer wg.Done()
		for i := int64(1); i < 1000; i++ {
			_ = g.IsReachable(start, i)
		}
	}

	wg.Add(2)
	go queryFunc(1, 500)
	go queryFunc(500, 1000)

	wg.Wait()

	// Validate that the full chain is established.
	if !g.IsReachable(1, 1000) {
		t.Errorf("expected 1 to reach 1000 after concurrent updates, but IsReachable(1, 1000) returned false")
	}
}