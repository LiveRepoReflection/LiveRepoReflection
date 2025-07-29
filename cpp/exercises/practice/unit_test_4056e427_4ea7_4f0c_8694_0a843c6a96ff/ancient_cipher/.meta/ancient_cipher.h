#ifndef ANCIENT_CIPHER_H
#define ANCIENT_CIPHER_H

#include <vector>
#include <tuple>
#include <utility>

namespace ancient_cipher {

std::pair<std::vector<int>, int> solve(int N, const std::vector<int>& V, const std::vector<std::tuple<int, int, int>>& roads, int start_city, int end_city, int K);

} // namespace ancient_cipher

#endif // ANCIENT_CIPHER_H