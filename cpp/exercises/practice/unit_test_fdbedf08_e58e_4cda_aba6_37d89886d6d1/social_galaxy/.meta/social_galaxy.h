#ifndef SOCIAL_GALAXY_H
#define SOCIAL_GALAXY_H

#include <vector>
#include <set>
#include <unordered_map>

namespace social_galaxy {

class SocialGalaxy {
public:
    // Adds a new user with the given user_id to the network.
    // If user_id already exists, the operation is ignored.
    void add_user(int user_id);

    // Removes the user from the network and updates all associated relationships.
    // If the user does not exist, the operation is ignored.
    void remove_user(int user_id);

    // Establishes a follow relationship from follower_id to followee_id.
    // If either user does not exist or the edge already exists, the operation is ignored.
    void follow(int follower_id, int followee_id);

    // Removes the follow relationship from follower_id to followee_id.
    // If either user does not exist or the edge does not exist, the operation is ignored.
    void unfollow(int follower_id, int followee_id);

    // Returns a sorted vector of user_ids representing the followers of the given user_id.
    // If the user does not exist, returns an empty vector.
    std::vector<int> get_followers(int user_id);

    // Returns a sorted vector of user_ids representing the users that the given user_id follows.
    // If the user does not exist, returns an empty vector.
    std::vector<int> get_following(int user_id);

    // Returns a sorted vector of user_ids representing the intersection of the users 
    // followed by both user_id1 and user_id2.
    // If either user does not exist, returns an empty vector.
    std::vector<int> get_mutual_followers(int user_id1, int user_id2);

    // Returns a sorted vector of user_ids representing all users that can reach user_id within k hops.
    // A hop is defined by traversing one follow relationship in reverse (i.e., using the follower links).
    // The user should not include itself, even if reachable.
    // If the user does not exist, returns an empty vector.
    std::vector<int> get_k_hop_followers(int user_id, int k);

private:
    struct User {
        std::set<int> followers; // Users who follow this user.
        std::set<int> following; // Users that this user follows.
    };

    std::unordered_map<int, User> users;
};

} // namespace social_galaxy

#endif