package dist_tx_coord

import (
	"errors"
	"testing"
	"time"
)

type mockService struct {
	name           string
	prepareErr     error
	commitErr      error
	prepareDelay   time.Duration
	commitDelay    time.Duration
	prepared       bool
	committed      bool
	rolledBack     bool
}

func (m *mockService) Prepare() error {
	time.Sleep(m.prepareDelay)
	m.prepared = true
	return m.prepareErr
}

func (m *mockService) CommitRollback(commit bool) error {
	time.Sleep(m.commitDelay)
	if commit {
		m.committed = true
		return m.commitErr
	}
	m.rolledBack = true
	return m.commitErr
}

func (m *mockService) GetName() string {
	return m.name
}

func TestTransactionCoordinator(t *testing.T) {
	t.Run("successful transaction", func(t *testing.T) {
		tc := NewTransactionCoordinator(10, 100)
		txID := tc.Begin()

		services := []Service{
			&mockService{name: "Inventory", prepareDelay: 50 * time.Millisecond},
			&mockService{name: "Payment", prepareDelay: 30 * time.Millisecond},
			&mockService{name: "Shipping", prepareDelay: 20 * time.Millisecond},
		}

		for _, svc := range services {
			if err := tc.Register(txID, svc); err != nil {
				t.Fatalf("Register failed: %v", err)
			}
		}

		if err := tc.End(txID, true); err != nil {
			t.Errorf("End failed: %v", err)
		}

		for _, svc := range services {
			mock := svc.(*mockService)
			if !mock.prepared {
				t.Errorf("%s was not prepared", mock.name)
			}
			if !mock.committed {
				t.Errorf("%s was not committed", mock.name)
			}
		}
	})

	t.Run("failed prepare phase", func(t *testing.T) {
		tc := NewTransactionCoordinator(10, 100)
		txID := tc.Begin()

		services := []Service{
			&mockService{name: "Inventory", prepareDelay: 50 * time.Millisecond},
			&mockService{name: "Payment", prepareDelay: 30 * time.Millisecond, prepareErr: errors.New("insufficient funds")},
			&mockService{name: "Shipping", prepareDelay: 20 * time.Millisecond},
		}

		for _, svc := range services {
			if err := tc.Register(txID, svc); err != nil {
				t.Fatalf("Register failed: %v", err)
			}
		}

		err := tc.End(txID, true)
		if err == nil {
			t.Error("Expected error but got none")
		}

		for _, svc := range services {
			mock := svc.(*mockService)
			if mock.name != "Payment" && !mock.prepared {
				t.Errorf("%s was not prepared", mock.name)
			}
			if mock.committed {
				t.Errorf("%s was committed but shouldn't be", mock.name)
			}
			if mock.name != "Payment" && !mock.rolledBack {
				t.Errorf("%s was not rolled back", mock.name)
			}
		}
	})

	t.Run("timeout during prepare", func(t *testing.T) {
		tc := NewTransactionCoordinator(10, 100)
		txID := tc.Begin()

		services := []Service{
			&mockService{name: "Inventory", prepareDelay: 600 * time.Millisecond},
			&mockService{name: "Payment", prepareDelay: 30 * time.Millisecond},
			&mockService{name: "Shipping", prepareDelay: 20 * time.Millisecond},
		}

		for _, svc := range services {
			if err := tc.Register(txID, svc); err != nil {
				t.Fatalf("Register failed: %v", err)
			}
		}

		err := tc.End(txID, true)
		if err == nil {
			t.Error("Expected timeout error but got none")
		}

		for _, svc := range services {
			mock := svc.(*mockService)
			if mock.name == "Inventory" && mock.prepared {
				t.Errorf("Inventory should have timed out before preparing")
			}
			if mock.committed {
				t.Errorf("%s was committed but shouldn't be", mock.name)
			}
		}
	})

	t.Run("concurrent transactions", func(t *testing.T) {
		tc := NewTransactionCoordinator(10, 100)
		var txIDs []TransactionID

		// Start 5 concurrent transactions
		for i := 0; i < 5; i++ {
			txID := tc.Begin()
			txIDs = append(txIDs, txID)

			services := []Service{
				&mockService{name: "Inventory", prepareDelay: time.Duration(i*10) * time.Millisecond},
				&mockService{name: "Payment", prepareDelay: time.Duration(i*5) * time.Millisecond},
			}

			for _, svc := range services {
				if err := tc.Register(txID, svc); err != nil {
					t.Fatalf("Register failed: %v", err)
				}
			}
		}

		// Commit all transactions
		for _, txID := range txIDs {
			if err := tc.End(txID, true); err != nil {
				t.Errorf("End failed for tx %v: %v", txID, err)
			}
		}
	})

	t.Run("register after end", func(t *testing.T) {
		tc := NewTransactionCoordinator(10, 100)
		txID := tc.Begin()

		svc := &mockService{name: "Inventory"}
		if err := tc.Register(txID, svc); err != nil {
			t.Fatalf("Initial register failed: %v", err)
		}

		if err := tc.End(txID, true); err != nil {
			t.Fatalf("End failed: %v", err)
		}

		err := tc.Register(txID, &mockService{name: "LateService"})
		if err == nil {
			t.Error("Expected error when registering after end but got none")
		}
	})
}