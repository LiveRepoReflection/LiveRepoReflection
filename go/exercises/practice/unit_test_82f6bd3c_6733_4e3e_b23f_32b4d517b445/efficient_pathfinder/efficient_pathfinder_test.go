package efficient_pathfinder

import (
	"testing"
	"sync"
)

func TestPathfinder_EmptyNetwork(t *testing.T) {
	pf := NewPathfinder(5)
	if cost := pf.Query(0, 1); cost != -1 {
		t.Errorf("Expected -1 for no path, got %d", cost)
	}
}

func TestPathfinder_BasicPath(t *testing.T) {
	pf := NewPathfinder(3)
	pf.Update("add", 0, 1, 5)
	pf.Update("add", 1, 2, 3)

	if cost := pf.Query(0, 2); cost != 8 {
		t.Errorf("Expected cost 8, got %d", cost)
	}
}

func TestPathfinder_UpdateEdge(t *testing.T) {
	pf := NewPathfinder(3)
	pf.Update("add", 0, 1, 5)
	pf.Update("add", 1, 2, 3)
	pf.Update("add", 0, 2, 10)
	pf.Update("update", 0, 2, 8)

	if cost := pf.Query(0, 2); cost != 8 {
		t.Errorf("Expected cost 8 after update, got %d", cost)
	}
}

func TestPathfinder_RemoveEdge(t *testing.T) {
	pf := NewPathfinder(3)
	pf.Update("add", 0, 1, 5)
	pf.Update("add", 1, 2, 3)
	pf.Update("remove", 1, 2, 0)

	if cost := pf.Query(0, 2); cost != -1 {
		t.Errorf("Expected -1 after edge removal, got %d", cost)
	}
}

func TestPathfinder_SelfLoop(t *testing.T) {
	pf := NewPathfinder(2)
	pf.Update("add", 0, 0, 1)

	if cost := pf.Query(0, 0); cost != 0 {
		t.Errorf("Expected 0 for self path, got %d", cost)
	}
}

func TestPathfinder_ParallelEdges(t *testing.T) {
	pf := NewPathfinder(2)
	pf.Update("add", 0, 1, 5)
	pf.Update("add", 0, 1, 3)

	if cost := pf.Query(0, 1); cost != 3 {
		t.Errorf("Expected lowest cost 3, got %d", cost)
	}
}

func TestPathfinder_InvalidInput(t *testing.T) {
	pf := NewPathfinder(2)
	if err := pf.Update("add", 0, 1, -1); err == nil {
		t.Error("Expected error for negative cost")
	}
	if err := pf.Update("invalid", 0, 1, 1); err == nil {
		t.Error("Expected error for invalid operation")
	}
	if cost := pf.Query(2, 0); cost != -1 {
		t.Error("Expected -1 for invalid node ID")
	}
}

func TestPathfinder_ConcurrentAccess(t *testing.T) {
	pf := NewPathfinder(100)
	var wg sync.WaitGroup

	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			pf.Update("add", id, id+1, int64(id+1))
		}(i)
	}

	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			pf.Query(id, id+1)
		}(i)
	}

	wg.Wait()

	// Verify some paths after concurrent operations
	if cost := pf.Query(0, 50); cost <= 0 {
		t.Errorf("Expected positive cost for long path, got %d", cost)
	}
}

func BenchmarkPathfinder_Updates(b *testing.B) {
	pf := NewPathfinder(1000)
	for i := 0; i < b.N; i++ {
		pf.Update("add", i%1000, (i+1)%1000, int64(i%100+1))
	}
}

func BenchmarkPathfinder_Queries(b *testing.B) {
	pf := NewPathfinder(1000)
	// Pre-populate with some edges
	for i := 0; i < 999; i++ {
		pf.Update("add", i, i+1, 1)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pf.Query(0, 999)
	}
}