package consensus

import (
    "reflect"
    "testing"
)

func TestConsensus(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            consensus := NewConsensus(tc.nodes, tc.byzantine)
            
            // Add all transactions
            for _, tx := range tc.transactions {
                consensus.AddTransaction(tx.ID, tx.Timestamp, tx.Inputs, tx.Outputs)
            }

            // Process all messages
            for _, msg := range tc.messages {
                consensus.ProcessMessage(msg.SenderID, msg.ReceiverID, msg.Type, msg.ProposalNum, msg.TxOrder)
            }

            // Get final transaction order
            result := consensus.GetFinalOrder()

            if !reflect.DeepEqual(result, tc.expected) {
                t.Errorf("Expected transaction order %v, but got %v", tc.expected, result)
            }
        })
    }
}

func BenchmarkConsensus(b *testing.B) {
    // Use the first test case for benchmarking
    tc := testCases[0]
    
    for i := 0; i < b.N; i++ {
        consensus := NewConsensus(tc.nodes, tc.byzantine)
        
        for _, tx := range tc.transactions {
            consensus.AddTransaction(tx.ID, tx.Timestamp, tx.Inputs, tx.Outputs)
        }

        for _, msg := range tc.messages {
            consensus.ProcessMessage(msg.SenderID, msg.ReceiverID, msg.Type, msg.ProposalNum, msg.TxOrder)
        }

        consensus.GetFinalOrder()
    }
}