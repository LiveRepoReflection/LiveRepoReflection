package auto_navigate

import (
	"reflect"
	"sync"
	"testing"
	"time"
)

// Assume that the implementation provides the following:
//
// type GraphNavigator struct { ... }
//
// func NewGraphNavigator(initialEdges [][]string, source, destination string) *GraphNavigator
// func (gn *GraphNavigator) ProcessEvent(event []string) error
// func (gn *GraphNavigator) ShortestPath() ([]string, error)
//
// The tests below are built against the expected behavior from the problem description.

func setupNavigator() *GraphNavigator {
	initialEdges := [][]string{
		{"A", "B", "10"},
		{"B", "C", "15"},
		{"A", "C", "50"},
	}
	return NewGraphNavigator(initialEdges, "A", "C")
}

func TestInitialPath(t *testing.T) {
	gn := setupNavigator()
	path, err := gn.ShortestPath()
	expected := []string{"A", "B", "C"}
	if err != nil {
		t.Errorf("Expected valid path, got error: %v", err)
	}
	if !reflect.DeepEqual(path, expected) {
		t.Errorf("Expected path %v, got %v", expected, path)
	}
}

func TestBlockEdge(t *testing.T) {
	gn := setupNavigator()
	err := gn.ProcessEvent([]string{"BlockEdge", "A", "B"})
	if err != nil {
		t.Errorf("Error processing event: %v", err)
	}
	path, err := gn.ShortestPath()
	expected := []string{"A", "C"}
	if err != nil {
		t.Errorf("Expected valid path after blocking edge, got error: %v", err)
	}
	if !reflect.DeepEqual(path, expected) {
		t.Errorf("Expected path %v, got %v", expected, path)
	}
}

func TestUnblockEdge(t *testing.T) {
	gn := setupNavigator()
	// Block edge A->B first.
	err := gn.ProcessEvent([]string{"BlockEdge", "A", "B"})
	if err != nil {
		t.Errorf("Error processing block event: %v", err)
	}
	// Unblock edge A->B with updated weight.
	err = gn.ProcessEvent([]string{"UnblockEdge", "A", "B", "20"})
	if err != nil {
		t.Errorf("Error processing unblock event: %v", err)
	}
	path, err := gn.ShortestPath()
	expected := []string{"A", "B", "C"}
	if err != nil {
		t.Errorf("Expected valid path after unblocking edge, got error: %v", err)
	}
	if !reflect.DeepEqual(path, expected) {
		t.Errorf("Expected path %v, got %v", expected, path)
	}
}

func TestAddEdge(t *testing.T) {
	gn := setupNavigator()
	// Add edge A->D and D->C to create a new potential path.
	err := gn.ProcessEvent([]string{"AddEdge", "A", "D", "5"})
	if err != nil {
		t.Errorf("Error processing add edge event: %v", err)
	}
	err = gn.ProcessEvent([]string{"AddEdge", "D", "C", "5"})
	if err != nil {
		t.Errorf("Error processing add edge event: %v", err)
	}
	path, err := gn.ShortestPath()
	expected := []string{"A", "D", "C"}
	if err != nil {
		t.Errorf("Expected valid path after adding edges, got error: %v", err)
	}
	if !reflect.DeepEqual(path, expected) {
		t.Errorf("Expected path %v, got %v", expected, path)
	}
}

func TestNonExistentRoute(t *testing.T) {
	gn := setupNavigator()
	// Block all possible routes.
	err := gn.ProcessEvent([]string{"BlockEdge", "A", "B"})
	if err != nil {
		t.Errorf("Error processing block event: %v", err)
	}
	err = gn.ProcessEvent([]string{"BlockEdge", "A", "C"})
	if err != nil {
		t.Errorf("Error processing block event: %v", err)
	}
	_, err = gn.ShortestPath()
	if err == nil {
		t.Errorf("Expected error when no path exists, but got valid path")
	}
}

func TestInvalidNodes(t *testing.T) {
	gn := setupNavigator()
	// Process event with non-existent nodes.
	err := gn.ProcessEvent([]string{"BlockEdge", "X", "Y"})
	if err == nil {
		t.Errorf("Expected error when processing event with non-existent nodes")
	}
}

func TestDuplicateEvents(t *testing.T) {
	gn := setupNavigator()
	// Process duplicate BlockEdge events.
	err := gn.ProcessEvent([]string{"BlockEdge", "A", "B"})
	if err != nil {
		t.Errorf("Error processing first block event: %v", err)
	}
	err = gn.ProcessEvent([]string{"BlockEdge", "A", "B"})
	if err != nil {
		t.Errorf("Error processing duplicate block event: %v", err)
	}
	path, err := gn.ShortestPath()
	expected := []string{"A", "C"}
	if err != nil {
		t.Errorf("Expected valid path after duplicate block events, got error: %v", err)
	}
	if !reflect.DeepEqual(path, expected) {
		t.Errorf("Expected path %v, got %v", expected, path)
	}
}

func TestConcurrency(t *testing.T) {
	gn := setupNavigator()
	var wg sync.WaitGroup
	events := [][]string{
		{"BlockEdge", "A", "B"},
		{"AddEdge", "A", "D", "5"},
		{"AddEdge", "D", "C", "5"},
		{"UnblockEdge", "A", "B", "20"},
	}
	for _, event := range events {
		wg.Add(1)
		go func(ev []string) {
			defer wg.Done()
			if err := gn.ProcessEvent(ev); err != nil {
				t.Errorf("Concurrent event processing error: %v", err)
			}
		}(event)
	}
	wg.Wait()

	// Allow slight delay for concurrent processes to finalize.
	time.Sleep(50 * time.Millisecond)

	path, err := gn.ShortestPath()
	if err != nil {
		t.Errorf("Expected valid path in concurrent scenario, got error: %v", err)
	}
	// Valid paths can be either A->B->C or A->D->C depending on event processing order.
	validPaths := [][]string{
		{"A", "B", "C"},
		{"A", "D", "C"},
	}
	valid := false
	for _, vp := range validPaths {
		if reflect.DeepEqual(path, vp) {
			valid = true
			break
		}
	}
	if !valid {
		t.Errorf("Expected path to be one of %v, got %v", validPaths, path)
	}
}