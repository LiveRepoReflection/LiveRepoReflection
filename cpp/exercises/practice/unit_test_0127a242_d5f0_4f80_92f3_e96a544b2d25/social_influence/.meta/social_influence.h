#ifndef SOCIAL_INFLUENCE_H_
#define SOCIAL_INFLUENCE_H_

#include <vector>
#include <utility>

namespace social_influence {

std::vector<int> find_top_influencers(int N, 
                                      const std::vector<std::pair<int, int>>& edges, 
                                      const std::vector<int>& activity_scores, 
                                      int K, 
                                      int max_steps);

}  // namespace social_influence

#endif  // SOCIAL_INFLUENCE_H_