#ifndef NETWORK_REACH_H
#define NETWORK_REACH_H

#include <vector>
#include <utility>
#include <unordered_map>
#include <unordered_set>
#include <string>

int estimateReach(const std::vector<int>& users,
                  const std::vector<std::pair<int, int>>& follows,
                  const std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>>& userProfiles,
                  const std::pair<int, std::unordered_set<std::string>>& post,
                  int iterations);

#endif // NETWORK_REACH_H