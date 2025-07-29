package packetrouter

var testCases = []struct {
    description     string
    routingTable   []string
    testAddresses  []testAddress
}{
    {
        description: "basic routing with single entry",
        routingTable: []string{
            "192.168.1.0/24 1",
        },
        testAddresses: []testAddress{
            {ip: "192.168.1.5", expectedInterface: 1},
            {ip: "192.168.2.1", expectedInterface: -1},
        },
    },
    {
        description: "multiple non-overlapping entries",
        routingTable: []string{
            "192.168.1.0/24 1",
            "10.0.0.0/8 2",
            "172.16.0.0/12 3",
        },
        testAddresses: []testAddress{
            {ip: "192.168.1.100", expectedInterface: 1},
            {ip: "10.1.1.1", expectedInterface: 2},
            {ip: "172.16.5.5", expectedInterface: 3},
            {ip: "8.8.8.8", expectedInterface: -1},
        },
    },
    {
        description: "overlapping prefixes",
        routingTable: []string{
            "10.0.0.0/8 1",
            "10.1.0.0/16 2",
            "10.1.1.0/24 3",
        },
        testAddresses: []testAddress{
            {ip: "10.1.1.1", expectedInterface: 3},
            {ip: "10.1.2.1", expectedInterface: 2},
            {ip: "10.2.1.1", expectedInterface: 1},
        },
    },
    {
        description: "empty routing table",
        routingTable: []string{},
        testAddresses: []testAddress{
            {ip: "192.168.1.1", expectedInterface: -1},
        },
    },
    {
        description: "default route",
        routingTable: []string{
            "0.0.0.0/0 1",
            "192.168.0.0/16 2",
        },
        testAddresses: []testAddress{
            {ip: "192.168.1.1", expectedInterface: 2},
            {ip: "8.8.8.8", expectedInterface: 1},
        },
    },
    {
        description: "complex overlapping prefixes",
        routingTable: []string{
            "0.0.0.0/0 1",
            "192.168.0.0/16 2",
            "192.168.1.0/24 3",
            "192.168.1.128/25 4",
        },
        testAddresses: []testAddress{
            {ip: "192.168.1.200", expectedInterface: 4},
            {ip: "192.168.1.100", expectedInterface: 3},
            {ip: "192.168.2.1", expectedInterface: 2},
            {ip: "172.16.1.1", expectedInterface: 1},
        },
    },
}

type testAddress struct {
    ip               string
    expectedInterface int
}