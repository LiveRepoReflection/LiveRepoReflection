#include "tx_coordinator.h"
#include <unordered_map>
#include <mutex>
#include <chrono>
#include <thread>
#include <future>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <atomic>
#include <algorithm>

namespace tx_coordinator {

// Global structure to hold mock responses.
struct MockResponse {
    std::string response;
    int delay_ms; // delay in milliseconds
};

// Global map: key format: phase + "|" + url
static std::unordered_map<std::string, MockResponse> g_mockResponses;
static std::mutex g_mocksMutex;

// Global transaction counter.
static std::atomic<int> g_transactionCounter(0);
static std::mutex g_txLogMutex;

// Helper function: generate a composite key for a given phase and url.
static std::string makeKey(const std::string &url, const std::string &phase) {
    return phase + "|" + url;
}

// Helper function to log transactions to an append-only log file.
static void logTransaction(const std::string &transactionId, const std::string &status,
                           const std::vector<std::string> &services, const std::vector<std::string> &errors)
{
    std::lock_guard<std::mutex> lock(g_txLogMutex);
    std::ofstream ofs("tx_coordinator/tx_coordinator_log.txt", std::ios::app);
    if (ofs.is_open()) {
        ofs << "TransactionID: " << transactionId << ", ";
        ofs << "Status: " << status << ", ";
        ofs << "Services: [";
        for (size_t i = 0; i < services.size(); ++i) {
            ofs << services[i];
            if (i != services.size()-1)
                ofs << ", ";
        }
        ofs << "], ";
        ofs << "Errors: [";
        for (size_t i = 0; i < errors.size(); ++i) {
            ofs << errors[i];
            if (i != errors.size()-1)
                ofs << ", ";
        }
        ofs << "]\n";
        ofs.close();
    }
}

// Helper function to simulate a service call.
// It retrieves the mock response for the given url and phase,
// sleeps for the designated delay, and returns the response.
// If the delay exceeds the timeout, it returns "TIMEOUT".
static std::string simulateServiceCall(const std::string &url, const std::string &phase, int timeout_ms) {
    MockResponse mock;
    {
        std::lock_guard<std::mutex> lock(g_mocksMutex);
        std::string key = makeKey(url, phase);
        if (g_mockResponses.find(key) == g_mockResponses.end()) {
            return "NACK"; // Default to NACK if no mock provided.
        }
        mock = g_mockResponses[key];
    }
    // Use std::packaged_task to simulate call with delay.
    auto task = std::packaged_task<std::string()>([mock]() -> std::string {
        std::this_thread::sleep_for(std::chrono::milliseconds(mock.delay_ms));
        return mock.response;
    });
    std::future<std::string> fut = task.get_future();
    std::thread(std::move(task)).detach();
    if (fut.wait_for(std::chrono::milliseconds(timeout_ms)) == std::future_status::ready) {
        return fut.get();
    } else {
        return "TIMEOUT";
    }
}

// Replace substring "prepare" with newPhase in the given URL.
// Assumes that the URL contains "prepare" as a substring.
static std::string replacePhaseInUrl(const std::string &url, const std::string &newPhase) {
    std::string newUrl = url;
    size_t pos = newUrl.find("prepare");
    if (pos != std::string::npos) {
        newUrl.replace(pos, 7, newPhase);
    }
    return newUrl;
}

void setMockResponse(const std::string &url, const std::string &phase, const std::string &response, int delay_ms) {
    std::lock_guard<std::mutex> lock(g_mocksMutex);
    std::string key = makeKey(url, phase);
    g_mockResponses[key] = MockResponse{response, delay_ms};
}

void clearMockResponses() {
    std::lock_guard<std::mutex> lock(g_mocksMutex);
    g_mockResponses.clear();
}

void resetCoordinator() {
    clearMockResponses();
    g_transactionCounter = 0;
    // Clear the log file.
    std::lock_guard<std::mutex> lock(g_txLogMutex);
    std::ofstream ofs("tx_coordinator/tx_coordinator_log.txt", std::ios::trunc);
    ofs.close();
}

// In this simplified version, recoverPendingTransactions is a no-op.
// In a real-world scenario, this would scan the persistent log and attempt to finish pending transactions.
void recoverPendingTransactions() {
    // For simulation purposes, we read the log and perform rollback on any transaction with status "preparing" or "committing".
    // Here we do nothing as our processTransaction handles timeouts synchronously.
    // This function is provided to satisfy the interface.
}

// Process a transaction using a simplified two-phase commit protocol.
TransactionResult processTransaction(const std::vector<std::string> &prepareUrls, int timeout_ms) {
    TransactionResult result;
    std::vector<std::string> errors;
    std::vector<std::string> services = prepareUrls; // Original prepare URLs.

    // Generate a unique transaction ID.
    int txId = ++g_transactionCounter;
    std::ostringstream oss;
    oss << "tx_" << std::setfill('0') << std::setw(4) << txId;
    result.transactionId = oss.str();

    // Log initial state as "preparing".
    logTransaction(result.transactionId, "preparing", services, {});

    // Phase 1: Prepare.
    std::vector<std::future<std::string>> prepareFutures;
    for (const auto &url : prepareUrls) {
        prepareFutures.push_back(std::async(std::launch::async, simulateServiceCall, url, "prepare", timeout_ms));
    }

    bool prepareSuccess = true;
    for (size_t i = 0; i < prepareFutures.size(); ++i) {
        std::string response = prepareFutures[i].get();
        if (response != "ACK") {
            prepareSuccess = false;
            errors.push_back("Prepare failed for service: " + prepareUrls[i] + " with response: " + response);
        }
    }

    // If prepare phase fails, perform rollback.
    if (!prepareSuccess) {
        // Log state as "rolling back".
        logTransaction(result.transactionId, "rolling_back", services, errors);
        std::vector<std::future<std::string>> rollbackFutures;
        for (const auto &prepUrl : prepareUrls) {
            std::string rollbackUrl = replacePhaseInUrl(prepUrl, "rollback");
            rollbackFutures.push_back(std::async(std::launch::async, simulateServiceCall, rollbackUrl, "rollback", timeout_ms));
        }
        for (auto &fut : rollbackFutures) {
            // We ignore rollback responses for simplicity.
            fut.get();
        }
        result.status = "rolled_back";
        result.errors = errors;
        logTransaction(result.transactionId, result.status, services, errors);
        return result;
    }

    // Phase 2: Commit.
    // Prepare commit URLs by replacing "prepare" with "commit" in the original URLs.
    std::vector<std::string> commitUrls;
    for (const auto &prepUrl : prepareUrls) {
        commitUrls.push_back(replacePhaseInUrl(prepUrl, "commit"));
    }
    // Log state as "committing".
    logTransaction(result.transactionId, "committing", commitUrls, {});

    std::vector<std::future<std::string>> commitFutures;
    for (const auto &url : commitUrls) {
        commitFutures.push_back(std::async(std::launch::async, simulateServiceCall, url, "commit", timeout_ms));
    }

    bool commitSuccess = true;
    for (size_t i = 0; i < commitFutures.size(); ++i) {
        std::string response = commitFutures[i].get();
        if (response != "ACK") {
            commitSuccess = false;
            errors.push_back("Commit failed for service: " + commitUrls[i] + " with response: " + response);
        }
    }

    // If commit fails or times out, perform rollback.
    if (!commitSuccess) {
        logTransaction(result.transactionId, "rolling_back", services, errors);
        std::vector<std::future<std::string>> rollbackFutures;
        for (const auto &prepUrl : prepareUrls) {
            std::string rollbackUrl = replacePhaseInUrl(prepUrl, "rollback");
            rollbackFutures.push_back(std::async(std::launch::async, simulateServiceCall, rollbackUrl, "rollback", timeout_ms));
        }
        for (auto &fut : rollbackFutures) {
            fut.get();
        }
        result.status = "rolled_back";
        result.errors = errors;
        logTransaction(result.transactionId, result.status, services, errors);
        return result;
    }

    // If both phases succeed, transaction is committed.
    result.status = "committed";
    result.errors = errors;
    logTransaction(result.transactionId, result.status, services, errors);
    return result;
}

} // namespace tx_coordinator