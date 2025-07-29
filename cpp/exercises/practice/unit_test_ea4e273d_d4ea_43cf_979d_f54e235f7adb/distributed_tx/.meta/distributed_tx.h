#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <memory>
#include <vector>
#include <mutex>
#include <set>
#include <unordered_set>
#include <string>
#include <atomic>
#include <iostream>

// Interface for participants in a transaction
class TransactionParticipant {
public:
    virtual ~TransactionParticipant() = default;
    
    // Prepare for transaction (first phase of 2PC)
    virtual bool prepare() = 0;
    
    // Commit the transaction (second phase of 2PC)
    virtual bool commit() = 0;
    
    // Compensate/rollback any changes
    virtual bool compensate() = 0;
};

// Transaction coordinator that manages participants
class TransactionCoordinator {
public:
    TransactionCoordinator();
    ~TransactionCoordinator();

    // Initialize a new transaction
    void begin();

    // Enroll a participant in the current transaction
    void enroll(std::shared_ptr<TransactionParticipant> participant);

    // Attempt to commit the transaction
    bool commit();

    // Rollback the transaction
    bool rollback();

private:
    enum class TransactionState {
        INACTIVE,
        ACTIVE,
        COMMITTING,
        COMMITTED,
        ROLLING_BACK,
        ROLLED_BACK
    };

    // Log transaction events for debugging
    void logEvent(const std::string& event);

    std::vector<std::shared_ptr<TransactionParticipant>> participants_;
    std::unordered_set<std::shared_ptr<TransactionParticipant>> uniqueParticipants_;
    TransactionState state_;
    std::mutex mutex_;
    static std::atomic<int> transactionCounter_;
    int transactionId_;
};

#endif // DISTRIBUTED_TX_H