package consensus

type transaction struct {
    ID        string
    Timestamp int
    Inputs    []string
    Outputs   []string
}

type message struct {
    SenderID   int
    ReceiverID int
    Type       string
    ProposalNum int
    TxOrder    []string
}

var testCases = []struct {
    description string
    nodes       int
    byzantine   int
    transactions []transaction
    messages    []message
    expected    []string
}{
    {
        description: "basic consensus with no conflicts",
        nodes:       4,
        byzantine:   0,
        transactions: []transaction{
            {ID: "tx1", Timestamp: 1, Inputs: []string{"a"}, Outputs: []string{"b"}},
            {ID: "tx2", Timestamp: 2, Inputs: []string{"c"}, Outputs: []string{"d"}},
            {ID: "tx3", Timestamp: 3, Inputs: []string{"e"}, Outputs: []string{"f"}},
        },
        messages: []message{
            {SenderID: 0, ReceiverID: 1, Type: "propose", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 1, ReceiverID: 0, Type: "promise", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 2, ReceiverID: 0, Type: "promise", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 0, ReceiverID: -1, Type: "accept", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
        },
        expected: []string{"tx1", "tx2", "tx3"},
    },
    {
        description: "conflict resolution with same timestamp",
        nodes:       4,
        byzantine:   0,
        transactions: []transaction{
            {ID: "tx1", Timestamp: 1, Inputs: []string{"a"}, Outputs: []string{"b"}},
            {ID: "tx2", Timestamp: 1, Inputs: []string{"a"}, Outputs: []string{"c"}},
            {ID: "tx3", Timestamp: 2, Inputs: []string{"d"}, Outputs: []string{"e"}},
        },
        messages: []message{
            {SenderID: 0, ReceiverID: 1, Type: "propose", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 1, ReceiverID: 0, Type: "promise", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 2, ReceiverID: 0, Type: "promise", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 0, ReceiverID: -1, Type: "accept", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
        },
        expected: []string{"tx1", "tx3"}, // tx2 is conflicting with tx1, tx1 wins due to lexicographical order
    },
    {
        description: "byzantine nodes scenario",
        nodes:       7,
        byzantine:   2,
        transactions: []transaction{
            {ID: "tx1", Timestamp: 1, Inputs: []string{"a"}, Outputs: []string{"b"}},
            {ID: "tx2", Timestamp: 2, Inputs: []string{"c"}, Outputs: []string{"d"}},
            {ID: "tx3", Timestamp: 3, Inputs: []string{"e"}, Outputs: []string{"f"}},
        },
        messages: []message{
            {SenderID: 0, ReceiverID: 1, Type: "propose", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 1, ReceiverID: 0, Type: "promise", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 2, ReceiverID: 0, Type: "promise", ProposalNum: 2, TxOrder: []string{"tx3", "tx2", "tx1"}}, // Byzantine behavior
            {SenderID: 3, ReceiverID: 0, Type: "promise", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 4, ReceiverID: 0, Type: "promise", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
            {SenderID: 0, ReceiverID: -1, Type: "accept", ProposalNum: 1, TxOrder: []string{"tx1", "tx2", "tx3"}},
        },
        expected: []string{"tx1", "tx2", "tx3"},
    },
}