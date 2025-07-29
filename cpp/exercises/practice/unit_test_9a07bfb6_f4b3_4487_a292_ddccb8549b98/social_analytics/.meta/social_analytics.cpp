#include "social_analytics.h"
#include <sstream>
#include <map>
#include <algorithm>
#include <vector>

using std::string;
using std::vector;
using std::map;
using std::pair;

vector<string> getTrendingTopics(const vector<Event>& events, long startTime, long endTime, int k) {
    map<string, double> wordScores;
    if (endTime <= startTime) return {};

    // Process events in the time window that have content
    for (const auto& event : events) {
        if (event.timestamp < startTime || event.timestamp > endTime) continue;
        if (event.content.empty()) continue;
        std::istringstream iss(event.content);
        string word;
        // Compute decay factor: linear scaling between 1 and 2
        double weight = 1.0 + (static_cast<double>(event.timestamp - startTime) / (endTime - startTime));
        while (iss >> word) {
            wordScores[word] += weight;
        }
    }

    // Move scores to vector of pairs
    vector<pair<string, double>> scoreVec(wordScores.begin(), wordScores.end());
    // Sort descending by score, if tie, lex order ascending
    std::sort(scoreVec.begin(), scoreVec.end(), [](const pair<string, double>& a, const pair<string, double>& b) {
        if (a.second == b.second) return a.first < b.first;
        return a.second > b.second;
    });

    vector<string> result;
    for (int i = 0; i < k && i < static_cast<int>(scoreVec.size()); ++i) {
        result.push_back(scoreVec[i].first);
    }
    return result;
}

vector<string> getInfluencerRanking(const vector<Event>& events, int k,
                                    double weight_post,
                                    double weight_comment,
                                    double weight_like,
                                    double weight_share,
                                    double weight_follower) {
    // Map each userId to its aggregated score.
    map<string, double> scoreMap;
    for (const auto& event : events) {
        if (event.eventType == EventType::POST) {
            scoreMap[event.userId] += weight_post;
        } else if (event.eventType == EventType::COMMENT) {
            if (!event.targetId.empty()) {
                scoreMap[event.targetId] += weight_comment;
            }
        } else if (event.eventType == EventType::LIKE) {
            if (!event.targetId.empty()) {
                scoreMap[event.targetId] += weight_like;
            }
        } else if (event.eventType == EventType::SHARE) {
            if (!event.targetId.empty()) {
                scoreMap[event.targetId] += weight_share;
            }
        } else if (event.eventType == EventType::FOLLOW) {
            if (!event.targetId.empty()) {
                scoreMap[event.targetId] += weight_follower;
            }
        }
    }
    // Move scores to vector for sorting
    vector<pair<string, double>> influencerScores(scoreMap.begin(), scoreMap.end());
    // Sort in descending order by score, if tie then lexicographic order ascending.
    std::sort(influencerScores.begin(), influencerScores.end(), [](const pair<string, double>& a, const pair<string, double>& b) {
        if (a.second == b.second) return a.first < b.first;
        return a.second > b.second;
    });
    vector<string> result;
    for (int i = 0; i < k && i < static_cast<int>(influencerScores.size()); ++i) {
        result.push_back(influencerScores[i].first);
    }
    return result;
}

vector<std::vector<Event>> detectAnomalies(const vector<Event>& events, long startTime, long endTime) {
    // Filter events in the time window.
    vector<Event> filtered;
    for (const auto& event : events) {
        if (event.timestamp >= startTime && event.timestamp <= endTime) {
            filtered.push_back(event);
        }
    }
    // Group events by a key: (eventType, content)
    map<pair<int, string>, vector<Event>> groups;
    for (const auto& event : filtered) {
        groups[{static_cast<int>(event.eventType), event.content}].push_back(event);
    }
    vector<vector<Event>> anomalies;
    const long timeThreshold = 20; // milliseconds

    for (auto& groupPair : groups) {
        auto& groupEvents = groupPair.second;
        if (groupEvents.size() < 3) continue;
        // Sort the events by timestamp for this group
        std::sort(groupEvents.begin(), groupEvents.end(), [](const Event& a, const Event& b) {
            return a.timestamp < b.timestamp;
        });
        long minTime = groupEvents.front().timestamp;
        long maxTime = groupEvents.back().timestamp;
        if ((maxTime - minTime) <= timeThreshold) {
            anomalies.push_back(groupEvents);
        }
    }
    return anomalies;
}