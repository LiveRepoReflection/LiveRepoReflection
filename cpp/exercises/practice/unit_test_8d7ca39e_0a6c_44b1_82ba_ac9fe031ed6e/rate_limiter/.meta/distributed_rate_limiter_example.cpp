#include "rate_limiter.h"
#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <iomanip>
#include <chrono>

void simulateTraffic(RateLimiter& limiter, const std::string& key, 
                     int numRequests, std::atomic<int>& allowed, std::atomic<int>& limited) {
    for (int i = 0; i < numRequests; ++i) {
        if (limiter.allow(key)) {
            allowed++;
        } else {
            limited++;
        }
        // Small delay between requests
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
}

void printProgress(const std::atomic<int>& allowed, const std::atomic<int>& limited, 
                   bool& done, int totalRequests) {
    while (!done) {
        int current_allowed = allowed.load();
        int current_limited = limited.load();
        int current_total = current_allowed + current_limited;
        
        double progress = static_cast<double>(current_total) / totalRequests * 100;
        double allowed_percent = current_total > 0 ? 
            static_cast<double>(current_allowed) / current_total * 100 : 0;
        
        std::cout << "\rProgress: " << std::fixed << std::setprecision(1) << progress << "% "
                  << "Allowed: " << current_allowed << " (" << allowed_percent << "%) "
                  << "Limited: " << current_limited
                  << std::flush;
                  
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    std::cout << std::endl;
}

int main() {
    // Example parameters
    int rateLimit = 20;        // 20 requests per second
    int windowDurationMs = 1000; // 1 second window
    int numThreads = 5;        // Simulate 5 concurrent clients
    int requestsPerThread = 50; // Each thread sends 50 requests
    int totalRequests = numThreads * requestsPerThread;
    
    std::cout << "Initializing rate limiter with limit of " 
              << rateLimit << " requests per " << windowDurationMs << "ms" << std::endl;
    
    // Create a distributed rate limiter (simulated with Redis)
    DistributedRateLimiter limiter(rateLimit, windowDurationMs);
    
    std::string key = "test_user";
    std::atomic<int> allowed(0);
    std::atomic<int> limited(0);
    bool done = false;
    
    std::cout << "Starting " << numThreads << " threads, each sending " 
              << requestsPerThread << " requests" << std::endl;
    
    // Start the progress printing thread
    std::thread progress_thread(printProgress, std::ref(allowed), std::ref(limited), 
                               std::ref(done), totalRequests);
    
    // Start the worker threads
    std::vector<std::thread> threads;
    for (int i = 0; i < numThreads; ++i) {
        threads.push_back(std::thread(simulateTraffic, 
                                     std::ref(limiter), key, 
                                     requestsPerThread, 
                                     std::ref(allowed), std::ref(limited)));
    }
    
    // Wait for all threads to complete
    for (auto& t : threads) {
        t.join();
    }
    
    done = true;
    progress_thread.join();
    
    std::cout << "\nTest completed!" << std::endl;
    std::cout << "Total requests: " << totalRequests << std::endl;
    std::cout << "Allowed: " << allowed << " (" 
              << (static_cast<double>(allowed) / totalRequests * 100) << "%)" << std::endl;
    std::cout << "Limited: " << limited << " (" 
              << (static_cast<double>(limited) / totalRequests * 100) << "%)" << std::endl;
    
    // Theoretical expected allowed requests for a perfect rate limiter:
    // With 5 threads making requests every 5ms, we should see approximately
    // rateLimit requests allowed in each windowDurationMs period.
    int expectedAllowed = totalRequests <= rateLimit ? totalRequests : rateLimit;
    std::cout << "Perfect rate limiter would allow approximately: " << expectedAllowed << " requests" << std::endl;
    
    return 0;
}