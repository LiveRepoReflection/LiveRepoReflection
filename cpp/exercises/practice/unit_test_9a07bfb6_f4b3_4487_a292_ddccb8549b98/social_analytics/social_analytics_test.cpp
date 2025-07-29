#include "social_analytics.h"
#include <vector>
#include <string>
#include <chrono>
#include "catch.hpp"

using std::vector;
using std::string;

TEST_CASE("Trending Topics: Basic Functionality", "[trending]") {
    // Create events with posts containing content keywords.
    long now = std::chrono::system_clock::now().time_since_epoch().count();
    vector<Event> events = {
        {now - 10000, EventType::POST, "user1", "", "apple banana apple"},
        {now - 9000,  EventType::POST, "user2", "", "banana orange"},
        {now - 8000,  EventType::POST, "user3", "", "apple banana"},
        {now - 7000,  EventType::POST, "user4", "", "kiwi banana"},
        {now - 6000,  EventType::POST, "user1", "", "apple orange"}
    };
    // Query trending topics within time window covering these events, k = 2.
    long startTime = now - 11000;
    long endTime = now - 5000;
    int k = 2;

    vector<string> trending = getTrendingTopics(events, startTime, endTime, k);

    // Expect the top two trending topics to be "banana" and "apple"
    REQUIRE(trending.size() == 2);
    bool hasApple = (trending[0] == "apple" || trending[1] == "apple");
    bool hasBanana = (trending[0] == "banana" || trending[1] == "banana");
    REQUIRE(hasApple);
    REQUIRE(hasBanana);
}

TEST_CASE("Influencer Ranking: Basic Functionality", "[influencer]") {
    // Create events representing posts and engagements.
    long now = std::chrono::system_clock::now().time_since_epoch().count();
    vector<Event> events = {
        {now - 15000, EventType::POST, "user1", "", "content1"},
        {now - 14000, EventType::LIKE, "user2", "user1", ""},
        {now - 13000, EventType::COMMENT, "user3", "user1", "Nice post!"},
        {now - 12000, EventType::SHARE, "user4", "user1", ""},

        {now - 15000, EventType::POST, "user2", "", "content2"},
        {now - 14000, EventType::LIKE, "user1", "user2", ""},

        {now - 11000, EventType::POST, "user5", "", "content3"},
        {now - 10000, EventType::FOLLOW, "user6", "user5", ""},
        {now - 9000, EventType::LIKE, "user7", "user5", ""},
        {now - 8000, EventType::COMMENT, "user8", "user5", "Great!"}
    };
    // Set weighting factors for influencer ranking.
    int k = 2;
    double weight_post = 1.0;
    double weight_comment = 2.0;
    double weight_like = 0.5;
    double weight_share = 1.5;
    double weight_follower = 1.0;

    vector<string> influencerRanking = getInfluencerRanking(events, k,
                                                            weight_post,
                                                            weight_comment,
                                                            weight_like,
                                                            weight_share,
                                                            weight_follower);
    // Expect top influencers to include at least user1 and user5.
    REQUIRE(influencerRanking.size() == 2);
    bool hasUser1 = (influencerRanking[0] == "user1" || influencerRanking[1] == "user1");
    bool hasUser5 = (influencerRanking[0] == "user5" || influencerRanking[1] == "user5");
    REQUIRE(hasUser1);
    REQUIRE(hasUser5);
}

TEST_CASE("Anomaly Detection: Detect Synchronized Activity", "[anomaly]") {
    long now = std::chrono::system_clock::now().time_since_epoch().count();
    // Create events with synchronized behavior across multiple users (e.g., bots).
    vector<Event> events = {
        {now - 30000, EventType::COMMENT, "bot1", "", "spam content"},
        {now - 29995, EventType::COMMENT, "bot2", "", "spam content"},
        {now - 29990, EventType::COMMENT, "bot3", "", "spam content"},
        {now - 29985, EventType::COMMENT, "bot4", "", "spam content"},

        // Normal user behavior
        {now - 25000, EventType::POST, "user1", "", "legit content"},
        {now - 24000, EventType::LIKE, "user2", "user1", ""},
        {now - 23000, EventType::COMMENT, "user3", "user1", "nice post"}
    };

    long startTime = now - 31000;
    long endTime = now - 29000;

    vector<vector<Event>> anomalies = detectAnomalies(events, startTime, endTime);

    // Expect detection of an anomaly group for bot activity having at least three events.
    bool detected = false;
    for (const auto& group : anomalies) {
        if (group.size() >= 3) {
            bool allSpam = true;
            for (const auto& event : group) {
                if (event.eventType != EventType::COMMENT || event.content != "spam content") {
                    allSpam = false;
                    break;
                }
            }
            if (allSpam) {
                detected = true;
                break;
            }
        }
    }
    REQUIRE(detected);
}

TEST_CASE("Edge Cases: Empty Event Stream", "[edge]") {
    vector<Event> events;
    long now = std::chrono::system_clock::now().time_since_epoch().count();
    long startTime = now - 5000;
    long endTime = now;
    int k = 3;

    vector<string> trending = getTrendingTopics(events, startTime, endTime, k);
    REQUIRE(trending.empty());

    vector<string> influencers = getInfluencerRanking(events, k, 1.0, 1.0, 1.0, 1.0, 1.0);
    REQUIRE(influencers.empty());

    vector<vector<Event>> anomalies = detectAnomalies(events, startTime, endTime);
    REQUIRE(anomalies.empty());
}

TEST_CASE("Edge Cases: No Relevant Events in Time Window", "[edge]") {
    long now = std::chrono::system_clock::now().time_since_epoch().count();
    vector<Event> events = {
        {now - 100000, EventType::POST, "user1", "", "distant post"}
    };
    long startTime = now - 5000;
    long endTime = now;
    int k = 3;

    vector<string> trending = getTrendingTopics(events, startTime, endTime, k);
    REQUIRE(trending.empty());

    vector<vector<Event>> anomalies = detectAnomalies(events, startTime, endTime);
    REQUIRE(anomalies.empty());
}