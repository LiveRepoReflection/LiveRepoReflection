#pragma once

#include <vector>
#include <string>

enum class EventType { POST, COMMENT, LIKE, SHARE, FOLLOW };

struct Event {
    long timestamp;
    EventType eventType;
    std::string userId;
    std::string targetId;
    std::string content;
};

std::vector<std::string> getTrendingTopics(const std::vector<Event>& events, long startTime, long endTime, int k);

std::vector<std::string> getInfluencerRanking(const std::vector<Event>& events, int k,
                                               double weight_post,
                                               double weight_comment,
                                               double weight_like,
                                               double weight_share,
                                               double weight_follower);

std::vector<std::vector<Event>> detectAnomalies(const std::vector<Event>& events, long startTime, long endTime);