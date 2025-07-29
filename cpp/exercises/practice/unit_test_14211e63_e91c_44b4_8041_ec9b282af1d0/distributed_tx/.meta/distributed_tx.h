#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>
#include <memory>
#include <future>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <unordered_map>
#include <queue>

enum class PrepareResult {
    READY,
    ABORT,
    TIMEOUT
};

enum class TransactionResult {
    COMMITTED,
    ABORTED,
    TIMEOUT,
    INVALID
};

class IParticipant {
public:
    virtual ~IParticipant() = default;
    virtual PrepareResult prepare() = 0;
    virtual bool commit() = 0;
    virtual bool rollback() = 0;
};

class TransactionCoordinator {
public:
    TransactionCoordinator(
        size_t maxParticipants = 100,
        std::chrono::milliseconds timeout = std::chrono::seconds(3)
    );
    
    TransactionResult executeTransaction(
        const std::vector<std::shared_ptr<IParticipant>>& participants
    );

private:
    bool validateParticipants(
        const std::vector<std::shared_ptr<IParticipant>>& participants
    );
    
    PrepareResult preparePhase(
        const std::vector<std::shared_ptr<IParticipant>>& participants
    );
    
    TransactionResult commitPhase(
        const std::vector<std::shared_ptr<IParticipant>>& participants
    );
    
    void rollbackAll(
        const std::vector<std::shared_ptr<IParticipant>>& participants
    );

    const size_t maxParticipants_;
    const std::chrono::milliseconds timeout_;
    std::mutex mutex_;
    std::condition_variable cv_;
};

#endif