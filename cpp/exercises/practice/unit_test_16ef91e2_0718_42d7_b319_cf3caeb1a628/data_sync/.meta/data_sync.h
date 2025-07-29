#if !defined(DATA_SYNC_H)
#define DATA_SYNC_H

#include <map>
#include <vector>

namespace data_sync {

// Main function to determine which datacenter IDs need to be synchronized
std::vector<int> get_missing_updates(
    const std::map<int, int>& local_version_vector,
    const std::map<int, int>& remote_version_vector);

// Bonus challenge functions (if implemented)
#if defined(BONUS_CHALLENGE)
// Merge two version vectors to get the latest state
std::map<int, int> merge_version_vectors(
    const std::map<int, int>& vector1,
    const std::map<int, int>& vector2);

// Handle datacenter failure
std::map<int, int> handle_datacenter_failure(
    const std::map<int, int>& state,
    int failed_datacenter_id);

// Check if a datacenter is marked as failed
bool is_datacenter_failed(
    const std::map<int, int>& state,
    int datacenter_id);

// Reintegrate a failed datacenter with new state
std::map<int, int> reintegrate_datacenter(
    const std::map<int, int>& state,
    int datacenter_id,
    int new_version);
#endif

}  // namespace data_sync

#endif  // DATA_SYNC_H