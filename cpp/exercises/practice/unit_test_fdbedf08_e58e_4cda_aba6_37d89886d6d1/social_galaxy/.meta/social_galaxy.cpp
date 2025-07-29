#include "social_galaxy.h"
#include <queue>
#include <algorithm>

namespace social_galaxy {

void SocialGalaxy::add_user(int user_id) {
    // If the user already exists, ignore.
    if (users.find(user_id) != users.end())
        return;
    users[user_id] = User();
}

void SocialGalaxy::remove_user(int user_id) {
    auto it = users.find(user_id);
    if (it == users.end())
        return;

    // Remove user_id from all followers' following lists.
    for (const int follower : it->second.followers) {
        auto followerIt = users.find(follower);
        if (followerIt != users.end()) {
            followerIt->second.following.erase(user_id);
        }
    }
    // Remove user_id from all followees' followers lists.
    for (const int followee : it->second.following) {
        auto followeeIt = users.find(followee);
        if (followeeIt != users.end()) {
            followeeIt->second.followers.erase(user_id);
        }
    }
    // Erase the user from the network.
    users.erase(it);
}

void SocialGalaxy::follow(int follower_id, int followee_id) {
    // Ensure both users exist.
    if (users.find(follower_id) == users.end() || users.find(followee_id) == users.end())
        return;
    // Check if the follow relationship already exists.
    if (users[follower_id].following.find(followee_id) != users[follower_id].following.end())
        return;

    // Add followee to follower's following and add follower to followee's followers.
    users[follower_id].following.insert(followee_id);
    users[followee_id].followers.insert(follower_id);
}

void SocialGalaxy::unfollow(int follower_id, int followee_id) {
    // Ensure both users exist.
    if (users.find(follower_id) == users.end() || users.find(followee_id) == users.end())
        return;
    // Check if the follow relationship exists.
    if (users[follower_id].following.find(followee_id) == users[follower_id].following.end())
        return;
    // Remove the relationship.
    users[follower_id].following.erase(followee_id);
    users[followee_id].followers.erase(follower_id);
}

std::vector<int> SocialGalaxy::get_followers(int user_id) {
    std::vector<int> result;
    auto it = users.find(user_id);
    if (it == users.end())
        return result;
    // Since followers is stored in a set, it's already sorted.
    result.assign(it->second.followers.begin(), it->second.followers.end());
    return result;
}

std::vector<int> SocialGalaxy::get_following(int user_id) {
    std::vector<int> result;
    auto it = users.find(user_id);
    if (it == users.end())
        return result;
    result.assign(it->second.following.begin(), it->second.following.end());
    return result;
}

std::vector<int> SocialGalaxy::get_mutual_followers(int user_id1, int user_id2) {
    std::vector<int> result;
    auto it1 = users.find(user_id1);
    auto it2 = users.find(user_id2);
    if (it1 == users.end() || it2 == users.end())
        return result;
    
    // Intersection of following sets for both users.
    const std::set<int>& following1 = it1->second.following;
    const std::set<int>& following2 = it2->second.following;
    
    std::set_intersection(following1.begin(), following1.end(),
                          following2.begin(), following2.end(),
                          std::back_inserter(result));
    return result;
}

std::vector<int> SocialGalaxy::get_k_hop_followers(int user_id, int k) {
    std::vector<int> result;
    auto startIt = users.find(user_id);
    if (startIt == users.end() || k <= 0)
        return result;

    // Reverse BFS: traverse using followers to find all users that can reach user_id.
    std::set<int> visited;
    std::queue<std::pair<int, int>> q; // pair<current_user, current_depth>

    // Start from direct followers of the target.
    for (int follower : startIt->second.followers) {
        q.push({follower, 1});
        visited.insert(follower);
    }

    while (!q.empty()) {
        auto[current, depth] = q.front();
        q.pop();
        if (depth <= k) {
            // Add current user to result.
            result.push_back(current);
            if (depth < k) {
                // Traverse further in the reverse direction.
                auto it = users.find(current);
                if (it != users.end()) {
                    for (int next_follower : it->second.followers) {
                        if (visited.find(next_follower) == visited.end() && next_follower != user_id) {
                            visited.insert(next_follower);
                            q.push({next_follower, depth + 1});
                        }
                    }
                }
            }
        }
    }
    // Sorting result in ascending order even though our traversal
    // could have produced unsorted order.
    std::sort(result.begin(), result.end());
    return result;
}

} // namespace social_galaxy