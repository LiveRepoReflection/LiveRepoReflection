package network_reconstruct

func ReconstructNetwork(localViews [][]int) [][]bool {
	n := len(localViews)
	result := make([][]bool, n)
	for i := 0; i < n; i++ {
		result[i] = make([]bool, n)
	}
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			countI := countOccurrence(localViews[i], j)
			countJ := countOccurrence(localViews[j], i)
			if (countI > 0 && countJ > 0) || (countI+countJ >= 2) {
				result[i][j] = true
				result[j][i] = true
			}
		}
	}
	return result
}

func countOccurrence(slice []int, target int) int {
	count := 0
	for _, v := range slice {
		if v == target {
			count++
		}
	}
	return count
}