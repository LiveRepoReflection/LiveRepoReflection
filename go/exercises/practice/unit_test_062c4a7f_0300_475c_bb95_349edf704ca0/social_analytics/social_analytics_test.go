package social_analytics

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// Assuming that the solution implements a SocialGraph structure with the following methods:
//
// NewSocialGraph() *SocialGraph
// IngestUser(userID int, metadata string) error
// IngestConnection(userID1, userID2 int) error
// GetDegreeDistribution() map[int]int
// GetConnectedComponents() int
// GetPersonalizedPageRank(sourceUserID int, k int) ([]UserPageRank, error)
//
// And a UserPageRank struct defined as:
// type UserPageRank struct {
//     UserID int
//     Score  float64
// }

func createTestGraph() *SocialGraph {
	graph := NewSocialGraph()
	// Ingest users - for testing assume IDs 1 to 5.
	for i := 1; i <= 5; i++ {
		err := graph.IngestUser(i, "user_metadata")
		if err != nil {
			panic("failed to ingest user in test setup")
		}
	}
	// Create connections grouped in two distinct components:
	// Component 1: 1, 2, 3 (forming a triangle)
	graph.IngestConnection(1, 2)
	graph.IngestConnection(2, 3)
	graph.IngestConnection(1, 3)
	// Component 2: 4, 5 (a single connection)
	graph.IngestConnection(4, 5)
	return graph
}

func TestIngestion(t *testing.T) {
	graph := NewSocialGraph()

	// Test adding new users
	if err := graph.IngestUser(10, "Alice"); err != nil {
		t.Fatalf("Unexpected error ingesting user 10: %v", err)
	}
	if err := graph.IngestUser(20, "Bob"); err != nil {
		t.Fatalf("Unexpected error ingesting user 20: %v", err)
	}

	// Test duplicate user ingestion: Assuming duplicate users return an error
	err := graph.IngestUser(10, "Alice_duplicate")
	if err == nil {
		t.Errorf("Expected error when ingesting duplicate user, got nil")
	}

	// Test adding connection with non-existent user (e.g. user 30 not added)
	err = graph.IngestConnection(10, 30)
	if err == nil {
		t.Errorf("Expected error when connecting to non-existent user, got nil")
	}

	// Add missing user and then connection
	if err := graph.IngestUser(30, "Charlie"); err != nil {
		t.Fatalf("Unexpected error ingesting user 30: %v", err)
	}
	if err := graph.IngestConnection(10, 30); err != nil {
		t.Fatalf("Unexpected error ingesting connection (10, 30): %v", err)
	}

	// Test duplicate connection; it should be handled gracefully.
	if err := graph.IngestConnection(10, 30); err != nil {
		t.Errorf("Unexpected error when ingesting duplicate connection (10, 30): %v", err)
	}
}

func TestDegreeDistribution(t *testing.T) {
	graph := createTestGraph()
	// Expected degrees:
	// Component 1: user1:2, user2:2, user3:2  (each is connected twice due to triangle)
	// Component 2: user4:1, user5:1
	expected := map[int]int{
		1: 2, // two nodes with degree 1
		2: 3, // three nodes with degree 2
	}
	degreeDist := graph.GetDegreeDistribution()

	// Count frequencies from degreeDist
	freq := make(map[int]int)
	for _, d := range degreeDist {
		freq[d]++
	}
	// Validate expected frequency
	for deg, count := range expected {
		if freq[deg] != count {
			t.Errorf("Expected %d nodes with degree %d; got %d", count, deg, freq[deg])
		}
	}
	// Ensure no unexpected degrees exist
	for deg := range freq {
		if _, found := expected[deg]; !found {
			t.Errorf("Unexpected degree %d found in distribution", deg)
		}
	}
}

func TestConnectedComponents(t *testing.T) {
	graph := createTestGraph()
	// In our test graph we expect 2 connected components.
	compCount := graph.GetConnectedComponents()
	if compCount != 2 {
		t.Fatalf("Expected 2 connected components; got %d", compCount)
	}

	// Add an isolated user
	if err := graph.IngestUser(6, "isolated"); err != nil {
		t.Fatalf("Error ingesting isolated user: %v", err)
	}
	compCount = graph.GetConnectedComponents()
	if compCount != 3 {
		t.Errorf("After adding an isolated node, expected 3 connected components; got %d", compCount)
	}
}

func TestPersonalizedPageRank(t *testing.T) {
	graph := createTestGraph()

	// Test with valid source and k value.
	ranks, err := graph.GetPersonalizedPageRank(1, 2)
	if err != nil {
		t.Fatalf("Unexpected error in PersonalizedPageRank for valid source: %v", err)
	}
	if len(ranks) != 2 {
		t.Errorf("Expected top 2 results, got %d", len(ranks))
	}

	// Ensure that the source is in the result or that the highest score is the source.
	foundSource := false
	for _, r := range ranks {
		if r.UserID == 1 {
			foundSource = true
		}
	}
	if !foundSource {
		t.Errorf("Expected source user (1) to appear in top PageRank results")
	}

	// Test with invalid source user (non-existent)
	_, err = graph.GetPersonalizedPageRank(9999, 3)
	if err == nil {
		t.Errorf("Expected error for non-existent source user, got nil")
	}
}

func TestConcurrentOperations(t *testing.T) {
	graph := NewSocialGraph()
	var wg sync.WaitGroup

	// Concurrently ingest users.
	userCount := 100
	wg.Add(userCount)
	for i := 1; i <= userCount; i++ {
		go func(id int) {
			defer wg.Done()
			if err := graph.IngestUser(id, "metadata"); err != nil && !errors.Is(err, ErrUserAlreadyExists) {
				t.Errorf("Error ingesting user %d concurrently: %v", id, err)
			}
		}(i)
	}
	wg.Wait()

	// Concurrently ingest connections.
	connCount := 50
	wg.Add(connCount)
	for i := 1; i <= connCount; i++ {
		go func(i int) {
			defer wg.Done()
			// Connect user i and i+1 if within bounds
			if i < userCount {
				if err := graph.IngestConnection(i, i+1); err != nil {
					t.Errorf("Error ingesting connection (%d, %d): %v", i, i+1, err)
				}
			}
		}(i)
	}
	wg.Wait()

	// Give the ingestion some time to settle if needed (simulate real-time updates).
	time.Sleep(100 * time.Millisecond)

	// Concurrently query degree distribution, connected components, and personalized PageRank.
	queryFuncs := []func(){
		func() {
			_ = graph.GetDegreeDistribution()
		},
		func() {
			_ = graph.GetConnectedComponents()
		},
		func() {
			_, _ = graph.GetPersonalizedPageRank(1, 5)
		},
	}
	wg.Add(len(queryFuncs) * 10)
	for i := 0; i < 10; i++ {
		for _, qf := range queryFuncs {
			go func(f func()) {
				defer wg.Done()
				f()
			}(qf)
		}
	}
	wg.Wait()
}