package packetrouter

import (
    "testing"
)

func TestPacketRouter(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            router, err := NewRouter(tc.routingTable)
            if err != nil {
                t.Fatalf("Failed to create router: %v", err)
            }

            for _, addr := range tc.testAddresses {
                result, err := router.Route(addr.ip)
                if err != nil {
                    t.Errorf("Unexpected error routing %s: %v", addr.ip, err)
                    continue
                }
                if result != addr.expectedInterface {
                    t.Errorf("For IP %s, expected interface %d, but got %d",
                        addr.ip, addr.expectedInterface, result)
                }
            }
        })
    }
}

func TestInvalidInputs(t *testing.T) {
    invalidCases := []struct {
        description string
        table      []string
        shouldFail bool
    }{
        {
            description: "invalid CIDR notation",
            table:      []string{"192.168.1.0/33 1"},
            shouldFail: true,
        },
        {
            description: "invalid IP address",
            table:      []string{"256.168.1.0/24 1"},
            shouldFail: true,
        },
        {
            description: "malformed entry",
            table:      []string{"192.168.1.0/24"},
            shouldFail: true,
        },
        {
            description: "negative interface number",
            table:      []string{"192.168.1.0/24 -1"},
            shouldFail: true,
        },
    }

    for _, tc := range invalidCases {
        t.Run(tc.description, func(t *testing.T) {
            _, err := NewRouter(tc.table)
            if tc.shouldFail && err == nil {
                t.Error("Expected error but got none")
            }
            if !tc.shouldFail && err != nil {
                t.Errorf("Unexpected error: %v", err)
            }
        })
    }
}

func BenchmarkRouterCreation(b *testing.B) {
    // Use a moderate-sized routing table for benchmarking
    table := []string{
        "192.168.0.0/16 1",
        "10.0.0.0/8 2",
        "172.16.0.0/12 3",
        "192.168.1.0/24 4",
        "10.10.0.0/16 5",
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        _, err := NewRouter(table)
        if err != nil {
            b.Fatalf("Failed to create router: %v", err)
        }
    }
}

func BenchmarkIPLookup(b *testing.B) {
    table := []string{
        "192.168.0.0/16 1",
        "10.0.0.0/8 2",
        "172.16.0.0/12 3",
        "192.168.1.0/24 4",
        "10.10.0.0/16 5",
    }

    router, err := NewRouter(table)
    if err != nil {
        b.Fatalf("Failed to create router: %v", err)
    }

    testIPs := []string{
        "192.168.1.100",
        "10.10.1.1",
        "172.16.5.5",
        "8.8.8.8",
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        for _, ip := range testIPs {
            _, err := router.Route(ip)
            if err != nil {
                b.Fatalf("Failed to route IP %s: %v", ip, err)
            }
        }
    }
}