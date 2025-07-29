package conflictresolution

type Transaction struct {
    ID         int
    Operations []Operation
}

type Operation struct {
    NodeID int
    Key    string
    Value  string
    OpType string
}