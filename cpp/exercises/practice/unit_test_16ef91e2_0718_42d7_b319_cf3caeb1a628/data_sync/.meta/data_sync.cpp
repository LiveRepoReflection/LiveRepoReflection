#include "data_sync.h"
#include <algorithm>
#include <unordered_set>

namespace data_sync {

std::vector<int> get_missing_updates(
    const std::map<int, int>& local_version_vector,
    const std::map<int, int>& remote_version_vector) {
    
    std::vector<int> missing_updates;
    
    // Reserve space to avoid reallocations
    missing_updates.reserve(remote_version_vector.size());
    
    // First check all datacenter IDs in the remote version vector
    for (const auto& [datacenter_id, remote_version] : remote_version_vector) {
        // Find the corresponding local version
        auto local_it = local_version_vector.find(datacenter_id);
        
        // If local datacenter doesn't have this ID or has a lower version
        if (local_it == local_version_vector.end()) {
            // If remote has updates (version > 0), we need to get them
            if (remote_version > 0) {
                missing_updates.push_back(datacenter_id);
            }
        } else if (local_it->second < remote_version) {
            // Local exists but has fewer updates than remote
            missing_updates.push_back(datacenter_id);
        }
    }
    
    return missing_updates;
}

// Bonus challenge implementations
#if defined(BONUS_CHALLENGE)

std::map<int, int> merge_version_vectors(
    const std::map<int, int>& vector1,
    const std::map<int, int>& vector2) {
    
    // Start with a copy of vector1
    std::map<int, int> merged(vector1);
    
    // For each entry in vector2, take the max value between vector1 and vector2
    for (const auto& [datacenter_id, version] : vector2) {
        auto it = merged.find(datacenter_id);
        if (it == merged.end()) {
            // If not in vector1, add it
            merged[datacenter_id] = version;
        } else {
            // Take the maximum version
            merged[datacenter_id] = std::max(it->second, version);
        }
    }
    
    return merged;
}

// We'll use a special flag value to mark failed datacenters
// For this implementation, we'll use a negative version number to indicate failure
// A real system would likely use a more sophisticated approach

std::map<int, int> handle_datacenter_failure(
    const std::map<int, int>& state,
    int failed_datacenter_id) {
    
    std::map<int, int> updated_state(state);
    
    // Find the datacenter and mark it as failed by negating its version
    auto it = updated_state.find(failed_datacenter_id);
    if (it != updated_state.end() && it->second >= 0) {
        // Only negate if it's not already marked as failed
        updated_state[failed_datacenter_id] = -it->second;
    }
    
    return updated_state;
}

bool is_datacenter_failed(
    const std::map<int, int>& state,
    int datacenter_id) {
    
    auto it = state.find(datacenter_id);
    if (it != state.end()) {
        // Negative version indicates failure
        return it->second < 0;
    }
    
    // Not in the map, consider it not failed
    // In a real system, this might be handled differently
    return false;
}

std::map<int, int> reintegrate_datacenter(
    const std::map<int, int>& state,
    int datacenter_id,
    int new_version) {
    
    std::map<int, int> updated_state(state);
    
    // Update the datacenter with the new version (regardless of previous state)
    updated_state[datacenter_id] = new_version;
    
    return updated_state;
}

#endif // BONUS_CHALLENGE

}  // namespace data_sync