#include "distributed_tx.h"

// Microservice representation
struct Microservice {
    long long id;
    long long prepare_time;  // in milliseconds
    long long commit_time;   // in milliseconds
    long long rollback_time; // in milliseconds
    bool in_transaction;
    long long transaction_id; // which transaction this service is part of

    Microservice(long long id, long long prepare, long long commit, long long rollback)
        : id(id), prepare_time(prepare), commit_time(commit), rollback_time(rollback), in_transaction(false), transaction_id(-1) {}
};

// Transaction statuses
enum class TransactionStatus {
    IN_PROGRESS,
    COMMITTED,
    ROLLED_BACK,
    ABORTED
};

// Helper function to convert enum to string
std::string status_to_string(TransactionStatus status) {
    switch (status) {
        case TransactionStatus::IN_PROGRESS: return "IN_PROGRESS";
        case TransactionStatus::COMMITTED: return "COMMITTED";
        case TransactionStatus::ROLLED_BACK: return "ROLLED_BACK";
        case TransactionStatus::ABORTED: return "ABORTED";
        default: return "UNKNOWN";
    }
}

// Transaction representation
struct Transaction {
    long long id;
    std::vector<long long> service_ids;
    TransactionStatus status;

    Transaction(long long id, const std::vector<long long>& services)
        : id(id), service_ids(services), status(TransactionStatus::IN_PROGRESS) {}
};

// Global state
class TransactionCoordinator {
private:
    std::unordered_map<long long, std::shared_ptr<Microservice>> services;
    std::unordered_map<long long, std::shared_ptr<Transaction>> transactions;
    std::mutex services_mutex;
    std::mutex transactions_mutex;

public:
    // Add a new microservice to the system
    void add_service(long long service_id, long long prepare_time, long long commit_time, long long rollback_time) {
        std::lock_guard<std::mutex> lock(services_mutex);
        services[service_id] = std::make_shared<Microservice>(service_id, prepare_time, commit_time, rollback_time);
    }

    // Begin a new transaction
    bool begin_transaction(long long transaction_id, const std::vector<long long>& service_ids) {
        std::lock_guard<std::mutex> services_lock(services_mutex);
        
        // Check if all services exist and are available
        for (const auto& service_id : service_ids) {
            if (services.find(service_id) == services.end() || 
                services[service_id]->in_transaction) {
                return false;
            }
        }

        // Mark all services as participating in this transaction
        for (const auto& service_id : service_ids) {
            services[service_id]->in_transaction = true;
            services[service_id]->transaction_id = transaction_id;
        }

        // Create the transaction
        std::lock_guard<std::mutex> transactions_lock(transactions_mutex);
        transactions[transaction_id] = std::make_shared<Transaction>(transaction_id, service_ids);
        return true;
    }

    // Get the status of a transaction
    std::string get_transaction_status(long long transaction_id) {
        std::lock_guard<std::mutex> lock(transactions_mutex);
        if (transactions.find(transaction_id) == transactions.end()) {
            return "NOT_FOUND";
        }
        return status_to_string(transactions[transaction_id]->status);
    }

    // Commit a transaction
    std::string commit_transaction(long long transaction_id) {
        std::lock_guard<std::mutex> transactions_lock(transactions_mutex);
        
        // Check if transaction exists
        if (transactions.find(transaction_id) == transactions.end()) {
            return "TRANSACTION_NOT_FOUND";
        }

        auto transaction = transactions[transaction_id];
        if (transaction->status != TransactionStatus::IN_PROGRESS) {
            // Transaction already completed
            return "INVALID_STATE";
        }

        std::lock_guard<std::mutex> services_lock(services_mutex);

        // Calculate total time for committing (sum of all service commit times)
        long long total_time = 0;
        for (const auto& service_id : transaction->service_ids) {
            if (services.find(service_id) == services.end()) {
                // Service disappeared during transaction
                return "COMMIT_FAILED";
            }
            total_time += services[service_id]->commit_time;
        }

        // Mark transaction as committed
        transaction->status = TransactionStatus::COMMITTED;

        // Release all services from this transaction
        for (const auto& service_id : transaction->service_ids) {
            if (services.find(service_id) != services.end()) {
                services[service_id]->in_transaction = false;
                services[service_id]->transaction_id = -1;
            }
        }

        return std::to_string(total_time);
    }

    // Rollback a transaction
    std::string rollback_transaction(long long transaction_id) {
        std::lock_guard<std::mutex> transactions_lock(transactions_mutex);
        
        // Check if transaction exists
        if (transactions.find(transaction_id) == transactions.end()) {
            return "TRANSACTION_NOT_FOUND";
        }

        auto transaction = transactions[transaction_id];
        if (transaction->status != TransactionStatus::IN_PROGRESS) {
            // Transaction already completed
            return "INVALID_STATE";
        }

        std::lock_guard<std::mutex> services_lock(services_mutex);

        // Calculate total time for rolling back (sum of all service rollback times)
        long long total_time = 0;
        for (const auto& service_id : transaction->service_ids) {
            if (services.find(service_id) == services.end()) {
                // Service disappeared during transaction
                return "ROLLBACK_FAILED";
            }
            total_time += services[service_id]->rollback_time;
        }

        // Mark transaction as rolled back
        transaction->status = TransactionStatus::ROLLED_BACK;

        // Release all services from this transaction
        for (const auto& service_id : transaction->service_ids) {
            if (services.find(service_id) != services.end()) {
                services[service_id]->in_transaction = false;
                services[service_id]->transaction_id = -1;
            }
        }

        return std::to_string(total_time);
    }
};

// Main function to process commands
void process_commands(std::istream& input) {
    TransactionCoordinator coordinator;
    std::string line;
    
    while (std::getline(input, line)) {
        std::istringstream iss(line);
        std::string command;
        iss >> command;

        if (command == "ADD_SERVICE") {
            long long service_id, prepare_time, commit_time, rollback_time;
            iss >> service_id >> prepare_time >> commit_time >> rollback_time;
            coordinator.add_service(service_id, prepare_time, commit_time, rollback_time);
        } 
        else if (command == "BEGIN_TRANSACTION") {
            long long transaction_id;
            iss >> transaction_id;
            
            std::vector<long long> service_ids;
            long long service_id;
            while (iss >> service_id) {
                service_ids.push_back(service_id);
            }
            
            bool result = coordinator.begin_transaction(transaction_id, service_ids);
            std::cout << (result ? "OK" : "ABORTED") << std::endl;
        } 
        else if (command == "GET_TRANSACTION_STATUS") {
            long long transaction_id;
            iss >> transaction_id;
            std::cout << coordinator.get_transaction_status(transaction_id) << std::endl;
        } 
        else if (command == "COMMIT_TRANSACTION") {
            long long transaction_id;
            iss >> transaction_id;
            std::cout << coordinator.commit_transaction(transaction_id) << std::endl;
        } 
        else if (command == "ROLLBACK_TRANSACTION") {
            long long transaction_id;
            iss >> transaction_id;
            std::cout << coordinator.rollback_transaction(transaction_id) << std::endl;
        }
    }
}