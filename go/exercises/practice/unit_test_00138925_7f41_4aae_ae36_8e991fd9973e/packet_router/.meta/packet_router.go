package packetrouter

import (
    "fmt"
    "net"
    "strconv"
    "strings"
)

// Node represents a node in the binary trie
type Node struct {
    left     *Node         // 0
    right    *Node        // 1
    iface    int          // interface number, -1 if not a match
    isPrefix bool         // indicates if this node represents a prefix
}

// Router represents the packet router
type Router struct {
    root *Node
}

// NewRouter creates a new Router instance with the given routing table
func NewRouter(table []string) (*Router, error) {
    router := &Router{
        root: &Node{iface: -1},
    }

    // Process each entry in the routing table
    for _, entry := range table {
        parts := strings.Fields(entry)
        if len(parts) != 2 {
            return nil, fmt.Errorf("invalid routing table entry: %s", entry)
        }

        // Parse interface number
        iface, err := strconv.Atoi(parts[1])
        if err != nil || iface < 0 {
            return nil, fmt.Errorf("invalid interface number: %s", parts[1])
        }

        // Parse CIDR notation
        _, ipNet, err := net.ParseCIDR(parts[0])
        if err != nil {
            return nil, fmt.Errorf("invalid CIDR notation: %s", parts[0])
        }

        // Insert the route into the trie
        err = router.insertRoute(ipNet, iface)
        if err != nil {
            return nil, err
        }
    }

    return router, nil
}

// insertRoute inserts a route into the trie
func (r *Router) insertRoute(ipNet *net.IPNet, iface int) error {
    ones, bits := ipNet.Mask.Size()
    if bits != 32 || ones > 32 {
        return fmt.Errorf("invalid prefix length: %d", ones)
    }

    ip := ipToUint32(ipNet.IP)
    current := r.root

    // Navigate the trie based on the IP address bits
    for i := 0; i < ones; i++ {
        bit := (ip >> (31 - i)) & 1

        if bit == 0 {
            if current.left == nil {
                current.left = &Node{iface: -1}
            }
            current = current.left
        } else {
            if current.right == nil {
                current.right = &Node{iface: -1}
            }
            current = current.right
        }
    }

    // Mark the node as a prefix and store the interface
    current.isPrefix = true
    current.iface = iface
    return nil
}

// Route finds the best matching route for the given IP address
func (r *Router) Route(ipStr string) (int, error) {
    ip := net.ParseIP(ipStr)
    if ip == nil {
        return -1, fmt.Errorf("invalid IP address: %s", ipStr)
    }
    ip = ip.To4()
    if ip == nil {
        return -1, fmt.Errorf("not an IPv4 address: %s", ipStr)
    }

    ipInt := ipToUint32(ip)
    bestMatch := -1
    current := r.root

    // Traverse the trie to find the longest matching prefix
    for i := 0; i < 32 && current != nil; i++ {
        if current.isPrefix {
            bestMatch = current.iface
        }

        bit := (ipInt >> (31 - i)) & 1
        if bit == 0 {
            current = current.left
        } else {
            current = current.right
        }
    }

    return bestMatch, nil
}

// ipToUint32 converts an IP address to a uint32
func ipToUint32(ip net.IP) uint32 {
    ip = ip.To4()
    return uint32(ip[0])<<24 | uint32(ip[1])<<16 | uint32(ip[2])<<8 | uint32(ip[3])
}