package distrotx

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

type mockParticipant struct {
	server        *httptest.Server
	prepareDelay  int
	commitDelay   int
	rollbackDelay int
	prepareError  bool
	commitError   bool
	prepareCalls  int
	commitCalls   int
	rollbackCalls int
	mu            sync.Mutex
}

func newMockParticipant(prepareDelay, commitDelay, rollbackDelay int, prepareError, commitError bool) *mockParticipant {
	mp := &mockParticipant{
		prepareDelay:  prepareDelay,
		commitDelay:   commitDelay,
		rollbackDelay: rollbackDelay,
		prepareError:  prepareError,
		commitError:   commitError,
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/prepare", mp.handlePrepare)
	mux.HandleFunc("/commit", mp.handleCommit)
	mux.HandleFunc("/rollback", mp.handleRollback)

	mp.server = httptest.NewServer(mux)
	return mp
}

func (mp *mockParticipant) handlePrepare(w http.ResponseWriter, r *http.Request) {
	mp.mu.Lock()
	mp.prepareCalls++
	mp.mu.Unlock()

	time.Sleep(time.Duration(mp.prepareDelay) * time.Millisecond)
	if mp.prepareError {
		w.WriteHeader(http.StatusInternalServerError)
		fmt.Fprint(w, "NACK")
		return
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "ACK")
}

func (mp *mockParticipant) handleCommit(w http.ResponseWriter, r *http.Request) {
	mp.mu.Lock()
	mp.commitCalls++
	mp.mu.Unlock()

	time.Sleep(time.Duration(mp.commitDelay) * time.Millisecond)
	if mp.commitError {
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "OK")
}

func (mp *mockParticipant) handleRollback(w http.ResponseWriter, r *http.Request) {
	mp.mu.Lock()
	mp.rollbackCalls++
	mp.mu.Unlock()

	time.Sleep(time.Duration(mp.rollbackDelay) * time.Millisecond)
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "OK")
}

func TestDistributedTransaction(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Setup mock participants
			mocks := make([]*mockParticipant, len(tc.participants))
			coordinator := NewTransactionCoordinator()

			// Create mock servers and register participants
			for i, p := range tc.participants {
				prepareDelay := tc.prepareDelay[p.ServiceURL]
				commitDelay := tc.commitDelay[p.ServiceURL]
				rollbackDelay := tc.rollbackDelay[p.ServiceURL]
				prepareError := tc.prepareError[p.ServiceURL]
				commitError := tc.commitError[p.ServiceURL]

				mock := newMockParticipant(prepareDelay, commitDelay, rollbackDelay, prepareError, commitError)
				mocks[i] = mock
				defer mock.server.Close()

				participant := Participant{
					ServiceURL: mock.server.URL,
					Timeout:    p.Timeout,
				}
				err := coordinator.RegisterParticipant(participant)
				if err != nil {
					if !tc.expectedErr {
						t.Errorf("unexpected error registering participant: %v", err)
					}
					return
				}
			}

			// Execute transaction
			ctx := context.Background()
			err := coordinator.Execute(ctx)

			// Verify results
			if tc.expectedErr && err == nil {
				t.Error("expected error but got none")
			}
			if !tc.expectedErr && err != nil {
				t.Errorf("unexpected error: %v", err)
			}

			// Verify participant calls
			for i, mock := range mocks {
				mock.mu.Lock()
				if mock.prepareCalls == 0 {
					t.Errorf("participant %d: prepare was not called", i)
				}
				if tc.shouldCommit {
					if mock.commitCalls == 0 {
						t.Errorf("participant %d: commit was not called when it should have been", i)
					}
					if mock.rollbackCalls > 0 {
						t.Errorf("participant %d: rollback was called when it shouldn't have been", i)
					}
				} else {
					if mock.commitCalls > 0 {
						t.Errorf("participant %d: commit was called when it shouldn't have been", i)
					}
					if mock.rollbackCalls == 0 && i < len(mocks)-1 { // Last participant might not get rollback in failure case
						t.Errorf("participant %d: rollback was not called when it should have been", i)
					}
				}
				mock.mu.Unlock()
			}
		})
	}
}

func BenchmarkDistributedTransaction(b *testing.B) {
	// Setup a basic successful case
	participant1 := newMockParticipant(0, 0, 0, false, false)
	participant2 := newMockParticipant(0, 0, 0, false, false)
	defer participant1.server.Close()
	defer participant2.server.Close()

	coordinator := NewTransactionCoordinator()
	_ = coordinator.RegisterParticipant(Participant{
		ServiceURL: participant1.server.URL,
		Timeout:    1000,
	})
	_ = coordinator.RegisterParticipant(Participant{
		ServiceURL: participant2.server.URL,
		Timeout:    1000,
	})

	ctx := context.Background()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		_ = coordinator.Execute(ctx)
	}
}