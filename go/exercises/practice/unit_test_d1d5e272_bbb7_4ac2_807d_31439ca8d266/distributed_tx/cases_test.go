package distributedtx

// Test cases for the distributed transaction coordinator
var testCases = []struct {
    description string
    setup       func() []Service
    operations  func(*Coordinator) error
    expected    string
    shouldError bool
}{
    {
        description: "successful transaction across all services",
        setup: func() []Service {
            return []Service{
                NewMockService("user"),
                NewMockService("inventory"),
                NewMockService("payment"),
            }
        },
        operations: func(c *Coordinator) error {
            txID := c.BeginTransaction()
            return c.CommitTransaction(txID)
        },
        expected:    "committed",
        shouldError: false,
    },
    {
        description: "rollback when one service fails prepare",
        setup: func() []Service {
            services := []Service{
                NewMockService("user"),
                NewFailingMockService("inventory"),
                NewMockService("payment"),
            }
            return services
        },
        operations: func(c *Coordinator) error {
            txID := c.BeginTransaction()
            return c.CommitTransaction(txID)
        },
        expected:    "rolledback",
        shouldError: true,
    },
    {
        description: "timeout during prepare phase",
        setup: func() []Service {
            services := []Service{
                NewMockService("user"),
                NewTimeoutMockService("inventory"),
                NewMockService("payment"),
            }
            return services
        },
        operations: func(c *Coordinator) error {
            txID := c.BeginTransaction()
            return c.CommitTransaction(txID)
        },
        expected:    "rolledback",
        shouldError: true,
    },
    {
        description: "concurrent transactions",
        setup: func() []Service {
            return []Service{
                NewMockService("user"),
                NewMockService("inventory"),
                NewMockService("payment"),
            }
        },
        operations: func(c *Coordinator) error {
            var errChan = make(chan error, 5)
            for i := 0; i < 5; i++ {
                go func() {
                    txID := c.BeginTransaction()
                    errChan <- c.CommitTransaction(txID)
                }()
            }
            for i := 0; i < 5; i++ {
                if err := <-errChan; err != nil {
                    return err
                }
            }
            return nil
        },
        expected:    "committed",
        shouldError: false,
    },
}