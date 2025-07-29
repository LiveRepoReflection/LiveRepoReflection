#include "resource_allocator.h"
#include <algorithm>
#include <queue>
#include <numeric>

// Helper struct to track job information
struct Job {
    int index;
    std::vector<double> requirements;
    int priority;
    int deadline;
    
    Job(int idx, const std::vector<double>& req, int p, int d)
        : index(idx), requirements(req), priority(p), deadline(d) {}
};

// Check if a job can be allocated with current resources
bool canAllocateJob(const std::vector<std::vector<double>>& nodes,
                   const std::vector<double>& requirements,
                   std::vector<std::vector<double>>& remainingResources) {
    
    size_t m = requirements.size();
    std::vector<double> totalAvailable(m, 0.0);
    
    // Calculate total available resources across all nodes
    for (const auto& node : nodes) {
        for (size_t j = 0; j < m; ++j) {
            totalAvailable[j] += node[j];
        }
    }
    
    // Check if total available resources are sufficient
    for (size_t j = 0; j < m; ++j) {
        if (totalAvailable[j] < requirements[j]) return false;
    }
    
    // Try to allocate resources greedily
    remainingResources = nodes;
    for (size_t j = 0; j < m; ++j) {
        double remaining = requirements[j];
        for (size_t i = 0; i < nodes.size() && remaining > 0; ++i) {
            double allocation = std::min(remaining, remainingResources[i][j]);
            remainingResources[i][j] -= allocation;
            remaining -= allocation;
        }
        if (remaining > 0) return false;
    }
    
    return true;
}

std::vector<int> allocateJobs(
    const std::vector<std::vector<double>>& nodes,
    const std::vector<std::tuple<std::vector<double>, int, int>>& requests,
    int currentTime) {
    
    if (nodes.empty() || requests.empty()) return {};
    
    // Create jobs with their indices
    std::vector<Job> jobs;
    for (size_t i = 0; i < requests.size(); ++i) {
        const auto& [req, priority, deadline] = requests[i];
        jobs.emplace_back(i, req, priority, deadline);
    }
    
    // Sort jobs by a score combining priority and deadline
    std::sort(jobs.begin(), jobs.end(),
              [currentTime](const Job& a, const Job& b) {
                  double scoreA = a.priority * (1.0 / (a.deadline - currentTime + 1));
                  double scoreB = b.priority * (1.0 / (b.deadline - currentTime + 1));
                  return scoreA > scoreB;
              });
    
    std::vector<int> allocatedJobs;
    std::vector<std::vector<double>> remainingResources = nodes;
    
    // Try to allocate jobs in order of their score
    for (const auto& job : jobs) {
        // Skip jobs that have passed their deadline
        if (job.deadline < currentTime) continue;
        
        // Try to allocate the job
        std::vector<std::vector<double>> tempResources;
        if (canAllocateJob(remainingResources, job.requirements, tempResources)) {
            allocatedJobs.push_back(job.index);
            remainingResources = tempResources;
        }
    }
    
    return allocatedJobs;
}