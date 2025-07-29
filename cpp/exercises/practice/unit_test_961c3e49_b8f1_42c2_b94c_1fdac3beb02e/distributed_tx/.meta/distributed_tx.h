#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <string>
#include <unordered_map>
#include <vector>
#include <mutex>
#include <condition_variable>
#include <fstream>
#include <set>
#include <memory>
#include <chrono>

class TransactionCoordinator {
public:
    TransactionCoordinator();
    virtual ~TransactionCoordinator();
    
    void processCommand(const std::string& command);
    
protected:
    virtual void processOutput(const std::string& message);

private:
    struct Transaction {
        int id;
        std::set<int> services;
        std::set<int> prepared_services;
        bool is_committed;
        bool is_aborted;
        std::chrono::steady_clock::time_point start_time;
        
        Transaction(int tid, const std::set<int>& sids)
            : id(tid), services(sids), is_committed(false), is_aborted(false),
              start_time(std::chrono::steady_clock::now()) {}
    };

    void handleBegin(const std::vector<std::string>& tokens);
    void handlePrepared(const std::vector<std::string>& tokens);
    void handleAbort(const std::vector<std::string>& tokens);
    void handleTimeout(const std::vector<std::string>& tokens);
    void handleRecover();
    void handlePrintLog();
    
    void commitTransaction(Transaction& tx);
    void rollbackTransaction(Transaction& tx);
    void writeToLog(const std::string& entry);
    void checkTimeout(int transaction_id);
    std::vector<std::string> tokenize(const std::string& command);
    
    std::unordered_map<int, std::unique_ptr<Transaction>> transactions_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::ofstream log_file_;
    static constexpr int TIMEOUT_MS = 100;
};

#endif // DISTRIBUTED_TX_H