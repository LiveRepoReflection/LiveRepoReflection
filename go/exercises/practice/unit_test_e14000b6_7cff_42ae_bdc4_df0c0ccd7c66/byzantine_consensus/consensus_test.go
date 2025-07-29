package byzantine_consensus

import (
	"math/rand"
	"sync"
	"testing"
	"time"
)

// Message represents a message exchanged between nodes.
type Message struct {
	from    int
	content []byte
}

// Network simulates the communication network between nodes.
type Network struct {
	inboxes []chan Message
}

// NewNetwork creates a simulated network with n nodes.
func NewNetwork(n int) *Network {
	inboxes := make([]chan Message, n)
	for i := 0; i < n; i++ {
		// Buffered channel to hold messages.
		inboxes[i] = make(chan Message, 1000)
	}
	return &Network{inboxes: inboxes}
}

// send delivers a message from a source node to a destination node.
func (net *Network) send(src, dest int, msg []byte) {
	// Simulate asynchronous delivery with a small random delay.
	go func() {
		time.Sleep(time.Duration(rand.Intn(10)+1) * time.Millisecond)
		net.inboxes[dest] <- Message{from: src, content: msg}
	}()
}

// receiveNonBlocking collects all messages currently available for the node.
func (net *Network) receiveNonBlocking(nodeID int) [][]byte {
	var msgs [][]byte
	for {
		select {
		case m := <-net.inboxes[nodeID]:
			msgs = append(msgs, m.content)
		default:
			return msgs
		}
	}
}

// byzantineSend simulates a Byzantine node's send behavior.
// It ignores the provided message and sends a conflicting message instead.
func byzantineSend(net *Network, nodeID int, dest int, _ []byte) {
	// Send a random bogus message.
	bogusMessages := [][]byte{[]byte("bogus1"), []byte("conflict"), []byte("error")}
	msg := bogusMessages[rand.Intn(len(bogusMessages))]
	net.send(nodeID, dest, msg)
}

// byzantineReceive simulates a Byzantine node's receive behavior.
// It discards all incoming messages.
func byzantineReceive(_ *Network, _ int) [][]byte {
	// Byzantine node ignores received messages.
	return [][]byte{}
}

//------------------ Simulated Consensus Runner ------------------//

// runNode starts a consensus instance for a single node.
// It calls the RunConsensus function (to be implemented in the answer) with appropriate
// send and receive functions based on whether the node is honest or Byzantine.
func runNode(nodeID, n, f int, initialValue string, net *Network, byzantine bool, wg *sync.WaitGroup, results []string, resMutex *sync.Mutex) {
	defer wg.Done()

	var sendFn func(dest int, msg []byte)
	var receiveFn func() [][]byte

	if byzantine {
		// For Byzantine nodes, override send and receive with malicious behavior.
		sendFn = func(dest int, msg []byte) {
			byzantineSend(net, nodeID, dest, msg)
		}
		receiveFn = func() [][]byte {
			return byzantineReceive(net, nodeID)
		}
	} else {
		// Honest nodes use the proper network functions.
		sendFn = func(dest int, msg []byte) {
			net.send(nodeID, dest, msg)
		}
		receiveFn = func() [][]byte {
			return net.receiveNonBlocking(nodeID)
		}
	}

	// Call the consensus algorithm.
	// The consensus algorithm is expected to block until a decision is reached.
	// It must be implemented in the byzantine_consensus package.
	result := RunConsensus(nodeID, n, f, initialValue, sendFn, receiveFn)

	// Store the result in the shared results slice.
	resMutex.Lock()
	results[nodeID] = result
	resMutex.Unlock()
}

//----------------------- Unit Tests -----------------------//

// TestConsensusAllHonest tests the consensus algorithm in a scenario where all nodes are honest.
func TestConsensusAllHonest(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	n := 4
	f := 1
	// All nodes are honest in this test.
	network := NewNetwork(n)
	results := make([]string, n)
	var wg sync.WaitGroup
	var resMutex sync.Mutex

	// All honest nodes will have the same initial value.
	initialValue := "TX1"

	// Launch all nodes.
	for i := 0; i < n; i++ {
		wg.Add(1)
		go runNode(i, n, f, initialValue, network, false, &wg, results, &resMutex)
	}

	// Wait for all nodes to complete consensus.
	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	// Set a timeout to prevent hanging tests.
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Fatal("TestConsensusAllHonest timed out waiting for consensus.")
	}

	// Check that all nodes (honest nodes) agreed on the same transaction.
	for i, result := range results {
		if result != initialValue {
			t.Fatalf("Node %d reached consensus on %q, expected %q", i, result, initialValue)
		}
	}
}

// TestConsensusWithByzantine tests the consensus algorithm in a scenario with Byzantine nodes.
func TestConsensusWithByzantine(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	n := 7
	f := 2
	network := NewNetwork(n)
	results := make([]string, n)
	var wg sync.WaitGroup
	var resMutex sync.Mutex

	// Designate nodes 0 and 1 as Byzantine.
	byzantineNodes := map[int]bool{
		0: true,
		1: true,
	}

	// Honest nodes have the same initial value.
	honestInitial := "TX_HONEST"
	// Byzantine nodes can have arbitrary initial values.
	byzantineInitial := "TX_BYZ"

	// Launch all nodes.
	for i := 0; i < n; i++ {
		wg.Add(1)
		initVal := honestInitial
		if byzantineNodes[i] {
			initVal = byzantineInitial
		}
		go runNode(i, n, f, initVal, network, byzantineNodes[i], &wg, results, &resMutex)
	}

	// Wait for all nodes to complete consensus.
	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	// Set a timeout to prevent hanging tests.
	select {
	case <-done:
	case <-time.After(10 * time.Second):
		t.Fatal("TestConsensusWithByzantine timed out waiting for consensus.")
	}

	// Check that all honest nodes reached agreement.
	var honestResult string
	for i := 0; i < n; i++ {
		if byzantineNodes[i] {
			continue
		}
		if honestResult == "" {
			honestResult = results[i]
		} else if results[i] != honestResult {
			t.Fatalf("Honest node %d reached consensus on %q which differs from other honest result %q", i, results[i], honestResult)
		}
	}

	// Validity property: since all honest nodes began with honestInitial, they must agree on it.
	if honestResult != honestInitial {
		t.Fatalf("Honest nodes agreed on %q, expected %q", honestResult, honestInitial)
	}
}