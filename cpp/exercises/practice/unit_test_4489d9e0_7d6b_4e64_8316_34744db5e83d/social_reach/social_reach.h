#ifndef SOCIAL_REACH_H
#define SOCIAL_REACH_H

#include <set>
#include <vector>
#include <string>
#include <functional>
#include <tuple>

/**
 * Calculate k-hop reachability from a starting user in a social network.
 *
 * @param startingUserID The ID of the user to start the reachability calculation from
 * @param k The maximum number of hops to consider
 * @param networkData A function that returns network data for a given user ID
 *                    The function returns a tuple containing:
 *                    - vector of follower IDs
 *                    - vector of followee IDs
 *                    - vector of content posted by the user
 * @return A set of user IDs that can be reached within k hops from startingUserID
 */
std::set<int> socialReachKHop(
    int startingUserID, 
    int k, 
    const std::function<std::tuple<std::vector<int>, std::vector<int>, std::vector<std::string>>(int)>& networkData
);

#endif // SOCIAL_REACH_H