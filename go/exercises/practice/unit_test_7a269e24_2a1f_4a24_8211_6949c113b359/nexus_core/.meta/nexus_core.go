package nexus

import (
    "bufio"
    "errors"
    "fmt"
    "io"
    "sort"
    "strconv"
    "strings"
)

var (
    ErrInvalidK     = errors.New("k must be non-negative")
    ErrInvalidInput = errors.New("invalid input format")
)

// Node represents a user in the social network
type Node struct {
    id       int
    degree   int
    friends  map[int]bool
    removed  bool
}

// FindKCore processes the network data stream and returns the k-core decomposition
func FindKCore(reader io.Reader, k int) ([]int, error) {
    if k < 0 {
        return nil, ErrInvalidK
    }

    // Initialize data structures
    nodes := make(map[int]*Node)
    scanner := bufio.NewScanner(reader)

    // First pass: Build the graph
    for scanner.Scan() {
        line := scanner.Text()
        if err := processLine(line, nodes); err != nil {
            return nil, err
        }
    }

    if err := scanner.Err(); err != nil {
        return nil, err
    }

    // Second pass: Compute k-core
    return computeKCore(nodes, k), nil
}

// processLine parses a line of input and updates the graph
func processLine(line string, nodes map[int]*Node) error {
    parts := strings.Split(line, ":")
    if len(parts) != 2 {
        return ErrInvalidInput
    }

    // Parse user ID
    userID, err := strconv.Atoi(strings.TrimSpace(parts[0]))
    if err != nil {
        return fmt.Errorf("invalid user ID: %w", err)
    }

    // Create or get the user node
    if _, exists := nodes[userID]; !exists {
        nodes[userID] = &Node{
            id:      userID,
            friends: make(map[int]bool),
        }
    }

    // Process friends
    if len(strings.TrimSpace(parts[1])) > 0 {
        friendIDs := strings.Split(parts[1], ",")
        for _, friendID := range friendIDs {
            fID, err := strconv.Atoi(strings.TrimSpace(friendID))
            if err != nil {
                return fmt.Errorf("invalid friend ID: %w", err)
            }

            // Create friend node if it doesn't exist
            if _, exists := nodes[fID]; !exists {
                nodes[fID] = &Node{
                    id:      fID,
                    friends: make(map[int]bool),
                }
            }

            // Add bidirectional friendship
            if !nodes[userID].friends[fID] {
                nodes[userID].friends[fID] = true
                nodes[userID].degree++
                nodes[fID].friends[userID] = true
                nodes[fID].degree++
            }
        }
    }

    return nil
}

// computeKCore finds the k-core of the graph using an iterative algorithm
func computeKCore(nodes map[int]*Node, k int) []int {
    // Create a queue for nodes to process
    queue := make([]*Node, 0)

    // Initial pass: identify nodes with degree < k
    for _, node := range nodes {
        if node.degree < k {
            queue = append(queue, node)
        }
    }

    // Process queue
    for len(queue) > 0 {
        node := queue[0]
        queue = queue[1:]

        if node.removed {
            continue
        }

        // Remove this node
        node.removed = true

        // Update neighbors
        for friendID := range node.friends {
            friend := nodes[friendID]
            if !friend.removed {
                friend.degree--
                if friend.degree < k {
                    queue = append(queue, friend)
                }
            }
        }
    }

    // Collect remaining nodes (k-core)
    result := make([]int, 0)
    for _, node := range nodes {
        if !node.removed {
            result = append(result, node.id)
        }
    }

    // Sort results
    sort.Ints(result)
    return result
}