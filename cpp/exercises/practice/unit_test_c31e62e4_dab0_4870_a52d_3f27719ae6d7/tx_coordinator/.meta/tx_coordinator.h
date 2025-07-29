#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <mutex>
#include <atomic>
#include <condition_variable>
#include <thread>
#include <future>
#include <chrono>
#include <algorithm>
#include <queue>
#include <functional>
#include <random>

// Interface for services participating in transactions
class ServiceInterface {
public:
    virtual ~ServiceInterface() = default;
    
    // Prepare phase of the two-phase commit
    virtual bool prepare(int transactionId) = 0;
    
    // Commit phase of the two-phase commit
    virtual bool commit(int transactionId) = 0;
    
    // Rollback phase in case of transaction abort
    virtual bool rollback(int transactionId) = 0;
};

// Thread pool for handling concurrent transaction processing
class ThreadPool {
public:
    ThreadPool(size_t numThreads) : stop(false) {
        for (size_t i = 0; i < numThreads; ++i) {
            workers.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    
                    {
                        std::unique_lock<std::mutex> lock(queueMutex);
                        condition.wait(lock, [this] { 
                            return stop || !tasks.empty(); 
                        });
                        
                        if (stop && tasks.empty()) {
                            return;
                        }
                        
                        task = std::move(tasks.front());
                        tasks.pop();
                    }
                    
                    task();
                }
            });
        }
    }
    
    template<class F, class... Args>
    auto enqueue(F&& f, Args&&... args) 
        -> std::future<typename std::result_of<F(Args...)>::type> {
        using return_type = typename std::result_of<F(Args...)>::type;
        
        auto task = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        
        std::future<return_type> result = task->get_future();
        
        {
            std::unique_lock<std::mutex> lock(queueMutex);
            if (stop) {
                throw std::runtime_error("enqueue on stopped ThreadPool");
            }
            
            tasks.emplace([task]() { (*task)(); });
        }
        
        condition.notify_one();
        return result;
    }
    
    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queueMutex);
            stop = true;
        }
        
        condition.notify_all();
        
        for (std::thread &worker : workers) {
            worker.join();
        }
    }
    
private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    
    std::mutex queueMutex;
    std::condition_variable condition;
    bool stop;
};

// Structure to hold transaction state
struct TransactionState {
    enum class Status { PREPARING, PREPARED, COMMITTING, COMMITTED, ABORTING, ABORTED };
    
    int transactionId;
    std::vector<std::string> involvedServices;
    Status status;
    std::map<std::string, bool> votes;
    std::mutex mutex;
    std::condition_variable condition;
    bool completed;
    
    TransactionState(int id, const std::vector<std::string>& services)
        : transactionId(id),
          involvedServices(services),
          status(Status::PREPARING),
          completed(false) {
        // Initialize votes to false
        for (const auto& service : services) {
            votes[service] = false;
        }
        
        // Sort services lexicographically to prevent deadlocks
        std::sort(involvedServices.begin(), involvedServices.end());
    }
};

// The main transaction coordinator class
class TransactionCoordinator {
public:
    TransactionCoordinator(
        std::map<std::string, std::shared_ptr<ServiceInterface>> services,
        int timeoutMs = 50,
        int maxRetries = 3,
        int threadPoolSize = 8
    )
        : services_(services),
          timeoutMs_(timeoutMs),
          maxRetries_(maxRetries),
          threadPool_(threadPoolSize) {
        // Initialize random number generator for exponential backoff
        std::random_device rd;
        rng_ = std::mt19937(rd());
    }
    
    // Process a single transaction
    std::string processTransaction(int transactionId, const std::vector<std::string>& involvedServices) {
        // If no services are involved, we can commit immediately
        if (involvedServices.empty()) {
            return "COMMIT " + std::to_string(transactionId);
        }
        
        // Create a new transaction state object
        auto state = std::make_shared<TransactionState>(transactionId, involvedServices);
        
        {
            // Register the transaction in the active transactions map
            std::lock_guard<std::mutex> lock(transactionsMutex_);
            activeTransactions_[transactionId] = state;
        }
        
        // Start the prepare phase
        bool prepareSuccess = executePreparePhase(state);
        
        if (prepareSuccess) {
            // All services voted to commit, proceed with commit phase
            executeCommitPhase(state);
            
            {
                std::unique_lock<std::mutex> lock(state->mutex);
                state->status = TransactionState::Status::COMMITTED;
                state->completed = true;
                state->condition.notify_all();
            }
            
            // Clean up
            cleanupTransaction(transactionId);
            return "COMMIT " + std::to_string(transactionId);
        } else {
            // At least one service voted to abort, proceed with rollback
            executeRollbackPhase(state);
            
            {
                std::unique_lock<std::mutex> lock(state->mutex);
                state->status = TransactionState::Status::ABORTED;
                state->completed = true;
                state->condition.notify_all();
            }
            
            // Clean up
            cleanupTransaction(transactionId);
            return "ABORT " + std::to_string(transactionId);
        }
    }
    
    // Process multiple transactions in batch
    std::vector<std::string> processTransactions(
        const std::vector<std::pair<int, std::vector<std::string>>>& transactions) {
        
        std::vector<std::future<std::string>> futures;
        
        for (const auto& tx : transactions) {
            futures.push_back(
                threadPool_.enqueue(
                    &TransactionCoordinator::processTransaction,
                    this,
                    tx.first,
                    tx.second
                )
            );
        }
        
        std::vector<std::string> results;
        for (auto& future : futures) {
            results.push_back(future.get());
        }
        
        return results;
    }
    
private:
    std::map<std::string, std::shared_ptr<ServiceInterface>> services_;
    int timeoutMs_;
    int maxRetries_;
    std::map<int, std::shared_ptr<TransactionState>> activeTransactions_;
    std::mutex transactionsMutex_;
    ThreadPool threadPool_;
    std::mt19937 rng_;
    
    // Execute the prepare phase of the 2PC protocol
    bool executePreparePhase(std::shared_ptr<TransactionState> state) {
        std::vector<std::future<bool>> prepareFutures;
        
        // Send prepare requests to all involved services
        for (const auto& serviceId : state->involvedServices) {
            auto serviceIt = services_.find(serviceId);
            if (serviceIt == services_.end()) {
                // Service not found, abort the transaction
                return false;
            }
            
            prepareFutures.push_back(
                threadPool_.enqueue([this, serviceId, state]() {
                    return prepareService(serviceId, state);
                })
            );
        }
        
        // Wait for all prepare responses
        bool allPrepared = true;
        for (auto& future : prepareFutures) {
            try {
                bool prepared = future.get();
                if (!prepared) {
                    allPrepared = false;
                    break;
                }
            } catch (const std::exception&) {
                // Exception during prepare, abort the transaction
                allPrepared = false;
                break;
            }
        }
        
        return allPrepared;
    }
    
    // Execute the commit phase of the 2PC protocol
    void executeCommitPhase(std::shared_ptr<TransactionState> state) {
        std::vector<std::future<bool>> commitFutures;
        
        {
            std::unique_lock<std::mutex> lock(state->mutex);
            state->status = TransactionState::Status::COMMITTING;
        }
        
        // Send commit requests to all involved services
        for (const auto& serviceId : state->involvedServices) {
            auto serviceIt = services_.find(serviceId);
            if (serviceIt == services_.end()) {
                continue;
            }
            
            commitFutures.push_back(
                threadPool_.enqueue([this, serviceId, state]() {
                    return commitService(serviceId, state->transactionId);
                })
            );
        }
        
        // Wait for all commit responses (but don't retry on failure)
        for (auto& future : commitFutures) {
            try {
                future.get();
            } catch (const std::exception&) {
                // Log the error but continue with other services
            }
        }
    }
    
    // Execute the rollback phase in case of abort
    void executeRollbackPhase(std::shared_ptr<TransactionState> state) {
        std::vector<std::future<bool>> rollbackFutures;
        
        {
            std::unique_lock<std::mutex> lock(state->mutex);
            state->status = TransactionState::Status::ABORTING;
        }
        
        // Send rollback requests to all involved services
        for (const auto& serviceId : state->involvedServices) {
            auto serviceIt = services_.find(serviceId);
            if (serviceIt == services_.end()) {
                continue;
            }
            
            rollbackFutures.push_back(
                threadPool_.enqueue([this, serviceId, state]() {
                    return rollbackService(serviceId, state->transactionId);
                })
            );
        }
        
        // Wait for all rollback responses (but don't retry on failure)
        for (auto& future : rollbackFutures) {
            try {
                future.get();
            } catch (const std::exception&) {
                // Log the error but continue with other services
            }
        }
    }
    
    // Prepare a single service with retry logic
    bool prepareService(const std::string& serviceId, std::shared_ptr<TransactionState> state) {
        auto service = services_[serviceId];
        int retries = 0;
        
        while (retries <= maxRetries_) {
            try {
                // Set up a timeout using a future
                auto prepareTask = std::async(
                    std::launch::async,
                    [&service, &state]() {
                        return service->prepare(state->transactionId);
                    }
                );
                
                // Wait for the prepare call to complete or timeout
                if (prepareTask.wait_for(std::chrono::milliseconds(timeoutMs_)) 
                    == std::future_status::timeout) {
                    // Timeout occurred
                    throw std::runtime_error("Service prepare timeout");
                }
                
                bool prepared = prepareTask.get();
                
                // Update the vote in the transaction state
                {
                    std::unique_lock<std::mutex> lock(state->mutex);
                    state->votes[serviceId] = prepared;
                }
                
                return prepared;
            } catch (const std::exception&) {
                // Service error or timeout, retry with exponential backoff
                retries++;
                
                if (retries <= maxRetries_) {
                    // Calculate backoff time: base * 2^retry * random factor
                    std::uniform_real_distribution<double> dist(0.5, 1.5);
                    int backoffMs = static_cast<int>(5 * std::pow(2, retries) * dist(rng_));
                    std::this_thread::sleep_for(std::chrono::milliseconds(backoffMs));
                }
            }
        }
        
        // All retries failed, abort the transaction
        {
            std::unique_lock<std::mutex> lock(state->mutex);
            state->votes[serviceId] = false;
        }
        
        return false;
    }
    
    // Commit a transaction on a single service
    bool commitService(const std::string& serviceId, int transactionId) {
        auto service = services_[serviceId];
        
        try {
            // Set up a timeout using a future
            auto commitTask = std::async(
                std::launch::async,
                [&service, transactionId]() {
                    return service->commit(transactionId);
                }
            );
            
            // Wait for the commit call to complete or timeout
            if (commitTask.wait_for(std::chrono::milliseconds(timeoutMs_)) 
                == std::future_status::timeout) {
                // Timeout occurred, but we don't retry commit operations
                throw std::runtime_error("Service commit timeout");
            }
            
            return commitTask.get();
        } catch (const std::exception&) {
            // Service error or timeout during commit
            // This is a critical failure in 2PC, but we continue with other services
            return false;
        }
    }
    
    // Rollback a transaction on a single service
    bool rollbackService(const std::string& serviceId, int transactionId) {
        auto service = services_[serviceId];
        
        try {
            // Set up a timeout using a future
            auto rollbackTask = std::async(
                std::launch::async,
                [&service, transactionId]() {
                    return service->rollback(transactionId);
                }
            );
            
            // Wait for the rollback call to complete or timeout
            if (rollbackTask.wait_for(std::chrono::milliseconds(timeoutMs_)) 
                == std::future_status::timeout) {
                // Timeout occurred, but we don't retry rollback operations
                throw std::runtime_error("Service rollback timeout");
            }
            
            return rollbackTask.get();
        } catch (const std::exception&) {
            // Service error or timeout during rollback
            // Not much we can do here, just return false
            return false;
        }
    }
    
    // Clean up a completed transaction
    void cleanupTransaction(int transactionId) {
        std::lock_guard<std::mutex> lock(transactionsMutex_);
        activeTransactions_.erase(transactionId);
    }
};