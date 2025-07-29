#include "social_galaxy.h"
#include "catch.hpp"
#include <vector>
#include <algorithm>

using namespace social_galaxy;

TEST_CASE("Add users and duplicate additions", "[social_galaxy]") {
    SocialGalaxy sg;
    sg.add_user(1);
    sg.add_user(2);
    sg.add_user(1); // Duplicate, should be ignored

    std::vector<int> followers1 = sg.get_followers(1);
    std::vector<int> following1 = sg.get_following(1);
    REQUIRE(followers1.empty());
    REQUIRE(following1.empty());

    std::vector<int> followers2 = sg.get_followers(2);
    std::vector<int> following2 = sg.get_following(2);
    REQUIRE(followers2.empty());
    REQUIRE(following2.empty());
}

TEST_CASE("Follow and unfollow operations", "[social_galaxy]") {
    SocialGalaxy sg;
    sg.add_user(1);
    sg.add_user(2);
    sg.add_user(3);

    sg.follow(1, 2);
    sg.follow(1, 3);

    std::vector<int> following1 = sg.get_following(1);
    std::vector<int> expected_following1 = {2, 3};
    std::sort(following1.begin(), following1.end());
    REQUIRE(following1 == expected_following1);

    std::vector<int> followers2 = sg.get_followers(2);
    std::vector<int> expected_followers2 = {1};
    REQUIRE(followers2 == expected_followers2);

    std::vector<int> followers3 = sg.get_followers(3);
    std::vector<int> expected_followers3 = {1};
    REQUIRE(followers3 == expected_followers3);

    // Unfollow operation
    sg.unfollow(1, 2);
    following1 = sg.get_following(1);
    expected_following1 = {3};
    REQUIRE(following1 == expected_following1);
    followers2 = sg.get_followers(2);
    REQUIRE(followers2.empty());

    // Unfollowing non-existent edge should be ignored
    sg.unfollow(1, 2);
    following1 = sg.get_following(1);
    REQUIRE(following1 == expected_following1);
}

TEST_CASE("Remove user and update relationships", "[social_galaxy]") {
    SocialGalaxy sg;
    // Add multiple users
    sg.add_user(1);
    sg.add_user(2);
    sg.add_user(3);
    sg.add_user(4);

    // Create follow relationships
    sg.follow(1, 2);
    sg.follow(1, 3);
    sg.follow(2, 3);
    sg.follow(3, 4);
    sg.follow(4, 1);

    // Remove user 3, which should update all edges related to user 3
    sg.remove_user(3);

    std::vector<int> following1 = sg.get_following(1);
    std::vector<int> expected_following1 = {2};
    REQUIRE(following1 == expected_following1);

    std::vector<int> following2 = sg.get_following(2);
    REQUIRE(following2.empty());

    std::vector<int> following4 = sg.get_following(4);
    std::vector<int> expected_following4 = {1};
    REQUIRE(following4 == expected_following4);

    std::vector<int> followers2 = sg.get_followers(2);
    std::vector<int> expected_followers2 = {1};
    REQUIRE(followers2 == expected_followers2);

    std::vector<int> followers1 = sg.get_followers(1);
    std::vector<int> expected_followers1 = {4};
    REQUIRE(followers1 == expected_followers1);
}

TEST_CASE("Mutual following retrieval", "[social_galaxy]") {
    SocialGalaxy sg;
    // Add users 1 through 5
    sg.add_user(1);
    sg.add_user(2);
    sg.add_user(3);
    sg.add_user(4);
    sg.add_user(5);

    // Setup following relationships
    // User 1 follows: 3, 4, 5
    sg.follow(1, 3);
    sg.follow(1, 4);
    sg.follow(1, 5);

    // User 2 follows: 3, 5
    sg.follow(2, 3);
    sg.follow(2, 5);

    std::vector<int> mutual = sg.get_mutual_followers(1, 2);
    std::vector<int> expected_mutual = {3, 5};
    REQUIRE(mutual == expected_mutual);
}

TEST_CASE("K-hop followers retrieval", "[social_galaxy]") {
    SocialGalaxy sg;
    // Create a chain network with users 1 to 7
    for (int i = 1; i <= 7; ++i) {
        sg.add_user(i);
    }
    
    // Setup edges:
    // 1 -> 2, 1 -> 3
    // 2 -> 4, 3 -> 4, 4 -> 5, 5 -> 6, 6 -> 7
    sg.follow(1, 2);
    sg.follow(1, 3);
    sg.follow(2, 4);
    sg.follow(3, 4);
    sg.follow(4, 5);
    sg.follow(5, 6);
    sg.follow(6, 7);

    // For get_k_hop_followers(user, k), we are looking for users that can reach the specified user.
    // Test on user 4:
    // Direct followers (1-hop): users 2 and 3.
    std::vector<int> k1 = sg.get_k_hop_followers(4, 1);
    std::vector<int> expected_k1 = {2, 3};
    REQUIRE(k1 == expected_k1);

    // 2-hop: user 1 can reach 4 through 2 or 3.
    std::vector<int> k2 = sg.get_k_hop_followers(4, 2);
    std::vector<int> expected_k2 = {1, 2, 3};
    REQUIRE(k2 == expected_k2);

    // Test on user 7:
    // 1-hop: direct follower is 6.
    std::vector<int> k1_user7 = sg.get_k_hop_followers(7, 1);
    std::vector<int> expected_k1_user7 = {6};
    REQUIRE(k1_user7 == expected_k1_user7);

    // 3-hop: 4 can reach 7 via 4->5->6->7 and 5 via 5->6->7.
    std::vector<int> k3_user7 = sg.get_k_hop_followers(7, 3);
    std::vector<int> expected_k3_user7 = {4, 5, 6};
    REQUIRE(k3_user7 == expected_k3_user7);

    // k = 0 should yield an empty result.
    std::vector<int> k0 = sg.get_k_hop_followers(7, 0);
    std::vector<int> expected_k0 = {};
    REQUIRE(k0 == expected_k0);
}

TEST_CASE("Edge cases with non-existent users", "[social_galaxy]") {
    SocialGalaxy sg;
    // No users added
    std::vector<int> followers = sg.get_followers(100);
    std::vector<int> following = sg.get_following(100);
    std::vector<int> mutual = sg.get_mutual_followers(100, 200);
    std::vector<int> k_hop = sg.get_k_hop_followers(100, 1);

    REQUIRE(followers.empty());
    REQUIRE(following.empty());
    REQUIRE(mutual.empty());
    REQUIRE(k_hop.empty());

    // Following, unfollowing, and removal operations on non-existent users should be ignored gracefully.
    sg.follow(100, 200);
    sg.unfollow(100, 200);
    sg.remove_user(100);
    
    // Verify again that no new users or relationships have been added.
    followers = sg.get_followers(200);
    following = sg.get_following(200);
    REQUIRE(followers.empty());
    REQUIRE(following.empty());
}