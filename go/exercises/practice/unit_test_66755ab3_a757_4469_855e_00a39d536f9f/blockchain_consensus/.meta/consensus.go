package consensus

import (
    "sort"
    "sync"
)

type Transaction struct {
    id        string
    timestamp int
    inputs    []string
    outputs   []string
}

type Promise struct {
    nodeID      int
    proposalNum int
    txOrder     []string
}

type Consensus struct {
    mu          sync.RWMutex
    nodes       int
    byzantine   int
    transactions map[string]*Transaction
    promises    map[int][]Promise
    accepted    map[int]bool
    highestPropNum int
    finalOrder  []string
}

func NewConsensus(nodes, byzantine int) *Consensus {
    return &Consensus{
        nodes:        nodes,
        byzantine:    byzantine,
        transactions: make(map[string]*Transaction),
        promises:     make(map[int][]Promise),
        accepted:     make(map[int]bool),
    }
}

func (c *Consensus) AddTransaction(id string, timestamp int, inputs, outputs []string) {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.transactions[id] = &Transaction{
        id:        id,
        timestamp: timestamp,
        inputs:    inputs,
        outputs:   outputs,
    }
}

func (c *Consensus) ProcessMessage(senderID, receiverID int, msgType string, proposalNum int, txOrder []string) {
    c.mu.Lock()
    defer c.mu.Unlock()

    switch msgType {
    case "propose":
        if proposalNum > c.highestPropNum {
            c.highestPropNum = proposalNum
            c.promises[proposalNum] = append(c.promises[proposalNum], Promise{
                nodeID:      senderID,
                proposalNum: proposalNum,
                txOrder:     txOrder,
            })
        }

    case "promise":
        c.promises[proposalNum] = append(c.promises[proposalNum], Promise{
            nodeID:      senderID,
            proposalNum: proposalNum,
            txOrder:     txOrder,
        })

    case "accept":
        if len(c.promises[proposalNum]) >= c.getQuorumSize() {
            c.accepted[proposalNum] = true
            c.finalOrder = c.resolveConflicts(txOrder)
        }
    }
}

func (c *Consensus) getQuorumSize() int {
    return (c.nodes - c.byzantine + 1) / 2
}

func (c *Consensus) resolveConflicts(txOrder []string) []string {
    // Create a map to track used inputs
    usedInputs := make(map[string]string)
    resolvedOrder := make([]string, 0)

    // Sort transactions by timestamp and ID for deterministic conflict resolution
    type txWithIndex struct {
        idx int
        tx  *Transaction
    }
    txsWithIndex := make([]txWithIndex, 0)
    
    for i, txID := range txOrder {
        if tx, exists := c.transactions[txID]; exists {
            txsWithIndex = append(txsWithIndex, txWithIndex{i, tx})
        }
    }

    sort.Slice(txsWithIndex, func(i, j int) bool {
        if txsWithIndex[i].tx.timestamp == txsWithIndex[j].tx.timestamp {
            return txsWithIndex[i].tx.id < txsWithIndex[j].tx.id
        }
        return txsWithIndex[i].tx.timestamp < txsWithIndex[j].tx.timestamp
    })

    // Process transactions in order
    for _, twi := range txsWithIndex {
        tx := twi.tx
        hasConflict := false

        // Check for input conflicts
        for _, input := range tx.inputs {
            if usedTxID, exists := usedInputs[input]; exists && usedTxID != tx.id {
                hasConflict = true
                break
            }
        }

        if !hasConflict {
            resolvedOrder = append(resolvedOrder, tx.id)
            // Mark inputs as used
            for _, input := range tx.inputs {
                usedInputs[input] = tx.id
            }
        }
    }

    return resolvedOrder
}

func (c *Consensus) GetFinalOrder() []string {
    c.mu.RLock()
    defer c.mu.RUnlock()
    
    result := make([]string, len(c.finalOrder))
    copy(result, c.finalOrder)
    return result
}