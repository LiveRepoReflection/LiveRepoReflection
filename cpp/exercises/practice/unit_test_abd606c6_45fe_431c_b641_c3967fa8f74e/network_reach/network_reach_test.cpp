#include "catch.hpp"
#include "network_reach.h"
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <string>
#include <utility>

TEST_CASE("Single user network") {
    std::vector<int> users = {1};
    std::vector<std::pair<int, int>> follows = {};
    std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>> userProfiles;
    
    std::unordered_set<std::string> interests = {"music"};
    userProfiles[1] = std::make_pair(interests, 0.5);
    
    std::unordered_set<std::string> postKeywords = {"music"};
    std::pair<int, std::unordered_set<std::string>> post = {1, postKeywords};
    
    REQUIRE(estimateReach(users, follows, userProfiles, post, 1) == 1);
}

TEST_CASE("Simple linear network") {
    std::vector<int> users = {1, 2, 3};
    std::vector<std::pair<int, int>> follows = {{1, 2}, {2, 3}};
    std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>> userProfiles;
    
    userProfiles[1] = std::make_pair(std::unordered_set<std::string>{"music"}, 1.0);
    userProfiles[2] = std::make_pair(std::unordered_set<std::string>{"music"}, 1.0);
    userProfiles[3] = std::make_pair(std::unordered_set<std::string>{"music"}, 1.0);
    
    std::pair<int, std::unordered_set<std::string>> post = {1, std::unordered_set<std::string>{"music"}};
    
    REQUIRE(estimateReach(users, follows, userProfiles, post, 2) == 3);
}

TEST_CASE("Cyclic network") {
    std::vector<int> users = {1, 2, 3};
    std::vector<std::pair<int, int>> follows = {{1, 2}, {2, 3}, {3, 1}};
    std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>> userProfiles;
    
    userProfiles[1] = std::make_pair(std::unordered_set<std::string>{"music", "movies"}, 0.8);
    userProfiles[2] = std::make_pair(std::unordered_set<std::string>{"movies", "sports"}, 0.6);
    userProfiles[3] = std::make_pair(std::unordered_set<std::string>{"sports", "news"}, 0.4);
    
    std::pair<int, std::unordered_set<std::string>> post = {1, std::unordered_set<std::string>{"music", "movies"}};
    
    int reach = estimateReach(users, follows, userProfiles, post, 3);
    REQUIRE(reach >= 1);
    REQUIRE(reach <= 3);
}

TEST_CASE("No interest alignment") {
    std::vector<int> users = {1, 2};
    std::vector<std::pair<int, int>> follows = {{1, 2}};
    std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>> userProfiles;
    
    userProfiles[1] = std::make_pair(std::unordered_set<std::string>{"music"}, 1.0);
    userProfiles[2] = std::make_pair(std::unordered_set<std::string>{"sports"}, 1.0);
    
    std::pair<int, std::unordered_set<std::string>> post = {1, std::unordered_set<std::string>{"news"}};
    
    REQUIRE(estimateReach(users, follows, userProfiles, post, 1) == 1);
}

TEST_CASE("Complex network with varying interest alignment") {
    std::vector<int> users = {1, 2, 3, 4, 5};
    std::vector<std::pair<int, int>> follows = {{1, 2}, {1, 3}, {2, 4}, {3, 4}, {4, 5}};
    std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>> userProfiles;
    
    userProfiles[1] = std::make_pair(std::unordered_set<std::string>{"tech", "music"}, 0.9);
    userProfiles[2] = std::make_pair(std::unordered_set<std::string>{"tech", "gaming"}, 0.7);
    userProfiles[3] = std::make_pair(std::unordered_set<std::string>{"music", "movies"}, 0.5);
    userProfiles[4] = std::make_pair(std::unordered_set<std::string>{"tech", "science"}, 0.8);
    userProfiles[5] = std::make_pair(std::unordered_set<std::string>{"gaming", "science"}, 0.6);
    
    std::pair<int, std::unordered_set<std::string>> post = {1, std::unordered_set<std::string>{"tech", "science"}};
    
    int reach = estimateReach(users, follows, userProfiles, post, 3);
    REQUIRE(reach >= 1);
    REQUIRE(reach <= 5);
}

TEST_CASE("Zero iterations") {
    std::vector<int> users = {1, 2};
    std::vector<std::pair<int, int>> follows = {{1, 2}};
    std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>> userProfiles;
    
    userProfiles[1] = std::make_pair(std::unordered_set<std::string>{"music"}, 1.0);
    userProfiles[2] = std::make_pair(std::unordered_set<std::string>{"music"}, 1.0);
    
    std::pair<int, std::unordered_set<std::string>> post = {1, std::unordered_set<std::string>{"music"}};
    
    REQUIRE(estimateReach(users, follows, userProfiles, post, 0) == 1);
}

TEST_CASE("Empty network") {
    std::vector<int> users = {};
    std::vector<std::pair<int, int>> follows = {};
    std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>> userProfiles;
    
    std::pair<int, std::unordered_set<std::string>> post = {1, std::unordered_set<std::string>{"music"}};
    
    REQUIRE(estimateReach(users, follows, userProfiles, post, 1) == 0);
}