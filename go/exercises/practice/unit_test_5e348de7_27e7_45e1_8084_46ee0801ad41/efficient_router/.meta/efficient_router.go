// Package efficient_router implements a high-performance IP router
// that uses longest prefix matching and metric-based tiebreaking
package efficient_router

import (
	"errors"
	"fmt"
	"net"
	"sort"
	"strconv"
	"strings"
)

// Rule represents a routing rule with a prefix, next hop, and metric
type Rule struct {
	Prefix  string // CIDR notation (e.g., "192.168.1.0/24")
	NextHop string // Next hop router IP (e.g., "RouterA")
	Metric  int    // Lower is better
}

// routingRule is an internal representation of a Rule with parsed prefix for faster matching
type routingRule struct {
	ipNet     *net.IPNet // Parsed network prefix
	prefixLen int        // Length of the prefix (e.g., 24 for /24)
	nextHop   string     // Next hop router identifier
	metric    int        // Lower is better
}

// Router implements an efficient IP router
type Router struct {
	rules       []routingRule // Sorted list of routing rules
	trieRoot    *trieNode     // Root of the prefix trie for fast lookup
	initialized bool          // Whether the router has been initialized
}

// trieNode represents a node in the prefix trie
type trieNode struct {
	children  [2]*trieNode  // Binary trie (0 and 1)
	rules     []routingRule // Rules that end at this node
	hasRules  bool          // Whether this node has any rules
}

// NewRouter creates a new router instance
func NewRouter() *Router {
	return &Router{
		rules:    make([]routingRule, 0),
		trieRoot: &trieNode{},
	}
}

// BuildRoutingTable initializes the router with the provided routing rules
func (r *Router) BuildRoutingTable(rules []Rule) error {
	r.rules = make([]routingRule, 0, len(rules))
	r.trieRoot = &trieNode{}

	// Parse all rules
	for _, rule := range rules {
		// Parse the CIDR notation
		_, ipNet, err := net.ParseCIDR(rule.Prefix)
		if err != nil {
			return fmt.Errorf("invalid prefix %s: %v", rule.Prefix, err)
		}

		// Extract prefix length from CIDR notation
		prefixLen, err := getPrefixLength(rule.Prefix)
		if err != nil {
			return err
		}

		// Add rule to our list
		r.rules = append(r.rules, routingRule{
			ipNet:     ipNet,
			prefixLen: prefixLen,
			nextHop:   rule.NextHop,
			metric:    rule.Metric,
		})
	}

	// Sort rules by prefix length (descending) and metric (ascending)
	sort.Slice(r.rules, func(i, j int) bool {
		if r.rules[i].prefixLen != r.rules[j].prefixLen {
			return r.rules[i].prefixLen > r.rules[j].prefixLen // Longest prefix first
		}
		return r.rules[i].metric < r.rules[j].metric // Lower metric first
	})

	// Build the prefix trie for O(1) lookup
	err := r.buildPrefixTrie()
	if err != nil {
		return err
	}

	r.initialized = true
	return nil
}

// buildPrefixTrie constructs a binary trie from the sorted rules
func (r *Router) buildPrefixTrie() error {
	for _, rule := range r.rules {
		// Convert IP to bits
		ipBytes := rule.ipNet.IP.To4()
		if ipBytes == nil {
			return errors.New("IPv6 addresses are not supported")
		}

		// Start at the root node
		node := r.trieRoot

		// Insert the rule into the trie
		for i := 0; i < rule.prefixLen; i++ {
			// Calculate the bit position and value
			byteIndex := i / 8
			bitOffset := 7 - (i % 8)
			bitValue := (ipBytes[byteIndex] >> bitOffset) & 1

			// Create the child node if it doesn't exist
			if node.children[bitValue] == nil {
				node.children[bitValue] = &trieNode{}
			}

			// Move to the next node
			node = node.children[bitValue]
		}

		// Add the rule to this node
		node.rules = append(node.rules, rule)
		node.hasRules = true

		// Sort rules at this node by metric (ascending)
		sort.Slice(node.rules, func(i, j int) bool {
			return node.rules[i].metric < node.rules[j].metric
		})
	}

	return nil
}

// RouteIP determines the next hop for a given IP address
func (r *Router) RouteIP(ipStr string) (string, error) {
	if !r.initialized {
		return "", errors.New("router not initialized, call BuildRoutingTable first")
	}

	// Parse the IP address
	ip := net.ParseIP(ipStr)
	if ip == nil {
		return "", fmt.Errorf("invalid IP address: %s", ipStr)
	}
	ip = ip.To4()
	if ip == nil {
		return "", errors.New("IPv6 addresses are not supported")
	}

	// Use trie-based lookup
	bestRule, found := r.lookupBestMatchingRule(ip)
	if !found {
		return "DROP", nil
	}

	return bestRule.nextHop, nil
}

// lookupBestMatchingRule finds the best matching rule for an IP using the prefix trie
func (r *Router) lookupBestMatchingRule(ip net.IP) (routingRule, bool) {
	node := r.trieRoot
	var bestMatch *routingRule
	
	// Walk the trie as far as possible
	for i := 0; i < 32 && node != nil; i++ {
		// If this node has rules, update the best match
		if node.hasRules {
			bestMatch = &node.rules[0] // First rule has lowest metric due to sorting
		}

		// Calculate the bit position and value
		byteIndex := i / 8
		bitOffset := 7 - (i % 8)
		bitValue := (ip[byteIndex] >> bitOffset) & 1

		// Move to the next node
		node = node.children[bitValue]
	}

	// Check the final node too
	if node != nil && node.hasRules {
		bestMatch = &node.rules[0]
	}

	if bestMatch == nil {
		return routingRule{}, false
	}

	return *bestMatch, true
}

// RouteIPStream routes multiple IP addresses efficiently
func (r *Router) RouteIPStream(ipAddresses []string) ([]string, error) {
	if !r.initialized {
		return nil, errors.New("router not initialized, call BuildRoutingTable first")
	}

	results := make([]string, len(ipAddresses))

	for i, ipStr := range ipAddresses {
		nextHop, err := r.RouteIP(ipStr)
		if err != nil {
			return nil, fmt.Errorf("error routing IP %s: %v", ipStr, err)
		}
		results[i] = nextHop
	}

	return results, nil
}

// getPrefixLength extracts the prefix length from CIDR notation
func getPrefixLength(cidr string) (int, error) {
	parts := strings.Split(cidr, "/")
	if len(parts) != 2 {
		return 0, fmt.Errorf("invalid CIDR notation: %s", cidr)
	}

	prefixLen, err := strconv.Atoi(parts[1])
	if err != nil {
		return 0, fmt.Errorf("invalid prefix length: %s", parts[1])
	}

	// IPv4 prefix length must be between 0 and 32
	if prefixLen < 0 || prefixLen > 32 {
		return 0, fmt.Errorf("prefix length must be between 0 and 32, got %d", prefixLen)
	}

	return prefixLen, nil
}