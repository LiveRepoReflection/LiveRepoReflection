package distributedtx

import (
    "errors"
    "sync"
    "testing"
    "time"
)

type MockService struct {
    name      string
    state     map[TransactionID]string
    mutex     sync.RWMutex
    shouldErr bool
    timeout   bool
}

func NewMockService(name string) *MockService {
    return &MockService{
        name:  name,
        state: make(map[TransactionID]string),
    }
}

func NewFailingMockService(name string) *MockService {
    return &MockService{
        name:      name,
        state:     make(map[TransactionID]string),
        shouldErr: true,
    }
}

func NewTimeoutMockService(name string) *MockService {
    return &MockService{
        name:    name,
        state:   make(map[TransactionID]string),
        timeout: true,
    }
}

func (m *MockService) Prepare(txID TransactionID) error {
    if m.shouldErr {
        return errors.New("prepare failed")
    }
    if m.timeout {
        time.Sleep(2 * time.Second)
    }
    m.mutex.Lock()
    defer m.mutex.Unlock()
    m.state[txID] = "prepared"
    return nil
}

func (m *MockService) Commit(txID TransactionID) error {
    m.mutex.Lock()
    defer m.mutex.Unlock()
    if m.state[txID] != "prepared" {
        return errors.New("not in prepared state")
    }
    m.state[txID] = "committed"
    return nil
}

func (m *MockService) Rollback(txID TransactionID) error {
    m.mutex.Lock()
    defer m.mutex.Unlock()
    m.state[txID] = "rolledback"
    return nil
}

func (m *MockService) GetState(txID TransactionID) string {
    m.mutex.RLock()
    defer m.mutex.RUnlock()
    return m.state[txID]
}

func TestDistributedTx(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            services := tc.setup()
            coordinator := NewCoordinator(services, 1*time.Second)
            
            err := tc.operations(coordinator)
            
            if tc.shouldError && err == nil {
                t.Error("expected error but got none")
            }
            if !tc.shouldError && err != nil {
                t.Errorf("unexpected error: %v", err)
            }

            // Check final state of all services
            for _, svc := range services {
                for txID := int64(1); txID <= 100; txID++ {
                    state := svc.GetState(TransactionID(txID))
                    if state != "" && state != tc.expected {
                        t.Errorf("expected service state %s, got %s", tc.expected, state)
                    }
                }
            }
        })
    }
}

func TestConcurrentTransactions(t *testing.T) {
    services := []Service{
        NewMockService("user"),
        NewMockService("inventory"),
        NewMockService("payment"),
    }
    coordinator := NewCoordinator(services, 1*time.Second)

    var wg sync.WaitGroup
    numTx := 10

    for i := 0; i < numTx; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            txID := coordinator.BeginTransaction()
            err := coordinator.CommitTransaction(txID)
            if err != nil {
                t.Errorf("unexpected error in concurrent transaction: %v", err)
            }
        }()
    }

    wg.Wait()
}

func TestTimeout(t *testing.T) {
    services := []Service{
        NewMockService("user"),
        NewTimeoutMockService("inventory"),
        NewMockService("payment"),
    }
    coordinator := NewCoordinator(services, 500*time.Millisecond)

    txID := coordinator.BeginTransaction()
    err := coordinator.CommitTransaction(txID)
    
    if err == nil {
        t.Error("expected timeout error but got none")
    }

    // Check that all services were rolled back
    for _, svc := range services {
        state := svc.GetState(txID)
        if state != "rolledback" {
            t.Errorf("expected service state rolledback, got %s", state)
        }
    }
}

func BenchmarkTransaction(b *testing.B) {
    services := []Service{
        NewMockService("user"),
        NewMockService("inventory"),
        NewMockService("payment"),
    }
    coordinator := NewCoordinator(services, 1*time.Second)

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        txID := coordinator.BeginTransaction()
        _ = coordinator.CommitTransaction(txID)
    }
}