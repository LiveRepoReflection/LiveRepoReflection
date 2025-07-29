#pragma once
#include <string>
#include <vector>

// Participant interface definition
class Participant {
public:
    virtual ~Participant() = default;
    
    // Execute an operation on the participant
    virtual bool execute(std::string operation) = 0;
    
    // First phase of the two-phase commit protocol
    virtual bool prepare() = 0;
    
    // Second phase - commit the transaction
    virtual bool commit() = 0;
    
    // Second phase - rollback the transaction
    virtual bool rollback() = 0;
};

// The distributed transaction coordinator
class Coordinator {
public:
    /**
     * Execute a distributed transaction across multiple participants
     * using the two-phase commit protocol.
     * 
     * @param participants The participants in the transaction
     * @param operation The operation to execute
     * @return true if the transaction was committed successfully, false otherwise
     */
    bool executeTransaction(std::vector<Participant*> participants, std::string operation);
};