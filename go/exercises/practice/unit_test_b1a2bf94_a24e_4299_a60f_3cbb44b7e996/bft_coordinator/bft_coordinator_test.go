package bft_coordinator

import (
	"testing"
	"time"
	"math/rand"
	"sync"
)

type mockParticipant struct {
	id        int
	isFaulty  bool
	responses map[int]bool // track responses to detect inconsistencies
	lock      sync.Mutex
}

func (m *mockParticipant) receivePrePrepare(txID int, commit bool) bool {
	m.lock.Lock()
	defer m.lock.Unlock()

	if m.isFaulty {
		// Byzantine behavior: randomly lie about the decision
		if rand.Intn(2) == 0 {
			return !commit
		}
	}
	m.responses[txID] = commit
	return commit
}

func TestBFTWithNoFaults(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	n := 4 // 3f+1 where f=1
	f := 1
	participants := make([]*mockParticipant, n)

	for i := 0; i < n; i++ {
		participants[i] = &mockParticipant{
			id:        i,
			isFaulty:  false,
			responses: make(map[int]bool),
		}
	}

	txID := 1
	coordinator := NewCoordinator(n, f)
	coordinator.StartTransaction(txID, true) // propose commit

	// Simulate message passing
	var wg sync.WaitGroup
	for _, p := range participants {
		wg.Add(1)
		go func(part *mockParticipant) {
			defer wg.Done()
			coordinator.ReceiveVote(txID, part.id, part.receivePrePrepare(txID, true))
		}(p)
	}
	wg.Wait()

	// Verify all honest participants agreed
	for _, p := range participants {
		if p.isFaulty {
			continue
		}
		if resp, ok := p.responses[txID]; !ok || !resp {
			t.Errorf("Honest participant %d did not commit", p.id)
		}
	}
}

func TestBFTWithFaults(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	n := 4 // 3f+1 where f=1
	f := 1
	participants := make([]*mockParticipant, n)

	// Mark one participant as faulty
	for i := 0; i < n; i++ {
		participants[i] = &mockParticipant{
			id:        i,
			isFaulty:  i == 0, // first participant is faulty
			responses: make(map[int]bool),
		}
	}

	txID := 1
	coordinator := NewCoordinator(n, f)
	coordinator.StartTransaction(txID, true) // propose commit

	// Simulate message passing with one faulty participant
	var wg sync.WaitGroup
	for _, p := range participants {
		wg.Add(1)
		go func(part *mockParticipant) {
			defer wg.Done()
			// Faulty participant may lie about the decision
			vote := part.receivePrePrepare(txID, true)
			coordinator.ReceiveVote(txID, part.id, vote)
		}(p)
	}
	wg.Wait()

	// Verify consensus despite faulty participant
	honestCommits := 0
	for _, p := range participants {
		if p.isFaulty {
			continue
		}
		if resp, ok := p.responses[txID]; ok && resp {
			honestCommits++
		}
	}

	if honestCommits < n-f {
		t.Errorf("Not enough honest participants committed: got %d, need at least %d", 
			honestCommits, n-f)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	n := 4
	f := 1
	participants := make([]*mockParticipant, n)

	for i := 0; i < n; i++ {
		participants[i] = &mockParticipant{
			id:        i,
			isFaulty:  false,
			responses: make(map[int]bool),
		}
	}

	coordinator := NewCoordinator(n, f)
	txIDs := []int{1, 2, 3}

	var wg sync.WaitGroup
	for _, txID := range txIDs {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			coordinator.StartTransaction(id, id%2 == 0) // alternate commit/abort

			for _, p := range participants {
				coordinator.ReceiveVote(id, p.id, p.receivePrePrepare(id, id%2 == 0))
			}
		}(txID)
	}
	wg.Wait()

	// Verify each transaction was handled correctly
	for _, txID := range txIDs {
		expected := txID%2 == 0
		for _, p := range participants {
			if resp, ok := p.responses[txID]; !ok || resp != expected {
				t.Errorf("Transaction %d: participant %d response %v, expected %v",
					txID, p.id, resp, expected)
			}
		}
	}
}